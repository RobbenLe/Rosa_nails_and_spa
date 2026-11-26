"""Appointment requests: every way of asking (English and Dutch) must get the fixed appointment
sentence (a) and the Book button at once, without the AI model, and without asking anything back.

Found in production: "Is there availability on Friday at 3pm?", "Hebben jullie plek op vrijdag om 15:00?"
and bookings with a name in one message fell into the 'ask Rosa' answer (b).
"""

import json
import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from chatbot import model_client
from chatbot.assistant import ChatMessage, answer_conversation
from chatbot.booking_intent import find_when, wants_appointment
from chatbot.fixed_replies import ASK_ROSA_REPLIES, BOOKING_REPLIES
from chatbot.names import find_stated_names, remove_stated_names
from chatbot.price_list import PriceListEntry
from chatbot.safety import is_personal_request

PRICE_LIST = [
    PriceListEntry("Manicure & Pedicure", "Gel Manicure", "", 60, 2500),
    PriceListEntry("Manicure & Pedicure", "Classic Pedicure", "", 40, 4000),
    PriceListEntry("BIAB & Gel", "BIAB (Builder Gel)", "Biab Colour", 75, 5000),
    PriceListEntry("BIAB & Gel", "BIAB (Builder Gel)", "Biab Combination Gellak", 75, 5500),
]


def model_must_not_be_called(instructions, messages):
    raise AssertionError("an appointment request must not need the model")


def ask(*customer_texts):
    history = []
    for customer_text in customer_texts:
        history.append(ChatMessage("user", customer_text))
    return answer_conversation(history, model_must_not_be_called, lambda: PRICE_LIST)


APPOINTMENT_REQUESTS = [
    # English
    ("I want to make an appointment on Friday", "en"),
    ("I'd like an appointment", "en"),
    ("Is there availability on Friday at 3pm?", "en"),
    ("Is there availability at 3pm tomorrow?", "en"),
    ("Are you free on Saturday?", "en"),
    ("Are you free tomorrow at 14:00?", "en"),
    ("Can I book a gel manicure for next week?", "en"),
    ("Can I book Friday 3pm?", "en"),
    ("Do you have time on Friday?", "en"),
    ("Do you have any space this Saturday?", "en"),
    ("Do you have any openings next week?", "en"),
    ("Is Rosa available on Tuesday at 15:00?", "en"),
    ("How do I book?", "en"),
    ("Can I come by on Thursday at 11?", "en"),
    ("I'd like BIAB colour on Saturday 28/11 at 10am, my name is Anna", "en"),
    ("I'd like BIAB colour Saturday 10am, my name is Anna", "en"),
    ("Hi, I'd like a gel manicure on Monday at 2pm. My name is Lisa", "en"),
    # Dutch
    ("Ik wil een afspraak maken", "nl"),
    ("Ik wil een afspraak maken voor vrijdag", "nl"),
    ("Hebben jullie plek op vrijdag om 15:00?", "nl"),
    ("Hebben jullie nog tijd morgen?", "nl"),
    ("Is er nog plek op zaterdag?", "nl"),
    ("Zijn jullie vrij op maandag?", "nl"),
    ("Is Rosa beschikbaar op woensdag?", "nl"),
    ("Kan ik een afspraak boeken voor zaterdag om 10 uur?", "nl"),
    ("Kan ik langskomen op donderdag?", "nl"),
    ("Ik wil zaterdag om 10 uur gellak, ik heet Anna", "nl"),
    ("Ik wil graag een gel pedicure op dinsdag om 14:00. Mijn naam is Sanne", "nl"),
]


@pytest.mark.parametrize("customer_text, language", APPOINTMENT_REQUESTS)
def test_appointment_requests_get_sentence_a_and_the_book_button(customer_text, language):
    answer = ask(customer_text)

    assert answer.outcome == "booking", f"outcome={answer.outcome} reason={answer.reason}"
    assert answer.reply == BOOKING_REPLIES[language]
    assert answer.language == language
    assert answer.button == "book"
    assert answer.show_whatsapp_button is True


def test_the_bot_never_says_whether_there_is_room():
    for customer_text, language in APPOINTMENT_REQUESTS:
        reply = ask(customer_text).reply.lower()
        for forbidden in ["available", "beschikbaar", "free", "vrij", "full", "volgeboekt", "no space", "yes,"]:
            assert forbidden not in reply


# ------------------------------------------------------------------ what goes into the WhatsApp message
def test_message_details_contain_what_the_customer_said_service_time_and_name():
    details = ask("I'd like BIAB colour on Saturday 28/11 at 10am, my name is Anna").booking
    assert details == {"service": "BIAB (Builder Gel) - Biab Colour", "when": "Saturday 28/11 10am", "name": "Anna"}


def test_dutch_details_keep_the_customers_own_service_word():
    details = ask("Ik wil zaterdag om 10 uur gellak, ik heet Anna").booking
    assert details == {"service": "gellak", "when": "zaterdag 10 uur", "name": "Anna"}


def test_missing_parts_are_left_out():
    assert ask("Is there availability on Friday at 3pm?").booking == {"when": "Friday 3pm"}
    assert ask("Ik wil een afspraak").booking == {}
    assert ask("I want to make an appointment, my name is Lisa").booking == {"name": "Lisa"}
    assert ask("Can I book a gel manicure?").booking == {"service": "Gel Manicure"}


def test_details_from_follow_up_messages_are_added():
    history = [
        ChatMessage("user", "I want to make an appointment"),
        ChatMessage("assistant", BOOKING_REPLIES["en"]),
        ChatMessage("user", "Friday at 3pm"),
        ChatMessage("assistant", BOOKING_REPLIES["en"]),
        ChatMessage("user", "my name is Anna"),
    ]
    answer = answer_conversation(history, model_must_not_be_called, lambda: PRICE_LIST)
    assert answer.reply == BOOKING_REPLIES["en"]
    assert answer.booking == {"when": "Friday 3pm", "name": "Anna"}


def test_appointment_request_works_even_when_the_price_list_cannot_be_read():
    def broken_database():
        raise ConnectionError("database down")

    history = [ChatMessage("user", "Are you free on Friday at 3pm?")]
    answer = answer_conversation(history, model_must_not_be_called, broken_database)
    assert answer.reply == BOOKING_REPLIES["en"]
    assert answer.booking == {"when": "Friday 3pm"}


# ------------------------------------------------------------------ not appointment requests
@pytest.mark.parametrize("customer_text", [
    "How much is a gel manicure?",
    "How much is gel on Saturday?",
    "What are your opening hours?",
    "What time do you close on Saturday?",
    "Are you open on Sunday?",
    "Zijn jullie op zondag open?",
    "Wat kost een gel pedicure?",
    "Waar is de salon?",
    "Do you take walk-ins?",
    "How can I pay?",
    "Can I cancel my appointment?",
    "How early must I book?",
    "Kan ik mijn afspraak annuleren?",
    "Hoe vroeg moet ik boeken?",
])
def test_ordinary_questions_are_not_taken_for_appointment_requests(customer_text):
    assert wants_appointment(customer_text, PRICE_LIST) is False


# ------------------------------------------------------------------ a name is not sensitive
@pytest.mark.parametrize("name", ["Anna", "Christian", "Sanne", "Gay", "Hindu", "Marokko"])
def test_a_stated_name_never_triggers_the_privacy_filter(name):
    assert is_personal_request(f"my name is {name}") is False
    assert is_personal_request(f"ik heet {name}") is False
    assert is_personal_request(f"I'd like a gel manicure on Friday at 3pm, my name is {name}") is False


def test_booking_with_a_name_that_looks_like_a_religion_still_gets_sentence_a():
    answer = ask("I'd like BIAB colour on Saturday at 10am, my name is Christian")
    assert answer.reply == BOOKING_REPLIES["en"]
    assert answer.booking["name"] == "Christian"


def test_name_helpers():
    assert find_stated_names("Ik heet anna en ik wil een afspraak") == ["Anna"]
    assert find_stated_names("My name's Lisa") == ["Lisa"]
    assert find_stated_names("I am Moroccan") == []          # 'I am X' is not a name statement
    assert "Christian" not in remove_stated_names("my name is Christian")


# ------------------------------------------------------------------ real personal details still go to (b)
@pytest.mark.parametrize("customer_text, language", [
    ("I am Moroccan, I only want a woman to do it for me", "en"),
    ("Ik ben Marokkaans, ik wil alleen een vrouw die het voor mij doet", "nl"),
    ("I am Muslim, I'd like an appointment with a woman only", "en"),
    ("I'm pregnant, can I book a gel manicure on Friday?", "en"),
    ("Ik ben zwanger, kan ik een afspraak maken?", "nl"),
    ("I'd like an appointment on Friday. I have an allergy to acrylic", "en"),
])
def test_origin_religion_health_still_get_sentence_b_even_with_an_appointment_word(customer_text, language):
    answer = ask(customer_text)
    assert answer.reply == ASK_ROSA_REPLIES[language]
    assert answer.button == "ask"


# ------------------------------------------------------------------ the model's own flag is a safety net
def test_model_flag_booking_intent_gives_sentence_a():
    def model_flags_an_appointment(instructions, messages):
        return json.dumps({"reply": "", "language": "en", "out_of_scope": False, "booking_intent": True})

    history = [ChatMessage("user", "Would Thursday morning work for you guys?")]
    answer = answer_conversation(history, model_flags_an_appointment, lambda: PRICE_LIST)
    assert answer.reply == BOOKING_REPLIES["en"]
    assert answer.button == "book"
    assert answer.booking == {"when": "Thursday"}


# ------------------------------------------------------------------ the model answers through a tool call
class FakeMessages:
    def __init__(self, blocks):
        self.blocks = blocks
        self.last_arguments = None

    def create(self, **arguments):
        self.last_arguments = arguments
        return SimpleNamespace(content=self.blocks)


def use_fake_client(monkeypatch, blocks):
    fake_messages = FakeMessages(blocks)
    monkeypatch.setattr(model_client, "get_client", lambda: SimpleNamespace(messages=fake_messages))
    return fake_messages


def test_model_client_forces_the_reply_tool_and_returns_valid_json(monkeypatch):
    tool_block = SimpleNamespace(
        type="tool_use",
        name=model_client.REPLY_TOOL_NAME,
        input={"reply": 'He said "hello"', "language": "en", "out_of_scope": False, "booking_intent": False},
    )
    fake_messages = use_fake_client(monkeypatch, [tool_block])

    text = model_client.call_anthropic_model("instructions", [ChatMessage("user", "hi")])

    assert fake_messages.last_arguments["tool_choice"] == {"type": "tool", "name": model_client.REPLY_TOOL_NAME}
    assert json.loads(text)["reply"] == 'He said "hello"'     # quotes cannot break the answer any more


def test_model_client_falls_back_to_plain_text_when_there_is_no_tool_call(monkeypatch):
    use_fake_client(monkeypatch, [SimpleNamespace(type="text", text="plain words")])
    assert model_client.call_anthropic_model("instructions", [ChatMessage("user", "hi")]) == "plain words"


def test_find_when_keeps_am_pm_and_dates():
    assert find_when("Saturday 28/11 at 10am") == "Saturday 28/11 10am"
    assert find_when("vrijdag om 15:00") == "vrijdag 15:00"
    assert find_when("on 5 December at 11") == "5 December 11"
