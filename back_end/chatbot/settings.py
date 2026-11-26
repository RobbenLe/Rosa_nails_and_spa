"""All chatbot settings in one place, read from environment variables.

PROBLEM THIS FILE SOLVES
Limits and switches must be easy to find and change without touching logic.
Secrets (API key, database password) only ever come from the environment, never from the code.

Environment variables:
  CHATBOT_ENABLED         "true" to turn the chatbot on. Anything else (or missing) = OFF. This is the kill switch.
  ANTHROPIC_API_KEY       key for the AI service
  CHATBOT_DATABASE_URL    connection string of the READ-ONLY database user (see docs/01-design-v1.md)
  CHATBOT_MODEL           optional, overrides the default model
"""

import os

DEFAULT_MODEL = "claude-haiku-5-5"

# --- limits that protect the monthly bill (the provider's €20 spend limit is the final stop)
MAX_CUSTOMER_MESSAGE_CHARACTERS = 500
MAX_MESSAGES_IN_CONVERSATION = 6
MAX_REPLY_TOKENS = 400
MODEL_TIMEOUT_SECONDS = 15

# --- simple rate limit (best effort: every serverless instance counts on its own)
MAX_MESSAGES_PER_VISITOR = 20
VISITOR_WINDOW_SECONDS = 10 * 60
MAX_MODEL_CALLS_PER_HOUR_PER_INSTANCE = 200


def chatbot_is_enabled() -> bool:
    """Kill switch. Read at every request, so a new deploy with the variable changed turns it off."""
    return os.getenv("CHATBOT_ENABLED", "").strip().lower() == "true"


def anthropic_api_key() -> str:
    return os.getenv("ANTHROPIC_API_KEY", "").strip()


def chatbot_database_url() -> str:
    return os.getenv("CHATBOT_DATABASE_URL", "").strip()


def model_name() -> str:
    return os.getenv("CHATBOT_MODEL", "").strip() or DEFAULT_MODEL


def chatbot_is_configured() -> bool:
    """On AND has everything it needs. Missing key or database means the widget stays hidden."""
    return chatbot_is_enabled() and bool(anthropic_api_key()) and bool(chatbot_database_url())
