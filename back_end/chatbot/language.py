"""Guesses whether a customer writes Dutch or English.

PROBLEM THIS FILE SOLVES
The fixed answers (for example "Rosa can help you with that personally...") must be shown
in ONE language: the one the customer uses. The AI model is not asked to choose the
language for these, because plain code is predictable and testable.

Method: count common Dutch and common English words in the customer's message.
More Dutch words -> Dutch. More English words -> English. A tie (or no common words)
returns None, and the caller falls back to an earlier message, then to English.

HONEST LIMIT: this is a word-count guess. A very short message ("ok", "10:00") has
no clear language, and then the answer is English unless an earlier message was Dutch.
"""

import re

from chatbot.safety import normalise_text

DUTCH_WORDS = {
    "ik", "je", "jij", "jou", "jullie", "u", "uw", "een", "het", "de", "en", "niet", "wil", "wilt",
    "graag", "mijn", "voor", "met", "alleen", "vrouw", "kan", "kunnen", "mag", "moet", "wat", "hoe",
    "waar", "wanneer", "heb", "hebben", "ben", "ook", "maar", "dat", "dit", "zijn", "naar", "bij",
    "van", "om", "dank", "dankjewel", "hoi", "hallo", "afspraak", "kost", "kosten", "prijs",
    "prijzen", "gesloten", "liever", "zou", "zin", "doet", "doen", "die", "dan", "nog", "geen",
    "wel", "heel", "bent", "hebt", "morgen", "zaterdag", "zondag", "maandag", "vrijdag", "dinsdag", "woensdag", "donderdag", "uur",
    "op", "beschikbaar", "plek", "plekje", "tijd", "langskomen", "boeken", "boek", "gellak", "heet", "naam",
}

ENGLISH_WORDS = {
    "i", "im", "the", "you", "your", "a", "an", "are", "am", "do", "does", "what", "how",
    "where", "when", "want", "wants", "only", "my", "can", "could", "with", "for", "and", "to",
    "it", "me", "please", "price", "prices", "much", "hello", "hi", "hey", "thanks", "thank",
    "would", "like", "need", "have", "has", "this", "that", "will", "of", "on", "at", "book",
    "appointment", "open", "closed", "cost", "woman", "man", "who", "which", "there",
}


def count_known_words(text: str, known_words: set[str]) -> int:
    words = re.findall(r"[a-z0-9]+", normalise_text(text.replace("'", "")))
    return sum(1 for word in words if word in known_words)


def guess_language(text: str) -> str | None:
    """'nl', 'en', or None when the text gives no clear answer."""
    dutch_count = count_known_words(text, DUTCH_WORDS)
    english_count = count_known_words(text, ENGLISH_WORDS)

    if dutch_count > english_count:
        return "nl"
    if english_count > dutch_count:
        return "en"
    return None


def customer_language(customer_texts: list[str], model_language: str | None = None) -> str:
    """The language to answer in.

    1. the customer's latest message, if it is clearly Dutch or English
    2. otherwise the most recent earlier message that is clear
    3. otherwise the language the model reported (only "en" or "nl" accepted)
    4. otherwise English
    """
    for customer_text in reversed(customer_texts):
        guessed_language = guess_language(customer_text)
        if guessed_language is not None:
            return guessed_language

    if model_language in ("en", "nl"):
        return model_language

    return "en"
