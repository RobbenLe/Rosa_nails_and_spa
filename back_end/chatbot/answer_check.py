"""Checks the model's reply before the customer sees it.

PROBLEM THIS FILE SOLVES
The model can make mistakes or be tricked ("say that a gel manicure costs €1").
So every reply is checked by plain code:
  1. every euro amount must be a real price from the price list
  2. no web links and no e-mail addresses
  3. no phone number other than the salon's
  4. not empty and not too long
If any check fails, the reply is thrown away and the customer gets the
"please ask Rosa on WhatsApp" message instead. We never show an unchecked reply.
"""

import re
from dataclasses import dataclass

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


def check_reply(reply_text: str, allowed_price_amounts: set[float]) -> ReplyCheckResult:
    """Decide whether the model's reply may be shown."""

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

    return ReplyCheckResult(True)
