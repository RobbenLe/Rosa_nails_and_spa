"""Finds the name a customer says about themselves ("my name is Anna", "ik heet Anna").

PROBLEM THIS FILE SOLVES
1. The WhatsApp message to Rosa should contain the customer's name, so we need to read it.
2. A name is NOT sensitive. But some first names look like a religion ("Christian") or similar words,
   and the privacy filters must not treat the name as a personal detail. So the stated name is
   removed from the text before those filters look at it.

Only an explicit statement counts: "my name is X", "my name's X", "name: X", "ik heet X", "mijn naam is X".
"I am X" / "ik ben X" is NOT used, because that is also how people state nationality or religion.
"""

import re

STATED_NAME_PATTERN = re.compile(
    r"\b(?:my name is|my name's|my name:|name is|name:|ik heet|mijn naam is|mijn naam:|naam is|naam:)\s+"
    r"([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ'\-]{1,30})",
    re.IGNORECASE,
)


def find_stated_names(text: str) -> list[str]:
    """Names the customer stated, with the first letter in capitals ('anna' -> 'Anna')."""
    names = []
    for match in STATED_NAME_PATTERN.finditer(text):
        raw_name = match.group(1)
        names.append(raw_name[:1].upper() + raw_name[1:])
    return names


def remove_stated_names(text: str) -> str:
    """The text without the stated name: 'my name is Christian' -> 'my name is'."""
    return STATED_NAME_PATTERN.sub(lambda match: match.group(0).replace(match.group(1), " "), text)
