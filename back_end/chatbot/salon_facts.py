"""Fixed facts about the salon that the chatbot may state: name, address, phone, hours, and the FAQ.

PROBLEM THIS FILE SOLVES
The bot must never invent facts. Everything it says about the salon comes from
this file (or from the live price list). Prices are NOT here: they come from the database.

These facts also exist on the website in front_end/src/data/salon.ts.
tests/test_salon_facts.py compares the two, so they cannot drift apart unnoticed.
If Rosa changes her hours or phone number, change BOTH places.
"""

import config

SALON_NAME = "Rosa Nails & Spa"
SALON_ADDRESS = "Hofwickstraat 2"
SALON_CITY = "1055 GE Amsterdam"
SALON_PHONE_DISPLAY = "+31 6 33 42 67 98"

WEEKDAY_NAMES_ENGLISH = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
WEEKDAY_NAMES_DUTCH = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]


def describe_opening_hours(weekday_names: list[str], closed_word: str) -> str:
    """One line per weekday, e.g. 'Monday: 10:00-18:00'. Built from config.BUSINESS_HOURS."""
    lines = []
    for weekday_number, weekday_name in enumerate(weekday_names):
        hours = config.BUSINESS_HOURS.get(weekday_number)
        if hours is None:
            lines.append(f"{weekday_name}: {closed_word}")
        else:
            lines.append(f"{weekday_name}: {hours[0]}-{hours[1]}")
    return "\n".join(lines)


# The approved FAQ (docs/faq-draft.md). Each entry: (english question, english answer, dutch answer).
FREQUENTLY_ASKED_QUESTIONS = [
    (
        "Where are you?",
        f"{SALON_NAME}, {SALON_ADDRESS}, {SALON_CITY} (Amsterdam West).",
        f"{SALON_NAME}, {SALON_ADDRESS}, {SALON_CITY} (Amsterdam West).",
    ),
    (
        "What are your opening hours?",
        "Monday to Saturday 10:00-18:00, closed on Sunday.",
        "Maandag t/m zaterdag 10:00-18:00, zondag gesloten.",
    ),
    (
        "How do I book?",
        f"Send us a message on WhatsApp ({SALON_PHONE_DISPLAY}) or call. Rosa confirms your appointment personally.",
        f"Stuur ons een bericht via WhatsApp ({SALON_PHONE_DISPLAY}) of bel. Rosa bevestigt je afspraak zelf.",
    ),
    (
        "Do you take walk-ins?",
        "Appointments are preferred. Message us on WhatsApp to see if there is space.",
        "Een afspraak heeft de voorkeur. Stuur ons een WhatsApp-bericht om te kijken of er plek is.",
    ),
    (
        "How early must I book?",
        "Please book at least 2 hours ahead.",
        "Boek graag minstens 2 uur van tevoren.",
    ),
    (
        "Can I cancel or change my appointment?",
        "Please cancel at least 12 hours before. Message us on WhatsApp.",
        "Annuleer graag minstens 12 uur van tevoren, via WhatsApp.",
    ),
    (
        "How can I pay?",
        "You can pay with cash or PIN (debit card). We prefer cash.",
        "Je kunt contant of met PIN betalen. Wij hebben een voorkeur voor contant.",
    ),
    (
        "Who will do my nails?",
        "Rosa and her team. Rosa has 10 years of experience.",
        "Rosa en haar team. Rosa heeft 10 jaar ervaring.",
    ),
    (
        "Do you do nail art?",
        "Yes, nail art is one of our services. Ask on WhatsApp about your design idea.",
        "Ja, nail art hoort bij onze diensten. Vraag via WhatsApp naar jouw ontwerp.",
    ),
]


def format_faq_for_prompt() -> str:
    """The FAQ as plain text that is pasted into the model's instructions."""
    blocks = []
    for question, english_answer, dutch_answer in FREQUENTLY_ASKED_QUESTIONS:
        blocks.append(f"Q: {question}\nEnglish answer: {english_answer}\nDutch answer: {dutch_answer}")
    return "\n\n".join(blocks)
