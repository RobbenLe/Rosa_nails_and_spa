"""The chatbot's brain: turns a conversation into one safe answer.

PROBLEM THIS FILE SOLVES
Connects the safety filter, the live price list, the AI model and the reply checker in a
fixed order, and guarantees that whatever goes wrong (database down, model error, strange
reply) the customer gets a calm "ask Rosa on WhatsApp" message instead of a guess.

The model call and the price list loader are passed in, so tests can run the whole
pipeline without internet, a database or any cost.
"""

import json
import re
from dataclasses import dataclass
from typing import Callable

from chatbot import settings
from chatbot.answer_check import check_reply
from chatbot.price_list import PriceListEntry, allowed_price_amounts_in_euros
from chatbot.prompt import build_instructions
from chatbot.safety import HEALTH_FIXED_REPLY, any_message_mentions_health_topic

# Same message in both languages, because when something fails we cannot be sure of the language.
FALLBACK_REPLY = (
    "I'm not sure about that, so I don't want to guess. Rosa can help you best on WhatsApp.\n\n"
    "Daar ben ik niet zeker van, en ik wil niet gokken. Rosa helpt je het beste via WhatsApp."
)

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
    outcome: str             # "answer", "booking", "health", "unsure", "fallback"  (for logs, no personal data)


# A function that takes (instructions, messages) and returns the model's raw text.
ModelCaller = Callable[[str, list[ChatMessage]], str]
PriceListLoader = Callable[[], list[PriceListEntry]]


def make_fallback_answer(outcome: str = "fallback") -> ChatAnswer:
    return ChatAnswer(FALLBACK_REPLY, show_whatsapp_button=True, booking=None, outcome=outcome)


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
    """Follow the fixed steps. Any problem leads to the WhatsApp fallback."""

    recent_messages = messages[-settings.MAX_MESSAGES_IN_CONVERSATION:]
    customer_texts = [message.content for message in recent_messages if message.role == "user"]

    # Step 1: health topics get the fixed reply and the model is never called
    if any_message_mentions_health_topic(customer_texts):
        return ChatAnswer(HEALTH_FIXED_REPLY, show_whatsapp_button=True, booking=None, outcome="health")

    # Step 2: read the live price list (read-only database user)
    try:
        price_list = load_prices()
    except Exception:
        return make_fallback_answer("fallback")

    if not price_list:
        return make_fallback_answer("fallback")

    # Step 3: ask the model
    try:
        model_text = call_model(build_instructions(price_list), recent_messages)
    except Exception:
        return make_fallback_answer("fallback")

    # Step 4: the model must answer in the agreed shape
    parsed_answer = extract_json_object(model_text)
    if parsed_answer is None or not isinstance(parsed_answer.get("reply"), str):
        return make_fallback_answer("fallback")

    # Step 5: when the model says it is unsure, show our fixed message, not its words
    if parsed_answer.get("unsure") is True:
        return make_fallback_answer("unsure")

    # Step 6: check the reply text (prices, links, phone numbers, length)
    reply_text = parsed_answer["reply"].strip()
    reply_check = check_reply(reply_text, allowed_price_amounts_in_euros(price_list))
    if not reply_check.is_acceptable:
        return make_fallback_answer("fallback")

    # Step 7: keep a booking request only if it is complete and valid
    booking = validate_booking(parsed_answer.get("booking"), price_list)
    mentions_whatsapp = "whatsapp" in reply_text.lower()

    return ChatAnswer(
        reply=reply_text,
        show_whatsapp_button=booking is not None or mentions_whatsapp,
        booking=booking,
        outcome="booking" if booking else "answer",
    )
