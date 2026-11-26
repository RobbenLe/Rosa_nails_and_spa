"""The chatbot's brain: turns a conversation into one safe answer.

PROBLEM THIS FILE SOLVES
Connects the safety filters, appointment recognition, the live price list, the AI model and the
reply checker in a fixed order, and guarantees that whatever goes wrong (database down, model error,
strange reply, a personal question) the customer gets a fixed answer, in ONE language, instead of a guess.

Two fixed answers exist (see fixed_replies.py):
  (a) appointment requests: "Rosa manages all appointments personally. Tap Book via WhatsApp..."
  (b) everything else the bot may not answer: "Rosa can help you with that personally. Tap Ask on WhatsApp..."

The model call and the price list loader are passed in, so tests can run the whole
pipeline without internet, a database or any cost.
"""

import json
import re
from dataclasses import dataclass
from typing import Callable

from chatbot import settings
from chatbot.answer_check import check_reply, claims_schedule_is_free
from chatbot.booking_intent import is_follow_up_to_appointment_offer, read_booking_details, wants_appointment
from chatbot.fixed_replies import ASK_ROSA_REPLIES, BOOKING_REPLIES, BUTTON_ASK, BUTTON_BOOK
from chatbot.language import customer_language
from chatbot.names import find_stated_names
from chatbot.price_list import PriceListEntry, allowed_price_amounts_in_euros
from chatbot.prompt import build_instructions
from chatbot.safety import any_message_mentions_health_topic, is_personal_request


@dataclass
class ChatMessage:
    role: str      # "user" or "assistant"
    content: str


@dataclass
class ChatAnswer:
    reply: str
    show_whatsapp_button: bool
    booking: dict | None     # what the customer told us: any of {"service", "when", "name"}; {} or None if nothing
    outcome: str             # "answer", "booking", "health", "personal", "unsure", "schedule", "fallback" (for logs, no personal data)
    language: str = "en"     # "en" or "nl": the language of the reply, so the button label can match
    button: str = BUTTON_BOOK  # "ask" or "book": which WhatsApp button label to show
    reason: str = ""         # short code saying WHY a fixed answer was used (for logs; never contains customer text)


# A function that takes (instructions, messages) and returns the model's raw text.
ModelCaller = Callable[[str, list[ChatMessage]], str]
PriceListLoader = Callable[[], list[PriceListEntry]]


def make_ask_rosa_answer(language: str, outcome: str, reason: str = "") -> ChatAnswer:
    """(b) The fixed answer for everything the bot may not answer itself. Word for word, one language."""
    return ChatAnswer(
        reply=ASK_ROSA_REPLIES[language],
        show_whatsapp_button=True,
        booking=None,
        outcome=outcome,
        language=language,
        button=BUTTON_ASK,
        reason=reason,
    )


def make_booking_answer(language: str, details: dict, outcome: str, reason: str = "") -> ChatAnswer:
    """(a) The fixed appointment sentence. The details (service, when, name) only fill the WhatsApp message."""
    return ChatAnswer(
        reply=BOOKING_REPLIES[language],
        show_whatsapp_button=True,
        booking=details,
        outcome=outcome,
        language=language,
        button=BUTTON_BOOK,
        reason=reason,
    )


# ------------------------------------------------------------------ reading the model's answer
def repair_unescaped_quotes_in_reply(json_text: str) -> str:
    """The model sometimes writes a double quote inside the reply text without escaping it,
    which makes the JSON invalid. Escape those quotes so the answer is not lost."""
    pattern = re.compile(
        r'("reply"\s*:\s*")(.*?)("\s*,\s*"(?:language|unsure|out_of_scope|booking_intent|booking)")', re.DOTALL
    )

    def escape_inner_quotes(match: re.Match) -> str:
        inner_text = re.sub(r'(?<!\\)"', r'\\"', match.group(2))
        return match.group(1) + inner_text + match.group(3)

    return pattern.sub(escape_inner_quotes, json_text, count=1)


def extract_json_object(model_text: str) -> dict | None:
    """The model answers with one JSON object. Be tolerant of text or code fences around it."""
    first_brace = model_text.find("{")
    last_brace = model_text.rfind("}")
    if first_brace == -1 or last_brace <= first_brace:
        return None

    json_text = model_text[first_brace:last_brace + 1]

    for candidate_text in (json_text, repair_unescaped_quotes_in_reply(json_text)):
        try:
            parsed = json.loads(candidate_text, strict=False)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    return None


# ------------------------------------------------------------------ the main steps
def answer_conversation(
    messages: list[ChatMessage],
    call_model: ModelCaller,
    load_prices: PriceListLoader,
) -> ChatAnswer:
    """Follow the fixed steps. Appointment requests get (a), anything else the bot may not answer gets (b)."""

    recent_messages = messages[-settings.MAX_MESSAGES_IN_CONVERSATION:]
    customer_texts = [message.content for message in recent_messages if message.role == "user"]
    latest_customer_text = customer_texts[-1] if customer_texts else ""
    language = customer_language(customer_texts)
    customer_names = tuple(find_stated_names(" ".join(customer_texts)))

    # Step 1: health topics anywhere in the recent conversation: (b), the model is never called
    if any_message_mentions_health_topic(customer_texts):
        return make_ask_rosa_answer(language, "health", "health word")

    # Step 2: personal request or personal detail in the latest message (for example the choice of
    # technician, origin, religion): (b), the model is never called. A stated name is not a personal detail.
    if is_personal_request(latest_customer_text):
        return make_ask_rosa_answer(language, "personal", "personal request")

    # Step 3: read the live price list (read-only database user). A failure is remembered, not raised,
    # because appointment requests do not need it.
    price_list: list[PriceListEntry] = []
    price_list_problem = ""
    try:
        price_list = load_prices()
    except Exception as error:
        price_list_problem = f"price list error: {type(error).__name__}"
    if not price_list and not price_list_problem:
        price_list_problem = "price list is empty"

    # Step 4: an appointment request (or the continuation of one): (a) right away, nothing is asked back.
    # The bot never says whether Rosa has time, because it does not know her schedule.
    if wants_appointment(latest_customer_text, price_list) or is_follow_up_to_appointment_offer(recent_messages):
        details = read_booking_details(customer_texts, price_list)
        return make_booking_answer(language, details, "booking", "appointment request")

    if price_list_problem:
        return make_ask_rosa_answer(language, "fallback", price_list_problem)

    # Step 5: ask the model (everything that is not an appointment request)
    try:
        model_text = call_model(build_instructions(price_list), recent_messages)
    except Exception as error:
        return make_ask_rosa_answer(language, "fallback", f"model error: {type(error).__name__}")

    parsed_answer = extract_json_object(model_text)
    if parsed_answer is None:
        return make_ask_rosa_answer(language, "fallback", "model answer is not valid JSON")

    # If the customer's messages gave no clear language, use the one the model reported
    language = customer_language(customer_texts, model_language=parsed_answer.get("language"))

    # Step 6: the model itself saw an appointment request that the word lists missed: (a)
    if parsed_answer.get("booking_intent") is True or isinstance(parsed_answer.get("booking"), dict):
        details = read_booking_details(customer_texts, price_list)
        return make_booking_answer(language, details, "booking", "model saw an appointment request")

    # Step 7: outside what the bot may answer, or not sure: (b), not the model's words
    if parsed_answer.get("out_of_scope") is True or parsed_answer.get("unsure") is True:
        return make_ask_rosa_answer(language, "unsure", "model says out of scope")

    # Step 8: a normal answer: check the reply text (prices, links, phone numbers, personal details, length)
    if not isinstance(parsed_answer.get("reply"), str):
        return make_ask_rosa_answer(language, "fallback", "model answer has no reply text")

    reply_text = parsed_answer["reply"].strip()
    reply_check = check_reply(reply_text, allowed_price_amounts_in_euros(price_list), customer_names)
    if not reply_check.is_acceptable:
        return make_ask_rosa_answer(language, "fallback", f"reply check: {reply_check.reason}")

    # Step 9: if the reply sounds like a time is free, fine or booked, show (a) instead
    if claims_schedule_is_free(reply_text):
        details = read_booking_details(customer_texts, price_list)
        return make_booking_answer(language, details, "schedule", "reply sounded like a free time")

    return ChatAnswer(
        reply=reply_text,
        show_whatsapp_button="whatsapp" in reply_text.lower(),
        booking=None,
        outcome="answer",
        language=language,
        button=BUTTON_BOOK,
    )
