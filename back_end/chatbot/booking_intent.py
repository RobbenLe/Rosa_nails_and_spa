"""Recognises appointment requests and reads what the customer already told us.

PROBLEM THIS FILE SOLVES
Appointment requests used to depend on the AI model, which sometimes answered in a broken
format or decided the question was "out of scope". Now plain code recognises the intent
(English and Dutch) and the bot answers at once with the fixed appointment sentence and the
"Book via WhatsApp" button. Nothing is asked back.

The same code reads, from the customer's own words, the service, the date/time and the name,
so the prepared WhatsApp message contains what they said. Anything we cannot read is left out.

The bot never says whether Rosa has time: it does not know her schedule.
"""

import re

from chatbot.fixed_replies import BOOKING_REPLIES
from chatbot.names import find_stated_names
from chatbot.price_list import PriceListEntry
from chatbot.safety import normalise_text

# ------------------------------------------------------------------ is this an appointment request?
# Words and phrases that show the customer wants an appointment or asks about free time.
# They are matched on normalise_text() output (lower case, no accents, punctuation as spaces).
BOOKING_INTENT_PHRASES = [
    # English
    r"appointments?", r"book", r"booking", r"booked", r"reserve", r"reservation", r"availability", r"available",
    r"are you free", r"is rosa free", r"is she free", r"any(?:thing)? free",
    r"free (?:on|at|today|tomorrow|this|next|for)",
    r"do you have (?:any )?(?:time|space|room|openings?|slots?|spots?|places?|availability)",
    r"have (?:any )?(?:time|space|room|openings?|slots?|spots?)", r"any (?:time|space|openings?|slots?|spots?)",
    r"time slots?", r"come by", r"stop by", r"drop by", r"can i come", r"can we come",
    # Dutch
    r"afspraak", r"afspraken", r"boeken", r"boek", r"reserveren", r"reservering", r"beschikbaar",
    r"beschikbaarheid", r"plek", r"plekje", r"plaatsje",
    r"hebben jullie (?:nog )?(?:tijd|plek|plaats|ruimte|plekje)", r"heb je (?:nog )?(?:tijd|plek|plaats|ruimte)",
    r"is er (?:nog )?(?:plek|plaats|ruimte|tijd)", r"zijn jullie vrij", r"is rosa vrij", r"is ze vrij",
    r"vrij (?:op|om|vandaag|morgen|deze|volgende)", r"kan ik langskomen", r"kunnen we langskomen",
    r"kan ik komen", r"kunnen we komen", r"langskomen",
]

# If one of these is in the message, it is about an existing appointment or the rules, not a new request:
# the approved FAQ answers those (cancel/change, how early to book).
NOT_A_NEW_REQUEST_PHRASES = [
    r"cancel", r"cancellation", r"reschedule", r"change", r"move", r"annuleer", r"annuleren", r"annulering",
    r"verzet", r"verzetten", r"wijzig", r"wijzigen",
    r"how early", r"how far", r"in advance", r"ahead", r"minimum notice", r"hoe vroeg", r"van tevoren",
    r"vooraf", r"hoeveel tijd",
]

# A customer who gives a day or time AND says what they would like (or names a service) wants an appointment,
# even without the word "appointment": "I'd like BIAB colour on Saturday at 10am".
WISH_PHRASES = [
    r"i d like", r"i would like", r"i want", r"i wanna", r"looking for", r"can i", r"could i", r"may i",
    r"ik wil", r"ik zou graag", r"graag", r"kan ik", r"mag ik", r"kunnen we", r"ik zoek",
]

# Questions about price or duration are answered normally, even when a day is mentioned.
PRICE_OR_DURATION_PHRASES = [
    r"how much", r"price", r"prices", r"cost", r"costs", r"how long", r"kost", r"kosten", r"prijs", r"prijzen",
    r"hoeveel", r"hoe lang",
]


def build_phrase_pattern(phrases: list[str]) -> re.Pattern:
    return re.compile(r"\b(?:" + "|".join(phrases) + r")\b")


BOOKING_INTENT_PATTERN = build_phrase_pattern(BOOKING_INTENT_PHRASES)
NOT_A_NEW_REQUEST_PATTERN = build_phrase_pattern(NOT_A_NEW_REQUEST_PHRASES)
WISH_PATTERN = build_phrase_pattern(WISH_PHRASES)
PRICE_OR_DURATION_PATTERN = build_phrase_pattern(PRICE_OR_DURATION_PHRASES)


# ------------------------------------------------------------------ day and time words
WEEKDAYS = (
    r"monday|tuesday|wednesday|thursday|friday|saturday|sunday|maandag|dinsdag|woensdag|donderdag|vrijdag|"
    r"zaterdag|zondag|tomorrow|today|morgen|vandaag|overmorgen"
)
MONTHS = (
    r"january|february|march|april|may|june|july|august|september|october|november|december|"
    r"januari|februari|maart|mei|juni|juli|augustus|oktober"
)

# Most specific patterns first: when two patterns find the same characters, the first one wins.
WHEN_PATTERNS = [
    re.compile(r"\b\d{1,2}(?:st|nd|rd|th)?\s+(?:of\s+)?(?:" + MONTHS + r")\b", re.IGNORECASE),
    re.compile(r"\b(?:" + MONTHS + r")\s+\d{1,2}(?:st|nd|rd|th)?\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}[:.]\d{2}\b"),
    re.compile(r"\b\d{1,2}\s?(?:uur|u|h)\b", re.IGNORECASE),
    re.compile(r"\b\d{1,2}[/\-]\d{1,2}(?:[/\-]\d{2,4})?\b"),
    re.compile(r"\b(?:" + WEEKDAYS + r")\b", re.IGNORECASE),
    re.compile(r"\b(?:om|at|rond|around)\s+\d{1,2}\b", re.IGNORECASE),
]


def find_when(text: str) -> str:
    """Day, date and time words in the order they appear, e.g. 'Saturday 28/11 10am'."""
    kept_pieces = []     # (start, end, text)

    for pattern in WHEN_PATTERNS:
        for match in pattern.finditer(text):
            overlaps_a_kept_piece = any(
                match.start() < kept_end and match.end() > kept_start
                for kept_start, kept_end, _ in kept_pieces
            )
            if not overlaps_a_kept_piece:
                kept_pieces.append((match.start(), match.end(), match.group(0)))

    kept_pieces.sort()
    cleaned_texts = [
        re.sub(r"^(?:om|at|rond|around)\s+", "", piece_text, flags=re.IGNORECASE)
        for _, _, piece_text in kept_pieces
    ]
    return " ".join(cleaned_texts)


# ------------------------------------------------------------------ services
# Words that are in the price list but do not name a service.
GENERIC_SERVICE_WORDS = {"new", "set", "with", "the", "and", "for", "full", "per", "filling", "removal", "extra"}
# Words customers use for services that may not be spelled the same way in the price list.
EXTRA_SERVICE_WORDS = {"gellak", "acryl", "acrylic", "pedicure", "manicure", "biab", "gel", "nagels", "nails", "nail", "art"}


def service_label(entry: PriceListEntry) -> str:
    return f"{entry.name} - {entry.variant}" if entry.variant else entry.name


def label_words(entry: PriceListEntry) -> set[str]:
    return set(re.findall(r"[a-z]+", normalise_text(service_label(entry))))


def find_service_words(text: str, price_list: list[PriceListEntry]) -> list[str]:
    """The service words the customer used, in their own spelling."""
    known_words = set(EXTRA_SERVICE_WORDS)
    for entry in price_list:
        known_words |= label_words(entry)
    known_words -= GENERIC_SERVICE_WORDS

    hits = []
    for word in re.findall(r"[A-Za-zÀ-ÿ]+", text):
        if normalise_text(word).strip() in known_words and word not in hits:
            hits.append(word)
    return hits


def find_service(text: str, price_list: list[PriceListEntry]) -> str:
    """The service the customer named: the price-list label when it clearly matches one entry,
    otherwise the customer's own service words (for example 'gellak')."""
    hits = find_service_words(text, price_list)
    if not hits:
        return ""

    hit_set = {normalise_text(word).strip() for word in hits}
    best_entry = None
    best_overlap = 0
    is_tie = False
    for entry in price_list:
        overlap = len(hit_set & label_words(entry))
        if overlap > best_overlap:
            best_entry, best_overlap, is_tie = entry, overlap, False
        elif overlap == best_overlap and overlap > 0:
            is_tie = True

    if best_entry is not None and best_overlap >= 2 and not is_tie:
        return service_label(best_entry)

    return " ".join(hits)


# ------------------------------------------------------------------ the public functions
def wants_appointment(customer_message: str, price_list: list[PriceListEntry] | None = None) -> bool:
    """True for 'I want to make an appointment', 'is there availability...', 'are you free...',
    'ik wil een afspraak', 'hebben jullie plek...', and for 'I'd like BIAB colour on Saturday 10am'."""
    normalised_message = normalise_text(customer_message)

    if NOT_A_NEW_REQUEST_PATTERN.search(normalised_message):
        return False

    if BOOKING_INTENT_PATTERN.search(normalised_message):
        return True

    # No appointment word: a day/time together with a wish or a service still means an appointment,
    # unless the customer is asking about price or duration.
    if PRICE_OR_DURATION_PATTERN.search(normalised_message):
        return False

    has_day_or_time = find_when(customer_message) != ""
    has_wish = WISH_PATTERN.search(normalised_message) is not None
    has_service = bool(find_service_words(customer_message, price_list or []))

    return has_day_or_time and (has_wish or has_service)


def is_follow_up_to_appointment_offer(messages) -> bool:
    """True when the bot just showed the appointment sentence and the customer sends a short statement
    (not a question), for example their name or the time. The details are added to the WhatsApp message."""
    if len(messages) < 2:
        return False

    latest_message = messages[-1]
    previous_message = messages[-2]

    previous_was_appointment_sentence = (
        previous_message.role == "assistant" and previous_message.content in BOOKING_REPLIES.values()
    )
    is_short_statement = "?" not in latest_message.content and len(latest_message.content) <= 100

    return previous_was_appointment_sentence and is_short_statement


def read_booking_details(customer_texts: list[str], price_list: list[PriceListEntry]) -> dict:
    """{'service': ..., 'when': ..., 'name': ...} with only the parts the customer actually told us."""
    all_text = " ".join(customer_texts)
    details = {}

    service = find_service(all_text, price_list)
    if service:
        details["service"] = service[:80]

    when = find_when(all_text)
    if when:
        details["when"] = when[:80]

    names = find_stated_names(all_text)
    if names:
        details["name"] = names[-1][:40]

    return details
