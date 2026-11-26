"""Safety filters that run BEFORE the AI model is called.

PROBLEM THIS FILE SOLVES
Some customer messages are not for the bot to answer, only for Rosa:
  1. health: allergies, sensitive skin, pregnancy, medication, nail/skin problems
  2. personal requests: for example "I only want a woman to do my nails"
  3. personal details: origin, nationality, religion and similar

This is plain code, not the AI model, on purpose: a clever message cannot talk plain
code out of it, and we can test it to be 100% reliable on the words listed below.
When a filter matches, the caller shows the fixed "Rosa can help you personally" answer
and the model is never called. The bot never repeats or comments on such details.

HONEST LIMIT: these are word lists. Unusual wording that is not on the list passes this
filter; the instructions given to the model are the second layer, and a code check on the
model's reply is the third.
"""

import re
import unicodedata

from chatbot.names import remove_stated_names

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


# ----------------------------------------------------------------------------------------
# Personal details (origin, nationality, religion and similar). Whole words, after normalise_text().
PERSONAL_IDENTITY_WORDS = [
    # religion
    "muslim", "muslims", "moslim", "moslims", "islam", "islamic", "islamitisch", "christian", "christelijk",
    "jewish", "joods", "hindu", "hindoe", "buddhist", "boeddhist", "catholic", "katholiek", "atheist",
    "sikh", "halal", "hijab", "headscarf", "hoofddoek", "niqab", "religion", "religious", "religie",
    "religieus", "geloof", "gelovig",
    # origin and nationality
    "moroccan", "marokkaan", "marokkaans", "marokkaanse", "morocco", "marokko", "turkish", "turks", "turkse",
    "turkey", "turkije", "surinamese", "surinaams", "surinaamse", "ukrainian", "oekraiens", "syrian",
    "syrisch", "eritrean", "afghan", "iranian", "iraqi", "indian", "pakistani", "chinese", "vietnamese",
    "indonesian", "indonesisch", "african", "nationality", "nationaliteit", "origin", "afkomst",
    "ethnicity", "immigrant", "refugee", "vluchteling", "asylum", "asiel",
    # other personal characteristics
    "gay", "lesbian", "transgender", "disabled", "gehandicapt", "handicap", "wheelchair", "rolstoel",
]

# A request about WHO does the nails: all three kinds of word must be in the same message.
GENDER_WORDS = [
    "man", "men", "male", "woman", "women", "female", "lady", "ladies", "girl", "girls", "guy", "guys",
    "boy", "vrouw", "vrouwen", "vrouwelijk", "vrouwelijke", "dame", "dames", "meisje", "meisjes",
    "mannelijk", "mannelijke", "mannen", "jongen",
]
PREFERENCE_WORDS = [
    "only", "prefer", "rather", "want", "wants", "wish", "must", "need", "require", "insist",
    "liever", "alleen", "wil", "wilt", "wens", "moet", "graag", "voorkeur", "uitsluitend",
]
WHO_DOES_IT_WORDS = [
    "do", "does", "doing", "done", "doe", "doet", "doen", "technician", "technicians", "therapist",
    "specialist", "stylist", "medewerker", "medewerkster", "behandelaar", "nagelstylist", "iemand",
    "someone", "person", "persoon", "staff", "employee", "handle", "treat", "behandelen", "behandeld",
    "work", "werkt", "werken", "help", "helpen",
]


def build_whole_word_pattern(words: list[str]) -> re.Pattern:
    escaped_words = [re.escape(word) for word in words]
    return re.compile(r"\b(?:" + "|".join(escaped_words) + r")\b")


PERSONAL_IDENTITY_PATTERN = build_whole_word_pattern(PERSONAL_IDENTITY_WORDS)
GENDER_PATTERN = build_whole_word_pattern(GENDER_WORDS)
PREFERENCE_PATTERN = build_whole_word_pattern(PREFERENCE_WORDS)
WHO_DOES_IT_PATTERN = build_whole_word_pattern(WHO_DOES_IT_WORDS)


def mentions_personal_identity(text: str, allowed_names: tuple[str, ...] = ()) -> bool:
    """True if the text mentions origin, nationality, religion or a similar personal detail.

    A name the customer stated about themselves is NOT a personal detail, even when it looks like
    one ('my name is Christian'), so stated names are removed first. allowed_names covers a reply
    that greets the customer by that name.
    """
    text_without_name = remove_stated_names(text)
    for allowed_name in allowed_names:
        text_without_name = re.sub(r"\b" + re.escape(allowed_name) + r"\b", " ", text_without_name, flags=re.IGNORECASE)
    return PERSONAL_IDENTITY_PATTERN.search(normalise_text(text_without_name)) is not None


def asks_for_technician_by_gender(customer_message: str) -> bool:
    """True for requests like 'I only want a woman to do it' or 'ik wil alleen een vrouw die het doet'."""
    normalised_message = normalise_text(remove_stated_names(customer_message))
    return (
        GENDER_PATTERN.search(normalised_message) is not None
        and PREFERENCE_PATTERN.search(normalised_message) is not None
        and WHO_DOES_IT_PATTERN.search(normalised_message) is not None
    )


def is_personal_request(customer_message: str) -> bool:
    """A personal request or personal detail: only Rosa answers these."""
    return mentions_personal_identity(customer_message) or asks_for_technician_by_gender(customer_message)
