#PRICE LIST: public read endpoint + password-protected admin endpoints

import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

import config
from database import get_db
from models import Appointment, Service

router = APIRouter()


# ------------------------------------------------------- shapes
class ServiceIn(BaseModel):
    """What the admin form sends when adding or editing a service."""
    name: str = Field(min_length=1, max_length=120)
    variant: str = Field(default="", max_length=60)
    category: str
    description: str = ""
    suitable: str = ""
    duration_minutes: int = Field(gt=0, le=600)
    price_cents: int = Field(ge=0, le=100_000)
    is_active: bool = True
    is_bookable: bool = True

    @field_validator("name", "variant", "description", "suitable")
    @classmethod
    def strip(cls, value: str) -> str:
        return value.strip()

    @field_validator("category")
    @classmethod
    def known_category(cls, value: str) -> str:
        if value not in config.SERVICE_CATEGORIES:
            raise ValueError(f"category must be one of {list(config.SERVICE_CATEGORIES)}")
        return value


def to_json(service: Service) -> dict:
    return {
        "id": service.id,
        "name": service.name,
        "variant": service.variant or "",
        "category": service.category,
        "description": service.description or "",
        "suitable": service.suitable or "",
        "duration_minutes": service.duration_minutes,
        "price_cents": service.price,
        "is_active": service.is_active,
        "is_bookable": service.is_bookable,
    }


def ordered(query):
    """Category order first, then the order services were added in."""
    services = query.order_by(Service.id).all()
    rank = {category: index for index, category in enumerate(config.SERVICE_CATEGORIES)}
    return sorted(services, key=lambda service: rank.get(service.category, len(rank)))


# ------------------------------------------------------- admin check
def require_admin(authorization: str = Header(default="")):
    """The admin page sends `Authorization: Bearer <ADMIN_PASSWORD>`."""
    password = os.getenv("ADMIN_PASSWORD")
    if not password:
        raise HTTPException(status_code=503, detail="Admin is disabled: ADMIN_PASSWORD is not set")

    supplied = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(supplied.encode(), password.encode()):
        raise HTTPException(status_code=401, detail="Wrong password")


# ------------------------------------------------------- public
@router.get("/api/services")
def list_services(db: Session = Depends(get_db)):
    """Everything shown on the website's price list."""
    return [to_json(service) for service in ordered(db.query(Service).filter(Service.is_active == True))]


# ------------------------------------------------------- admin
@router.get("/api/admin/services", dependencies=[Depends(require_admin)])
def admin_list_services(db: Session = Depends(get_db)):
    """Every service, including hidden ones."""
    return {
        "categories": list(config.SERVICE_CATEGORIES),
        "services": [to_json(service) for service in ordered(db.query(Service))],
    }


@router.post("/api/admin/services", status_code=201, dependencies=[Depends(require_admin)])
def create_service(body: ServiceIn, db: Session = Depends(get_db)):
    service = Service()
    apply(service, body)
    db.add(service)
    db.commit()
    db.refresh(service)
    return to_json(service)


@router.put("/api/admin/services/{service_id}", dependencies=[Depends(require_admin)])
def update_service(service_id: int, body: ServiceIn, db: Session = Depends(get_db)):
    service = get_or_404(db, service_id)
    apply(service, body)
    db.commit()
    db.refresh(service)
    return to_json(service)


@router.delete("/api/admin/services/{service_id}", dependencies=[Depends(require_admin)])
def delete_service(service_id: int, db: Session = Depends(get_db)):
    """
    Delete a service. If it was ever booked, the appointments still point at it,
    so it is hidden from the website instead of removed.
    """
    service = get_or_404(db, service_id)

    if db.query(Appointment).filter(Appointment.service_id == service.id).first():
        service.is_active = False
        db.commit()
        return {"deleted": False, "hidden": True}

    db.delete(service)
    db.commit()
    return Response(status_code=204)


# ------------------------------------------------------- helpers
def get_or_404(db: Session, service_id: int) -> Service:
    service = db.query(Service).filter(Service.id == service_id).first()
    if service is None:
        raise HTTPException(status_code=404, detail="Service not found")
    return service


def apply(service: Service, body: ServiceIn):
    service.name = body.name
    service.variant = body.variant
    service.category = body.category
    service.description = body.description
    service.suitable = body.suitable
    service.duration_minutes = body.duration_minutes
    service.price = body.price_cents
    service.is_active = body.is_active
    service.is_bookable = body.is_bookable
