"""Health-question safety filter.

PROBLEM THIS FILE SOLVES
Customers sometimes ask about allergies, sensitive skin, pregnancy, medication or
nail/skin problems. The bot must NOT give advice on these. Only Rosa may answer.

This is plain code, not the AI model, on purpose: the filter runs BEFORE the model
is called, so a clever message cannot talk the bot out of it, and we can test it
to be 100% reliable on the words listed below.

If any customer message in the recent conversation contains one of these words,
the answer is the fixed message at the bottom of this file and the model is never called.
"""

import re
import unicodedata

# Each entry is the START of a word. "allerg" catches allergy, allergic, allergie, allergisch.
HEALTH_WORD_STARTS_ENGLISH = [
    "allerg", "sensitiv", "irritat", "rash", "eczema", "psoria", "dermat",
    "itch", "swell", "swollen", "infect", "fung", "mold", "mould",
    "pregnan", "breastfe", "nursing", "medic", "prescri", "antibiot",
    "chemo", "radiotherap", "diabet", "blood thinner", "blood-thinner",
    "immune", "asthma", "bleed", "burn", "blister",
    "reaction", "react to", "hypoallergen", "hurt",
    "ingrown", "nail disease", "nail problem", "damaged nail", "brittle",
    "vitiligo", "cancer", "epilep", "hepatitis",
    "skin condition", "skin problem", "skin issue",
]

HEALTH_WORD_STARTS_DUTCH = [
    "allergi", "gevoelig", "overgevoelig", "huidaandoening", "huidprobleem",
    "huidziekte", "huid probleem", "uitslag", "eczeem", "psoria", "jeuk",
    "zwelling", "gezwollen", "ontsteking", "ontstok", "infectie", "schimmel",
    "zwanger", "borstvoeding", "medicij", "medicatie", "medicament",
    "antibiotica", "chemo", "bestraling", "diabet", "suikerziekte",
    "bloedverdunner", "afweer", "astma", "bloed", "blaar",
    "blaren", "reactie", "reageer", "pijn", "ingegroeid",
    "nagelziekte", "nagelprobleem", "beschadigde nagel", "broze nagel",
    "kanker", "epilep", "hepatitis", "wratten",
]

# Short words that would match harmless words if we only checked the start
# ("wond" would match "wonderful", "pain" would match "paint"), so they must match as a whole word.
HEALTH_WHOLE_WORDS = [
    "pain", "painful", "sore", "wound", "wounds", "wond", "wonden", "wondje",
    "hiv", "wart", "warts", "wrat", "pus", "brandwond", "brandwonden",
]

ALL_HEALTH_WORD_STARTS = HEALTH_WORD_STARTS_ENGLISH + HEALTH_WORD_STARTS_DUTCH


def normalise_text(text: str) -> str:
    """Lower-case, remove accents (ë -> e), and turn punctuation into spaces."""
    lowered = text.lower()
    decomposed = unicodedata.normalize("NFKD", lowered)
    without_accents = "".join(
        character for character in decomposed if not unicodedata.combining(character)
    )
    return re.sub(r"[^a-z0-9]+", " ", without_accents)


def build_health_pattern() -> re.Pattern:
    """One regular expression: a health word-start, or a health whole word."""
    escaped_starts = [re.escape(normalise_text(start).strip()) for start in ALL_HEALTH_WORD_STARTS]
    escaped_whole_words = [re.escape(word) for word in HEALTH_WHOLE_WORDS]

    start_part = r"\b(?:" + "|".join(escaped_starts) + r")"
    whole_word_part = r"\b(?:" + "|".join(escaped_whole_words) + r")\b"
    return re.compile(start_part + "|" + whole_word_part)


HEALTH_PATTERN = build_health_pattern()


def mentions_health_topic(customer_message: str) -> bool:
    """True if the customer's message touches allergy, skin, pregnancy, medication or similar."""
    normalised_message = normalise_text(customer_message)
    return HEALTH_PATTERN.search(normalised_message) is not None


def any_message_mentions_health_topic(customer_messages: list[str]) -> bool:
    """Check every customer message in the recent conversation, not only the last one.

    Why: if someone says "I am pregnant" and next asks "so can I get gel?", the second
    message looks harmless by itself but the answer is still Rosa's to give.
    """
    for customer_message in customer_messages:
        if mentions_health_topic(customer_message):
            return True
    return False


# One message in both languages, so we never have to guess which language the customer speaks.
HEALTH_FIXED_REPLY = (
    "I can't give advice on allergies, skin, pregnancy, medication or nail health. "
    "Please message Rosa on WhatsApp so she can answer you personally.\n\n"
    "Hier kan ik geen advies over geven (allergie, huid, zwangerschap, medicijnen of nagelgezondheid). "
    "Stuur Rosa een WhatsApp-bericht, dan antwoordt zij je persoonlijk."
)
