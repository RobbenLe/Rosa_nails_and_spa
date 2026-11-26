"""Tests for the Dutch/English guess used to pick the language of fixed answers."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from chatbot.language import customer_language, guess_language


@pytest.mark.parametrize("text, expected", [
    ("I am Moroccan, I only want a woman to do it for me", "en"),
    ("Ik ben Marokkaans, ik wil alleen een vrouw die het voor mij doet", "nl"),
    ("How much is a gel manicure?", "en"),
    ("Wat kost een gel manicure?", "nl"),
    ("Hoi, zijn jullie open op zaterdag?", "nl"),
    ("Hello, are you open on Saturday?", "en"),
    ("Kan ik met pin betalen?", "nl"),
])
def test_clear_messages_are_recognised(text, expected):
    assert guess_language(text) == expected


def test_unclear_message_returns_none():
    assert guess_language("10:00") is None
    assert guess_language("ok") is None


def test_unclear_latest_message_uses_an_earlier_one():
    assert customer_language(["Wat kost een gel pedicure?", "ok"]) == "nl"


def test_model_language_is_used_when_nothing_is_clear_and_english_is_the_last_resort():
    assert customer_language(["10:00"], model_language="nl") == "nl"
    assert customer_language(["10:00"], model_language="fr") == "en"
    assert customer_language(["10:00"]) == "en"
