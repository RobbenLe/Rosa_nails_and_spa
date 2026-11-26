"""Talks to the Anthropic API.

PROBLEM THIS FILE SOLVES
Keeps the one place that calls the paid AI service small and easy to find, with
a short timeout, a token cap and no retries (a retry would double the cost).
"""

from anthropic import Anthropic

from chatbot import settings
from chatbot.assistant import ChatMessage

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
    """Send the instructions and the recent conversation, return the model's text."""
    # The API wants the first message to come from the user.
    usable_messages = list(messages)
    while usable_messages and usable_messages[0].role != "user":
        usable_messages.pop(0)

    response = get_client().messages.create(
        model=settings.model_name(),
        max_tokens=settings.MAX_REPLY_TOKENS,
        system=instructions,
        messages=[{"role": message.role, "content": message.content} for message in usable_messages],
    )

    return "".join(block.text for block in response.content if block.type == "text")
