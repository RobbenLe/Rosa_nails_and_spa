"""The chatbot's salon facts must match the website's (front_end/src/data/salon.ts)."""

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import config
from chatbot import salon_facts

SALON_TS_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "front_end", "src", "data", "salon.ts"
)

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def read_salon_ts() -> str:
    with open(SALON_TS_PATH, encoding="utf-8") as salon_file:
        return salon_file.read()


def test_phone_matches_website():
    assert f"phone: '{salon_facts.SALON_PHONE_DISPLAY}'" in read_salon_ts()
    assert f"whatsapp: '{salon_facts.SALON_PHONE_DISPLAY}'" in read_salon_ts()


def test_address_matches_website():
    website_text = read_salon_ts()
    assert f"address: '{salon_facts.SALON_ADDRESS}'" in website_text
    assert f"city: '{salon_facts.SALON_CITY}'" in website_text


def test_opening_hours_match_website():
    website_text = read_salon_ts()

    for weekday_number, weekday_name in enumerate(WEEKDAY_NAMES):
        hours = config.BUSINESS_HOURS.get(weekday_number)
        pattern = re.compile(r"day: '" + weekday_name + r"',\s*open: ([^,]+), close: ([^ }]+)")
        match = pattern.search(website_text)
        assert match is not None, f"{weekday_name} not found in salon.ts"

        website_open = match.group(1).strip("' ")
        website_close = match.group(2).strip("' ")

        if hours is None:
            assert website_open == "null" and website_close == "null"
        else:
            assert (website_open, website_close) == hours


def test_faq_hours_sentence_matches_config():
    # The FAQ says "Monday to Saturday 10:00-18:00, closed on Sunday".
    assert all(config.BUSINESS_HOURS[day] == ("10:00", "18:00") for day in range(6))
    assert config.BUSINESS_HOURS[6] is None


def test_faq_notice_periods_match_config():
    faq_text = salon_facts.format_faq_for_prompt()
    assert f"at least {config.MIN_BOOKING_NOTICE_HOURS} hours ahead" in faq_text
    assert f"at least {config.MIN_CANCLE_NOTICE_HOURS} hours before" in faq_text
