"""The two web addresses of the chatbot.

  GET  /api/chat/status  -> {"enabled": true/false}   the website asks this to decide whether to show the widget
  POST /api/chat         -> one answer for the conversation so far

PROBLEM THIS FILE SOLVES
Receives chat messages from the website, applies the kill switch and the limits,
and hands the conversation to assistant.py. Nothing is saved, and logs never contain message text.
"""

import logging

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from chatbot import settings
from chatbot.assistant import ChatMessage, answer_conversation, make_ask_rosa_answer
from chatbot.language import customer_language
from chatbot.model_client import call_anthropic_model
from chatbot.price_list import load_price_list
from chatbot.rate_limit import RateLimiter

logger = logging.getLogger("chatbot")

# Python's default logging hides INFO lines. This makes the outcome lines visible in the Vercel logs.
if not logger.handlers:
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter("%(levelname)s %(name)s %(message)s"))
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False

router = APIRouter()
rate_limiter = RateLimiter()


class IncomingMessage(BaseModel):
    role: str = Field(pattern="^(user|assistant)$")
    content: str = Field(min_length=1, max_length=settings.MAX_CUSTOMER_MESSAGE_CHARACTERS)


class ChatRequest(BaseModel):
    messages: list[IncomingMessage] = Field(min_length=1, max_length=settings.MAX_MESSAGES_IN_CONVERSATION)


def find_visitor_id(request: Request) -> str:
    """Vercel puts the visitor's address first in x-forwarded-for."""
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.get("/api/chat/status")
def chat_status():
    return {"enabled": settings.chatbot_is_configured()}


@router.post("/api/chat")
def chat(body: ChatRequest, request: Request):
    # Step 1: kill switch and configuration
    if not settings.chatbot_is_configured():
        raise HTTPException(status_code=503, detail="Chat is switched off")

    # Step 2: the last message must come from the customer
    if body.messages[-1].role != "user":
        raise HTTPException(status_code=422, detail="Last message must be from the user")

    # Step 3: rate limits
    if not rate_limiter.allow_visitor_message(find_visitor_id(request)):
        raise HTTPException(status_code=429, detail="Too many messages, please try again later")

    messages = [ChatMessage(role=message.role, content=message.content) for message in body.messages]

    if not rate_limiter.allow_model_call():
        customer_texts = [message.content for message in messages if message.role == "user"]
        answer = make_ask_rosa_answer(customer_language(customer_texts), "fallback")
        return build_response(answer)

    # Step 4: answer
    answer = answer_conversation(messages, call_anthropic_model, load_price_list)

    # Step 5: log the outcome type and the reason code only, never any customer or reply text
    logger.info("chat outcome=%s language=%s reason=%s", answer.outcome, answer.language, answer.reason or "-")

    return build_response(answer)


def build_response(answer) -> dict:
    return {
        "reply": answer.reply,
        "whatsapp": answer.show_whatsapp_button,
        "booking": answer.booking,
        "button": answer.button,        # "ask" or "book": which WhatsApp button label the website shows
        "language": answer.language,    # "en" or "nl": the language of the reply
    }
