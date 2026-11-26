"""Tests for the reply checker and the rate limiter."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from chatbot import settings
from chatbot.answer_check import check_reply
from chatbot.price_list import PriceListEntry, allowed_price_amounts_in_euros, format_euros
from chatbot.rate_limit import RateLimiter

PRICE_LIST = [
    PriceListEntry("Manicure & Pedicure", "Gel Manicure", "", 60, 2500),
    PriceListEntry("Manicure & Pedicure", "Classic Pedicure", "", 40, 4000),
    PriceListEntry("Extras", "Nail art", "per nail", 10, 550),
]
ALLOWED = allowed_price_amounts_in_euros(PRICE_LIST)


@pytest.mark.parametrize("reply", [
    "A gel manicure is €25 and takes 60 minutes.",
    "Gel manicure: € 25,00. Pedicure 40 euro.",
    "Nail art is €5.50 per nail.",
    "Een gel manicure kost 25 € en duurt 60 minuten.",
    "Message Rosa on WhatsApp +31 6 33 42 67 98.",
    "Call 06 33 42 67 98 to book.",
    "We are open Monday to Saturday from 10:00 to 18:00.",
])
def test_good_replies_are_accepted(reply):
    assert check_reply(reply, ALLOWED).is_acceptable is True


@pytest.mark.parametrize("reply", [
    "A gel manicure is €1.",
    "A gel manicure is €26.",
    "That costs 30 euro.",
    "Pedicure is €40 and a gel manicure is €20.",
    "Book at https://example.com/rosa",
    "Mail us at rosa@example.com",
    "Visit www.rosa-nails.nl",
    "Call +31 6 11 22 33 44 for a discount.",
    "",
    "   ",
    "x" * 1000,
])
def test_bad_replies_are_rejected(reply):
    assert check_reply(reply, ALLOWED).is_acceptable is False


def test_format_euros():
    assert format_euros(2500) == "€25"
    assert format_euros(550) == "€5.50"
    assert format_euros(0) == "€0"


def test_visitor_is_blocked_after_the_limit_and_freed_after_the_window():
    limiter = RateLimiter()
    start = 1_000_000.0

    for message_number in range(settings.MAX_MESSAGES_PER_VISITOR):
        assert limiter.allow_visitor_message("visitor-a", now=start + message_number) is True

    assert limiter.allow_visitor_message("visitor-a", now=start + 100) is False
    assert limiter.allow_visitor_message("visitor-b", now=start + 100) is True

    after_window = start + settings.VISITOR_WINDOW_SECONDS + 100
    assert limiter.allow_visitor_message("visitor-a", now=after_window) is True


def test_model_call_cap_per_hour():
    limiter = RateLimiter()
    start = 2_000_000.0

    for call_number in range(settings.MAX_MODEL_CALLS_PER_HOUR_PER_INSTANCE):
        assert limiter.allow_model_call(now=start + call_number) is True

    assert limiter.allow_model_call(now=start + 1000) is False
    assert limiter.allow_model_call(now=start + 3700) is True


# ------------------------------------------------------------------ schedule claims
from chatbot.answer_check import SCHEDULE_STANDARD_REPLY, claims_schedule_is_free


@pytest.mark.parametrize("reply", [
    "Saturday 28 November at 10:00 works!",
    "Saturday 28 November at 10:00 works",
    "That time is available.",
    "Yes, we have availability on Friday.",
    "Your appointment is booked.",
    "You're booked for Friday 14:00.",
    "Your appointment is confirmed.",
    "That's fine, see you then!",
    "That’s fine!",
    "Sounds good, no problem.",
    "Friday at 14:00 is free.",
    "Zaterdag 10:00 kan prima.",
    "Dat kan!",
    "Die tijd is beschikbaar.",
    "Je afspraak is geboekt.",
    "Je afspraak is bevestigd.",
    "Dat past prima, tot dan!",
    "Geen probleem, zaterdag 10:00 is vrij.",
])
def test_replies_that_claim_a_free_or_booked_time_are_caught(reply):
    assert claims_schedule_is_free(reply) is True


@pytest.mark.parametrize("reply", [
    "That time is within our opening hours. Rosa will check her schedule and confirm on WhatsApp.",
    "Dat valt binnen onze openingstijden. Rosa kijkt in haar agenda en bevestigt via WhatsApp.",
    "We are closed on Sunday, so 19:00 is outside our opening hours. Could you pick another day?",
    "Op zondag zijn we gesloten. Kies je een andere dag?",
    "Which service would you like, and what is your name?",
    "Waar kan ik betalen? Je kunt contant of met PIN betalen.",
    "Rosa confirms your appointment personally on WhatsApp.",
    "A gel manicure is €25 and takes 60 minutes.",
    SCHEDULE_STANDARD_REPLY,
])
def test_normal_replies_are_not_flagged_as_schedule_claims(reply):
    assert claims_schedule_is_free(reply) is False


def test_approved_faq_answers_are_not_flagged_as_schedule_claims():
    from chatbot.salon_facts import FREQUENTLY_ASKED_QUESTIONS

    for _question, english_answer, dutch_answer in FREQUENTLY_ASKED_QUESTIONS:
        assert claims_schedule_is_free(english_answer) is False, english_answer
        assert claims_schedule_is_free(dutch_answer) is False, dutch_answer
