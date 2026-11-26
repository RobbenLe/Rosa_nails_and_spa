"""The chatbot's brain: turns a conversation into one safe answer.

PROBLEM THIS FILE SOLVES
Connects the safety filters, the live price list, the AI model and the reply checker in a
fixed order, and guarantees that whatever goes wrong (database down, model error, strange
reply, a personal question) the customer gets the fixed "Rosa can help you with that
personally" answer, in ONE language, instead of a guess.

Appointment requests also get a fixed sentence: the model only collects service, time and name;
the sentence the customer reads is written by us (see fixed_replies.py).

The model call and the price list loader are passed in, so tests can run the whole
pipeline without internet, a database or any cost.
"""

import json
import re
from dataclasses import dataclass
from typing import Callable

from chatbot import settings
from chatbot.answer_check import check_reply, claims_schedule_is_free
from chatbot.fixed_replies import ASK_ROSA_REPLIES, BOOKING_REPLIES, BUTTON_ASK, BUTTON_BOOK
from chatbot.language import customer_language
from chatbot.price_list import PriceListEntry, allowed_price_amounts_in_euros
from chatbot.prompt import build_instructions
from chatbot.safety import any_message_mentions_health_topic, is_personal_request

MAX_BOOKING_FIELD_CHARACTERS = 80


@dataclass
class ChatMessage:
    role: str      # "user" or "assistant"
    content: str


@dataclass
class ChatAnswer:
    reply: str
    show_whatsapp_button: bool
    booking: dict | None     # {"service": ..., "when": ..., "name": ...} or None
    outcome: str             # "answer", "booking", "health", "personal", "unsure", "schedule", "fallback" (for logs, no personal data)
    language: str = "en"     # "en" or "nl": the language of the reply, so the button label can match
    button: str = BUTTON_BOOK  # "ask" or "book": which WhatsApp button label to show
    reason: str = ""         # short code saying WHY a fixed fallback was used (for logs; never contains customer text)


# A function that takes (instructions, messages) and returns the model's raw text.
ModelCaller = Callable[[str, list[ChatMessage]], str]
PriceListLoader = Callable[[], list[PriceListEntry]]


def make_ask_rosa_answer(language: str, outcome: str, reason: str = "") -> ChatAnswer:
    """The fixed answer for everything the bot may not answer itself. Word for word, one language."""
    return ChatAnswer(
        reply=ASK_ROSA_REPLIES[language],
        show_whatsapp_button=True,
        booking=None,
        outcome=outcome,
        language=language,
        button=BUTTON_ASK,
        reason=reason,
    )


def make_booking_answer(language: str, booking: dict | None, outcome: str) -> ChatAnswer:
    """The fixed appointment sentence. The booking details only fill the WhatsApp message."""
    return ChatAnswer(
        reply=BOOKING_REPLIES[language],
        show_whatsapp_button=True,
        booking=booking,
        outcome=outcome,
        language=language,
        button=BUTTON_BOOK,
    )


# ------------------------------------------------------------------ reading the model's answer
def repair_unescaped_quotes_in_reply(json_text: str) -> str:
    """The model sometimes writes a double quote inside the reply text without escaping it,
    which makes the JSON invalid. Escape those quotes so the answer is not lost."""
    pattern = re.compile(
        r'("reply"\s*:\s*")(.*?)("\s*,\s*"(?:language|unsure|out_of_scope|booking)")', re.DOTALL
    )

    def escape_inner_quotes(match: re.Match) -> str:
        inner_text = re.sub(r'(?<!\\)"', r'\\"', match.group(2))
        return match.group(1) + inner_text + match.group(3)

    return pattern.sub(escape_inner_quotes, json_text, count=1)


def extract_json_object(model_text: str) -> dict | None:
    """The model should answer with one JSON object. Be tolerant of text or code fences around it."""
    first_brace = model_text.find("{")
    last_brace = model_text.rfind("}")
    if first_brace == -1 or last_brace <= first_brace:
        return None

    json_text = model_text[first_brace:last_brace + 1]

    for candidate_text in (json_text, repair_unescaped_quotes_in_reply(json_text)):
        try:
            parsed = json.loads(candidate_text)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    return None


# ------------------------------------------------------------------ booking details
def clean_booking_field(value) -> str:
    """Plain text, no control characters, limited length."""
    if not isinstance(value, str):
        return ""
    without_control_characters = re.sub(r"[\x00-\x1f\x7f]", " ", value)
    return without_control_characters.strip()[:MAX_BOOKING_FIELD_CHARACTERS]


def find_matching_service_label(service_text: str, price_list: list[PriceListEntry]) -> str | None:
    """Match the customer's service words to the price list: by name, by option, or by 'name (option)'.

    The price list has entries like name 'BIAB (Builder Gel)' with option 'Biab Colour', while customers
    say 'BIAB colour'. Returns a readable label for the WhatsApp message, or None if nothing matches.
    """
    wanted_text = service_text.strip().lower()

    for entry in price_list:
        name_text = entry.name.lower()
        option_text = entry.variant.lower()
        full_label = f"{entry.name} - {entry.variant}" if entry.variant else entry.name

        possible_matches = {name_text, option_text, full_label.lower(), f"{name_text} {option_text}".strip()}
        possible_matches.discard("")
        if wanted_text in possible_matches:
            return full_label

    return None


def validate_booking(raw_booking, price_list: list[PriceListEntry]) -> dict | None:
    """Keep the booking only if service, time and name are all present.

    The service label is replaced by the price-list label when it matches. When the customer's words do not
    match any entry exactly (for example 'gellak'), their own words are kept: the message is only text that the
    customer reads and sends to Rosa themselves, and Rosa can understand it.
    """
    if not isinstance(raw_booking, dict):
        return None

    service = clean_booking_field(raw_booking.get("service"))
    when = clean_booking_field(raw_booking.get("when"))
    name = clean_booking_field(raw_booking.get("name"))
    if not service or not when or not name:
        return None

    matching_label = find_matching_service_label(service, price_list)
    return {"service": matching_label or service, "when": when, "name": name}


# ------------------------------------------------------------------ the main steps
def answer_conversation(
    messages: list[ChatMessage],
    call_model: ModelCaller,
    load_prices: PriceListLoader,
) -> ChatAnswer:
    """Follow the fixed steps. Anything the bot may not answer leads to the fixed 'ask Rosa' answer."""

    recent_messages = messages[-settings.MAX_MESSAGES_IN_CONVERSATION:]
    customer_texts = [message.content for message in recent_messages if message.role == "user"]
    latest_customer_text = customer_texts[-1] if customer_texts else ""
    language = customer_language(customer_texts)

    # Step 1: health topics anywhere in the recent conversation: fixed answer, the model is never called
    if any_message_mentions_health_topic(customer_texts):
        return make_ask_rosa_answer(language, "health", "health word")

    # Step 2: personal request or personal detail in the latest message (for example the choice of
    # technician, origin, religion): fixed answer, the model is never called
    if is_personal_request(latest_customer_text):
        return make_ask_rosa_answer(language, "personal", "personal request")

    # Step 3: read the live price list (read-only database user)
    try:
        price_list = load_prices()
    except Exception as error:
        return make_ask_rosa_answer(language, "fallback", f"price list error: {type(error).__name__}")

    if not price_list:
        return make_ask_rosa_answer(language, "fallback", "price list is empty")

    # Step 4: ask the model
    try:
        model_text = call_model(build_instructions(price_list), recent_messages)
    except Exception as error:
        return make_ask_rosa_answer(language, "fallback", f"model error: {type(error).__name__}")

    # Step 5: the model must answer in the agreed shape
    parsed_answer = extract_json_object(model_text)
    if parsed_answer is None:
        return make_ask_rosa_answer(language, "fallback", "model answer is not valid JSON")

    # If the customer's messages gave no clear language, use the one the model reported
    language = customer_language(customer_texts, model_language=parsed_answer.get("language"))

    # Step 6: outside what the bot may answer, or not sure: the fixed answer, not the model's words
    if parsed_answer.get("out_of_scope") is True or parsed_answer.get("unsure") is True:
        return make_ask_rosa_answer(language, "unsure", "model says out of scope")

    # Step 7: a complete appointment request: the fixed appointment sentence (the model's own words are not used)
    booking = validate_booking(parsed_answer.get("booking"), price_list)
    if booking is not None:
        return make_booking_answer(language, booking, "booking")

    # Step 8: a normal answer: check the reply text (prices, links, phone numbers, personal details, length)
    if not isinstance(parsed_answer.get("reply"), str):
        return make_ask_rosa_answer(language, "fallback", "model answer has no reply text")

    reply_text = parsed_answer["reply"].strip()
    reply_check = check_reply(reply_text, allowed_price_amounts_in_euros(price_list))
    if not reply_check.is_acceptable:
        return make_ask_rosa_answer(language, "fallback", f"reply check: {reply_check.reason}")

    # Step 9: the bot does not know Rosa's schedule. If the reply sounds like a time is free,
    # fine or booked, replace it with the fixed appointment sentence.
    if claims_schedule_is_free(reply_text):
        return make_booking_answer(language, None, "schedule")

    return ChatAnswer(
        reply=reply_text,
        show_whatsapp_button="whatsapp" in reply_text.lower(),
        booking=None,
        outcome="answer",
        language=language,
        button=BUTTON_BOOK,
    )
