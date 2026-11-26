"""Tests for the health-question filter: every health question must be caught,
and ordinary salon questions must pass through."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from chatbot.safety import any_message_mentions_health_topic, is_personal_request, mentions_health_topic

HEALTH_MESSAGES = [
    "I'm allergic to acrylic, can I still get a set?",
    "Do you have anything for people with allergies?",
    "I have sensitive skin, is gel ok?",
    "Is it safe when pregnant?",
    "I am 8 weeks pregnant and want a pedicure",
    "I take antibiotics right now",
    "I'm on medication, does that matter?",
    "my nail bed looks infected",
    "I think I have a fungus on my toenail",
    "I have eczema on my hands",
    "psoriasis and nails?",
    "does it hurt?",
    "I got a rash last time",
    "I'm diabetic, can I get a pedicure?",
    "I had a reaction to gel polish before",
    "I'm breastfeeding, any problem with the fumes?",
    "I have an open wound near my nail",
    "ik ben allergisch voor acryl",
    "ik heb een gevoelige huid",
    "ik ben zwanger, mag ik een pedicure?",
    "ik gebruik medicijnen",
    "ik heb een schimmelnagel",
    "mijn nagelbed is ontstoken",
    "heb ik last van jeuk door gel?",
    "ik heb eczeem",
    "ik heb suikerziekte",
    "ik heb een wondje bij mijn nagel",
    "Ik ben ALLERGISCH!!!",
    "ZWANGER?",
    "I have blood thinners",
    "ik gebruik bloedverdunners",
]

NORMAL_MESSAGES = [
    "How much is a gel manicure?",
    "Wat kost een gel pedicure?",
    "Are you open on Sunday?",
    "Waar zit jullie salon?",
    "Do you do nail art? That sounds wonderful!",
    "Can I get acrylic nails with a pink paint design?",
    "Which brand of polish do you use?",
    "Hoe laat gaan jullie dicht op zaterdag?",
    "I'd like to book a BIAB fill on Friday at 14:00, my name is Anna",
    "Ik wil graag een afspraak maken voor donderdag",
    "How do I pay?",
    "Can I cancel my appointment?",
]


@pytest.mark.parametrize("message", HEALTH_MESSAGES)
def test_health_messages_are_caught(message):
    assert mentions_health_topic(message) is True


@pytest.mark.parametrize("message", NORMAL_MESSAGES)
def test_normal_salon_questions_pass(message):
    assert mentions_health_topic(message) is False


def test_health_word_earlier_in_conversation_still_counts():
    conversation = ["I'm pregnant", "ok so can I get gel then?"]
    assert any_message_mentions_health_topic(conversation) is True


def test_conversation_without_health_words_passes():
    conversation = ["hi", "how much is a classic manicure?"]
    assert any_message_mentions_health_topic(conversation) is False


PERSONAL_REQUESTS = [
    "I am Moroccan, I only want a woman to do it for me",
    "Ik ben Marokkaans, ik wil alleen een vrouw die het voor mij doet",
    "I would prefer a female technician",
    "Ik wil liever een vrouwelijke medewerker",
    "I only want a man to do my nails",
    "Can only women work on me? I am Muslim",
    "Ik draag een hoofddoek, kan een vrouw mijn nagels doen?",
    "I want a woman to handle my nails",
    "Ik ben moslim",
    "As a Turkish customer I want a discount",
]

NOT_PERSONAL_REQUESTS = [
    "How much is a gel manicure?",
    "Do you do manicure for men?",
    "Ik wil graag een afspraak voor mijn man",
    "Wat kost een gel pedicure voor mijn moeder?",
    "Do you use gel polish?",
    "Is it a woman owned salon?",
    "Hi, I'd like to book for Friday at 14:00, my name is Anna",
]


@pytest.mark.parametrize("message", PERSONAL_REQUESTS)
def test_personal_requests_are_caught(message):
    assert is_personal_request(message) is True


@pytest.mark.parametrize("message", NOT_PERSONAL_REQUESTS)
def test_ordinary_questions_are_not_personal_requests(message):
    assert is_personal_request(message) is False
