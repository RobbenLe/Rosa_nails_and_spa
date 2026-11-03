"""Load the salon's services into the database. Safe to re-run."""

from database import Base, SessionLocal, engine
from models import Service, Technician

Base.metadata.create_all(bind=engine)

TECHNICIANS = [
    ("Rosa", 1),
    ("Technicians-2", 2),
    ("Technicians-3", 3),\
]

# (category, name, duration_minutes, price_cents, is_bookable)
SERVICES = [
("Manicure & Pedicure", "Classic Manicure", 40, 2000, True),
    ("Manicure & Pedicure", "Gel Manicure", 60, 2500, True),
    ("Manicure & Pedicure", "Classic Pedicure", 40, 4000, True),
    ("Manicure & Pedicure", "Gel Pedicure", 60, 5500, True),

    ("Acrylic & Extensions", "Natural - new set", 90, 5000, True),
    ("Acrylic & Extensions", "Natural - filling", 60, 4000, True),
    ("Acrylic & Extensions", "Natural with gel polish - new set", 105, 6000, True),
    ("Acrylic & Extensions", "Natural with gel polish - filling", 75, 5000, True),
    ("Acrylic & Extensions", "Nude - new set", 90, 5000, True),
    ("Acrylic & Extensions", "Nude - filling", 60, 4000, True),
    ("Acrylic & Extensions", "Color powder - new set", 90, 5500, True),
    ("Acrylic & Extensions", "Color powder - filling", 60, 4500, True),
    ("Acrylic & Extensions", "Baby boom - new set", 105, 6500, True),
    ("Acrylic & Extensions", "Baby boom - filling", 75, 5000, True),
    ("Acrylic & Extensions", "Pink & White - new set", 105, 6500, True),
    ("Acrylic & Extensions", "Pink & White - filling", 75, 5500, True),

    ("BIAB & Gel", "BIAB (Builder Gel)", 75, 6000, True),
    ("BIAB & Gel", "BIAB Infill", 60, 4000, True),
    ("BIAB & Gel", "Gel Polish", 45, 2500, True),
    ("BIAB & Gel", "Gel Polish Removal", 20, 1000, True),

    # Add-ons: priced on the website, not bookable on their own.
    ("Extras", "Nail Art", 10, 500, False),
    ("Extras", "Nail Repair", 15, 500, False),
    ("Extras", "Removal", 20, 1500, False),
]

def seed():
    db = SessionLocal()
    try:
        for name, order in TECHNICIANS:
            if db.query(Technician).filter(Technician.name == name).first():
                continue
            db.add(Technician(name=name, display_order=order, is_active=True))

        for category, name, duration_minutes, price, is_bookable in SERVICES:
            if db.query(Service).filter(Service.name == name).first():
                continue
            db.add(Service(category=category, name=name, duration_minutes=duration_minutes, price=price, is_bookable=is_bookable,
                           is_active=True))

        db.commit()
        print(f"Seeded. Total services {db.query(Service).count()}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()



