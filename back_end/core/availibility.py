from datetime import data as data_type, datetime, time, timedelta, timezone

from sqlachemy import or_
from sqlalchemy.orm import Session

import config
from models import Appointment, ClosedSlot, Technician, Service


######################################## HELPERS FUNCTION
def as_utc(value: datetime) -> datetime:
    """SQLite forgets timezones. Treat a naive value as UTC."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.replace(tzinfo=timezone.utc)





# ------------------------------------------------------- small lookups
def find_bookable_technician(db: Session, technician_id: int):
    """The technician, but only if they still work here."""
    technician = db.query(Technician).filter(Technician.id == technician_id).first()

    if technician is None or not technician.is_active:
        return None

    return technician

def get_active_technician(db: Session) -> list[Technician]:
    """All technicians, in the order the admin wants them shown."""
    return (db.query(Technician)
            .filter(Technician.is_active == (True))
            .order_by(Technician.display_name, Technician.id)
            .all()
            )

def get_opening_hours(day: data_type):
    """(opens_at, closes_at) in UTC, or None if the salon is shut that day."""
    hours = config.BUSINESS_HOURS.get(day.weekday())
    if hours is None:
        return None
    opens_at = local_time_to_utc(day, hours[0])
    closes_at = local_time_to_utc(day, hours[1])
    return opens_at, closes_at

def earliest_bookable_time() -> datetime:
    """Customers must book at least a couple of hours ahead."""
    earliest_booking_time = datetime.now(timezone.utc) + timedelta(hours=config.MIN_BOOKING_NOTICE_HOURS)
    return earliest_booking_time


# --------------------------------------------------- what blocks a slot
def get_busy_ranges(db: Session, technician_id: int, opens_at: datetime, closes_at: datetime) -> list[tuple[datetime, datetime]]:
    """
        Every (start, end) range this technician is unavailable on this day.

        Two sources, treated the same way:
          - their own appointments
          - closed slots, either for them or for the whole salon
        """


