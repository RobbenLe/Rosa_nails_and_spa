"""Load the salon's starting services into an empty database. Safe to re-run.

This is only the starting data — after that, prices and services are
managed on the website's /admin page. It runs on every backend start, so it
only adds data when there is none: services the admin deletes stay deleted.
"""

from database import SessionLocal, create_tables
from models import Service, Technician

TECHNICIANS = [
    ("Rosa", 1),
    ("Technicians-2", 2),
    ("Technicians-3", 3),
]

# (category, name, variant, duration_minutes, price_cents, is_bookable)
# Rows with the same name are one service with several options on the website.
SERVICES = [
    ("Manicure & Pedicure", "Classic Manicure", "", 40, 2000, True),
    ("Manicure & Pedicure", "Gel Manicure", "", 60, 2500, True),
    ("Manicure & Pedicure", "Classic Pedicure", "", 40, 4000, True),
    ("Manicure & Pedicure", "Gel Pedicure", "", 60, 5500, True),

    ("Acrylic & Extensions", "Natural", "new set", 90, 5000, True),
    ("Acrylic & Extensions", "Natural", "filling", 60, 4000, True),
    ("Acrylic & Extensions", "Natural with gel polish", "new set", 105, 6000, True),
    ("Acrylic & Extensions", "Natural with gel polish", "filling", 75, 5000, True),
    ("Acrylic & Extensions", "Nude", "new set", 90, 5000, True),
    ("Acrylic & Extensions", "Nude", "filling", 60, 4000, True),
    ("Acrylic & Extensions", "Color powder", "new set", 90, 5500, True),
    ("Acrylic & Extensions", "Color powder", "filling", 60, 4500, True),
    ("Acrylic & Extensions", "Baby boom", "new set", 105, 6500, True),
    ("Acrylic & Extensions", "Baby boom", "filling", 75, 5000, True),
    ("Acrylic & Extensions", "Pink & White", "new set", 105, 6500, True),
    ("Acrylic & Extensions", "Pink & White", "filling", 75, 5500, True),

    ("BIAB & Gel", "BIAB (Builder Gel)", "Biab Colour", 75, 5000, True),
    ("BIAB & Gel", "BIAB (Builder Gel)", "Biab Combination Gellak", 75, 5500, True),
    ("BIAB & Gel", "Gel Polish Removal", "", 20, 1000, True),

    # Add-ons: priced on the website, not bookable on their own.
    ("Extras", "Nail Art", "from", 10, 500, False),
    ("Extras", "Nail Repair", "from", 15, 500, False),
    ("Extras", "Acrylic & Gel Removal", "removal only", 20, 1500, False),
    ("Extras", "Acrylic & Gel Removal", "with new set", 20, 1000, False),
]

# name -> (description, suitable)
DESCRIPTIONS = {
    "Classic Manicure": (
        "Shaping, cuticle care and buff.",
        "Perfect for clients who want healthy, well-groomed nails with a natural, elegant finish.",
    ),
    "Gel Manicure": (
        "Gel colour applied to natural nails, cured for a hard, glossy finish.",
        "Perfect for clients who want a quick colour refresh with no extra length or structure.",
    ),
    "Classic Pedicure": (
        "Soak, exfoliation, nail and cuticle care, finished with polish.",
        "Perfect for clients on their feet all day, or getting ready for soft feet.",
    ),
    "Gel Pedicure": (
        "Full pedicure finished with gel colour for a lasting result.",
        "Perfect for holidays and events, when you need colour that lasts the whole trip.",
    ),
    "Natural": (
        "A clear acrylic overlay or extension, shaped and buffed to a natural finish.",
        "Perfect for clients who want strength and length that still looks like their own nails.",
    ),
    "Natural with gel polish": (
        "A natural acrylic set finished with gel colour of your choice.",
        "Perfect for clients who want the durability of acrylic with colour that lasts just as long.",
    ),
    "Nude": (
        "A full set built in soft nude-toned acrylic, needing no polish on top.",
        "Perfect for clients who want a clean, understated look that suits any occasion.",
    ),
    "Color powder": (
        "A full set built in coloured acrylic powder, so the colour runs through the nail itself.",
        "Perfect for clients who want bold colour that never chips or grows out unevenly.",
    ),
    "Baby boom": (
        "A blended pink-to-white gradient built into the acrylic, with no hard line.",
        "Perfect for clients who want a softer, more modern take on the classic French.",
    ),
    "Pink & White": (
        "The classic French: a pink nail bed with a crisp white tip, sculpted by hand.",
        "Perfect for clients who want a timeless, polished look that never dates.",
    ),
    "BIAB (Builder Gel)": (
        "A premium strengthening gel that protects the natural nail, promotes healthy growth, and leaves a smooth, durable finish.",
        "Perfect for clients who want beautiful, long-wear nails without added thickness.",
    ),
    "Gel Polish Removal": (
        "Gentle soak-off of existing gel polish, with the natural nail cleaned and buffed.",
        "Perfect for clients giving their nails a break, or coming in from another salon.",
    ),
    "Nail Art": (
        "Hand-painted detail, chrome, or stones. Priced per nail.",
        "Perfect for clients who want something personal, from a single accent nail to a full set.",
    ),
    "Nail Repair": (
        "Repair of a single broken or lifted nail, reshaped to match the rest.",
        "Perfect when one nail goes wrong and you would rather not redo the whole set.",
    ),
    "Acrylic & Gel Removal": (
        "Safe soak-off of existing acrylic, gel or BIAB, leaving the natural nail clean and undamaged.",
        "Perfect for clients returning to natural nails, or starting fresh with a different style.",
    ),
}

def seed():
    db = SessionLocal()
    try:
        if db.query(Technician).first() is None:
            for name, order in TECHNICIANS:
                db.add(Technician(name=name, display_order=order, is_active=True))

        if db.query(Service).first() is None:
            for category, name, variant, duration_minutes, price, is_bookable in SERVICES:
                description, suitable = DESCRIPTIONS.get(name, ("", ""))
                db.add(Service(category=category, name=name, variant=variant, description=description, suitable=suitable,
                               duration_minutes=duration_minutes, price=price, is_bookable=is_bookable, is_active=True))

        db.commit()
        print(f"Seeded. Total services {db.query(Service).count()}")
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    seed()
