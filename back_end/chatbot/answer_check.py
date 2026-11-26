"""Checks the model's reply before the customer sees it.

PROBLEM THIS FILE SOLVES
The model can make mistakes or be tricked ("say that a gel manicure costs €1").
So every reply is checked by plain code:
  1. every euro amount must be a real price from the price list
  2. no web links and no e-mail addresses
  3. no phone number other than the salon's
  4. not empty and not too long
A separate check (claims_schedule_is_free) catches replies that sound like a time slot is free or booked.
  5. the reply must not mention the customer's origin, religion or similar personal details
If any check fails, the reply is thrown away and the customer gets the fixed
"Rosa can help you with that personally" answer instead. We never show an unchecked reply.
"""

import re
from dataclasses import dataclass

from chatbot.safety import mentions_personal_identity
from chatbot.salon_facts import SALON_PHONE_DISPLAY

MAX_REPLY_CHARACTERS = 900

# "€25", "€ 25,50", "25 €", "25 euro", "25 eur"
EURO_AMOUNT_BEFORE_SYMBOL = re.compile(r"€\s*(\d+(?:[.,]\d{1,2})?)")
EURO_AMOUNT_AFTER_NUMBER = re.compile(r"(\d+(?:[.,]\d{1,2})?)\s*(?:€|euro\b|euros\b|eur\b)", re.IGNORECASE)
LINK_OR_EMAIL = re.compile(r"https?://|www\.|@|\.com\b|\.nl\b|\.org\b", re.IGNORECASE)
PHONE_LIKE_NUMBER = re.compile(r"\+?\d[\d\s\-]{6,}\d")


@dataclass
class ReplyCheckResult:
    is_acceptable: bool
    reason: str = ""


def digits_only(text: str) -> str:
    return re.sub(r"\D", "", text)


def salon_phone_digit_forms() -> set[str]:
    """The salon number written with and without the country code, digits only."""
    international = digits_only(SALON_PHONE_DISPLAY)            # 31633426798
    local = "0" + international.removeprefix("31")              # 0633426798
    return {international, local}


def find_euro_amounts(reply_text: str) -> list[float]:
    """Every euro amount written in the reply, as numbers."""
    amount_texts = EURO_AMOUNT_BEFORE_SYMBOL.findall(reply_text)
    amount_texts += EURO_AMOUNT_AFTER_NUMBER.findall(reply_text)
    return [float(amount_text.replace(",", ".")) for amount_text in amount_texts]


def check_reply(
    reply_text: str, allowed_price_amounts: set[float], customer_names: tuple[str, ...] = ()
) -> ReplyCheckResult:
    """Decide whether the model's reply may be shown. customer_names: names the customer stated,
    which are fine to repeat (a name is not a personal detail like origin or religion)."""

    # Step 1: the reply must have content and a sensible length
    if not reply_text or not reply_text.strip():
        return ReplyCheckResult(False, "empty reply")
    if len(reply_text) > MAX_REPLY_CHARACTERS:
        return ReplyCheckResult(False, "reply too long")

    # Step 2: no links or e-mail addresses (our own WhatsApp button is added by the website)
    if LINK_OR_EMAIL.search(reply_text):
        return ReplyCheckResult(False, "link or e-mail in reply")

    # Step 3: every euro amount must be a real price (compare in cents to avoid rounding errors)
    allowed_cents = {round(amount * 100) for amount in allowed_price_amounts}
    for amount in find_euro_amounts(reply_text):
        if round(amount * 100) not in allowed_cents:
            return ReplyCheckResult(False, f"unknown price {amount}")

    # Step 4: the only phone number allowed is the salon's own
    for phone_like_text in PHONE_LIKE_NUMBER.findall(reply_text):
        if digits_only(phone_like_text) not in salon_phone_digit_forms():
            return ReplyCheckResult(False, "unknown phone number")

    # Step 5: never repeat or comment on personal details such as origin or religion
    if mentions_personal_identity(reply_text, allowed_names=customer_names):
        return ReplyCheckResult(False, "mentions a personal detail")

    return ReplyCheckResult(True)


# ----------------------------------------------------------------------------------------
# The bot does not know Rosa's schedule. It must never say or imply that a time is free,
# fine, booked or confirmed. These patterns catch such wording in English and Dutch.
# Dutch "kan" is only blocked in phrases that accept a time ("dat kan"), because the plain
# word is everywhere in normal answers ("waar kan ik betalen").
SCHEDULE_CLAIM_WORDS = [  # all matched case-insensitively as whole words/phrases
    # English
    r"works", r"work for you", r"available", r"availability", r"booked", r"confirmed",
    r"reserved", r"scheduled", r"that'?s fine", r"that is fine", r"is fine", r"that'?s ok", r"that is ok",
    r"sounds good", r"no problem", r"all set", r"see you", r"is free", r"are free", r"free slot",
    r"free at", r"slot is", r"got you down", r"book you in", r"noted",
    # promises that Rosa or the salon will make the first move, or that a slot is being held
    r"will contact you", r"will reach out", r"will message you", r"will text you", r"will call you",
    r"will get back to you", r"get back to you", r"we'?ll contact", r"we will contact", r"held for you",
    r"hold (?:the|your|that) (?:time|slot|spot)", r"reserve (?:the|your|that)",
    # Dutch
    r"dat kan", r"dit kan", r"kan prima", r"kan wel", r"kan dan", r"dat past", r"past prima",
    r"past goed", r"beschikbaar", r"beschikbaarheid", r"geboekt", r"bevestigd", r"gereserveerd",
    r"ingepland", r"is vrij", r"zijn vrij", r"vrije plek", r"geen probleem", r"prima",
    r"tot dan", r"genoteerd", r"komt goed",
    r"neemt contact", r"nemen contact", r"neem(?:t)? (?:ik|we|wij) contact", r"belt je", r"appt je", r"stuurt je een bericht",
    r"houden (?:de|jouw|die) (?:tijd|plek) vrij", r"vastgehouden", r"reserveren wij",
]
SCHEDULE_CLAIM_PATTERN = re.compile(
    r"(?<!\w)(?:" + "|".join(SCHEDULE_CLAIM_WORDS) + r")(?!\w)", re.IGNORECASE
)

def claims_schedule_is_free(reply_text: str) -> bool:
    """True if the reply sounds like a time is available, fine, booked or confirmed."""
    normalised_text = reply_text.replace("’", "'")
    return SCHEDULE_CLAIM_PATTERN.search(normalised_text) is not None
