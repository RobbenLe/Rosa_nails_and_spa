"""The chatbot's brain: turns a conversation into one safe answer.

PROBLEM THIS FILE SOLVES
Connects the safety filters, the live price list, the AI model and the reply checker in a
fixed order, and guarantees that whatever goes wrong (database down, model error, strange
reply, a personal question) the customer gets the fixed "Rosa can help you with that
personally" answer, in ONE language, instead of a guess.

The model call and the price list loader are passed in, so tests can run the whole
pipeline without internet, a database or any cost.
"""

import json
import re
from dataclasses import dataclass
from typing import Callable

from chatbot import settings
from chatbot.answer_check import check_reply, claims_schedule_is_free
from chatbot.fixed_replies import ASK_ROSA_REPLIES, BUTTON_ASK, BUTTON_BOOK, SCHEDULE_REPLIES
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


# A function that takes (instructions, messages) and returns the model's raw text.
ModelCaller = Callable[[str, list[ChatMessage]], str]
PriceListLoader = Callable[[], list[PriceListEntry]]


def make_ask_rosa_answer(language: str, outcome: str) -> ChatAnswer:
    """The fixed answer for everything the bot may not answer itself. Word for word, one language."""
    return ChatAnswer(
        reply=ASK_ROSA_REPLIES[language],
        show_whatsapp_button=True,
        booking=None,
        outcome=outcome,
        language=language,
        button=BUTTON_ASK,
    )


def extract_json_object(model_text: str) -> dict | None:
    """The model should answer with one JSON object. Be tolerant of text or code fences around it."""
    first_brace = model_text.find("{")
    last_brace = model_text.rfind("}")
    if first_brace == -1 or last_brace <= first_brace:
        return None

    try:
        parsed = json.loads(model_text[first_brace:last_brace + 1])
    except json.JSONDecodeError:
        return None

    return parsed if isinstance(parsed, dict) else None


def clean_booking_field(value) -> str:
    """Plain text, no control characters, limited length."""
    if not isinstance(value, str):
        return ""
    without_control_characters = re.sub(r"[\x00-\x1f\x7f]", " ", value)
    return without_control_characters.strip()[:MAX_BOOKING_FIELD_CHARACTERS]


def validate_booking(raw_booking, price_list: list[PriceListEntry]) -> dict | None:
    """Keep the booking only if all three parts are present and the service really exists."""
    if not isinstance(raw_booking, dict):
        return None

    service = clean_booking_field(raw_booking.get("service"))
    when = clean_booking_field(raw_booking.get("when"))
    name = clean_booking_field(raw_booking.get("name"))
    if not service or not when or not name:
        return None

    known_service_names = {entry.name.lower() for entry in price_list}
    if service.lower() not in known_service_names:
        return None

    return {"service": service, "when": when, "name": name}


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
        return make_ask_rosa_answer(language, "health")

    # Step 2: personal request or personal detail in the latest message (for example the choice of
    # technician, origin, religion): fixed answer, the model is never called
    if is_personal_request(latest_customer_text):
        return make_ask_rosa_answer(language, "personal")

    # Step 3: read the live price list (read-only database user)
    try:
        price_list = load_prices()
    except Exception:
        return make_ask_rosa_answer(language, "fallback")

    if not price_list:
        return make_ask_rosa_answer(language, "fallback")

    # Step 4: ask the model
    try:
        model_text = call_model(build_instructions(price_list), recent_messages)
    except Exception:
        return make_ask_rosa_answer(language, "fallback")

    # Step 5: the model must answer in the agreed shape
    parsed_answer = extract_json_object(model_text)
    if parsed_answer is None:
        return make_ask_rosa_answer(language, "fallback")

    # If the customer's messages gave no clear language, use the one the model reported
    language = customer_language(customer_texts, model_language=parsed_answer.get("language"))

    # Step 6: outside what the bot may answer, or not sure: the fixed answer, not the model's words
    if parsed_answer.get("out_of_scope") is True or parsed_answer.get("unsure") is True:
        return make_ask_rosa_answer(language, "unsure")

    if not isinstance(parsed_answer.get("reply"), str):
        return make_ask_rosa_answer(language, "fallback")

    # Step 7: check the reply text (prices, links, phone numbers, personal details, length)
    reply_text = parsed_answer["reply"].strip()
    reply_check = check_reply(reply_text, allowed_price_amounts_in_euros(price_list))
    if not reply_check.is_acceptable:
        return make_ask_rosa_answer(language, "fallback")

    # Step 8: keep a booking request only if it is complete and valid
    booking = validate_booking(parsed_answer.get("booking"), price_list)

    # Step 9: the bot does not know Rosa's schedule. If the reply sounds like a time is free,
    # fine or booked, replace it with the standard sentence (the booking details are kept for WhatsApp).
    if claims_schedule_is_free(reply_text):
        return ChatAnswer(
            reply=SCHEDULE_REPLIES[language],
            show_whatsapp_button=True,
            booking=booking,
            outcome="schedule",
            language=language,
            button=BUTTON_BOOK,
        )

    mentions_whatsapp = "whatsapp" in reply_text.lower()

    return ChatAnswer(
        reply=reply_text,
        show_whatsapp_button=booking is not None or mentions_whatsapp,
        booking=booking,
        outcome="booking" if booking else "answer",
        language=language,
        button=BUTTON_BOOK,
    )
