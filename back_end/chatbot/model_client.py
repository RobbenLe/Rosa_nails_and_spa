"""Talks to the Anthropic API.

PROBLEM THIS FILE SOLVES
1. Keeps the one place that calls the paid AI service small and easy to find, with
   a short timeout, a token cap and no retries (a retry would double the cost).
2. The production logs showed most failures were "model answer is not valid JSON": the model wrote its
   answer as free text that sometimes was not valid JSON (loose quotes, extra text, cut-off).
   Now the model must answer by calling a tool with a fixed set of fields. The API hands us the
   fields as ready data, so there is no JSON text to get wrong.
"""

import json

from anthropic import Anthropic

from chatbot import settings
from chatbot.assistant import ChatMessage

REPLY_TOOL_NAME = "reply_to_customer"

REPLY_TOOL = {
    "name": REPLY_TOOL_NAME,
    "description": "Give the answer for the customer. Call this tool exactly once.",
    "input_schema": {
        "type": "object",
        "properties": {
            "reply": {"type": "string", "description": "Text for the customer. Empty when booking_intent or out_of_scope is true."},
            "language": {"type": "string", "enum": ["en", "nl"], "description": "Language of the customer's last message."},
            "out_of_scope": {"type": "boolean", "description": "True when the bot may not answer this."},
            "booking_intent": {"type": "boolean", "description": "True when the customer wants an appointment or asks about a free time."},
        },
        "required": ["reply", "language", "out_of_scope", "booking_intent"],
    },
}

_client: Anthropic | None = None


def get_client() -> Anthropic:
    """Create the client once per server instance."""
    global _client
    if _client is None:
        _client = Anthropic(
            api_key=settings.anthropic_api_key(),
            timeout=settings.MODEL_TIMEOUT_SECONDS,
            max_retries=0,
        )
    return _client


def call_anthropic_model(instructions: str, messages: list[ChatMessage]) -> str:
    """Send the instructions and the recent conversation. Returns the answer fields as a JSON text
    (written by us from the tool call, so it is always valid), or the plain text if no tool call came back."""
    # The API wants the first message to come from the user.
    usable_messages = list(messages)
    while usable_messages and usable_messages[0].role != "user":
        usable_messages.pop(0)

    response = get_client().messages.create(
        model=settings.model_name(),
        max_tokens=settings.MAX_REPLY_TOKENS,
        system=instructions,
        messages=[{"role": message.role, "content": message.content} for message in usable_messages],
        tools=[REPLY_TOOL],
        tool_choice={"type": "tool", "name": REPLY_TOOL_NAME},
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == REPLY_TOOL_NAME:
            return json.dumps(block.input)

    return "".join(block.text for block in response.content if block.type == "text")
