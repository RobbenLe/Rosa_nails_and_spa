#CREATING THE TABLE IN DATABASE

from datetime import datetime
from sqlalchemy import(
  Boolean, Column, DateTime, ForeignKey, Index, Integer, String, Text, text,
)
from sqlalchemy.orm import relationship
from database import Base

def utcnow():
    return datetime.utcnow();

class Service(Base):
    __tablename__ = 'services'

    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    category = Column(String(60), nullable=False, default='')
    description = Column(Text, default='')
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_bookable = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable = False, default=utcnow)
    updated_at = Column(DateTime, nullable = False, default=utcnow)
    appointments= relationship("Appointment", back_populates="service")

class Appointment(Base):
    __tablename__ = 'appointments'

    id = Column(Integer, primary_key=True)
    customer_name = Column(String(120), nullable=False)
    customer_email = Column(String(60), nullable=False )
    customer_phone = Column(String(40), nullable = False)
    service_id = Column(Integer, ForeignKey('services.id'), nullable=False)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    status = Column(String(30), nullable=False, default='confirmed')
    source = Column(String(10), nullable=False, default='Web')
    cancellation_token = Column(String(40), unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    service = relationship("Service", back_populates="appointments")
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=False)
    technician = relationship("Technician", back_populates="appointments")

    __table_args__ = (
        Index(
            "uq_active_appointment_slot",
            "technician_id",
            "start_time",
            unique=True,
            sqlite_where=text("status IN ('confirmed', 'rescheduled')"),
            postgresql_where=text("status IN ('confirmed', 'rescheduled')"),
        ),
    )

class ClosedSlot(Base):
    __tablename__ = 'closed_slots'

    id = Column(Integer, primary_key=True)
    start_time = Column(DateTime(timezone=True), nullable=False, index=True)
    end_time = Column(DateTime(timezone=True), nullable=False)
    reason = Column(String(40), default='')
    created_by = Column(String(50), default="admin")
    created_at = Column(DateTime(timezone=True), default=utcnow)
    technician_id = Column(Integer, ForeignKey("technicians.id"), nullable=True)


class Technician(Base):
    __tablename__ = 'technicians'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    display_order = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=utcnow)
    updated_at = Column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)
    appointments = relationship("Appointment", back_populates="technician")
