"""Simple rate limit to stop casual abuse.

PROBLEM THIS FILE SOLVES
Without a limit one visitor (or a script) could send thousands of messages and run up the AI bill.

HONEST LIMIT OF THIS DESIGN: the counters live in the memory of one server instance.
Vercel may run several instances, and each counts on its own, so this is best effort.
The real hard stop on cost is the spend limit set in the Anthropic console.
"""

import threading
import time

from chatbot import settings


class RateLimiter:
    def __init__(self):
        self._lock = threading.Lock()
        self._visitor_message_times: dict[str, list[float]] = {}
        self._model_call_times: list[float] = []

    def allow_visitor_message(self, visitor_id: str, now: float | None = None) -> bool:
        """True if this visitor is under the limit; records the message when allowed."""
        current_time = now if now is not None else time.time()
        window_start = current_time - settings.VISITOR_WINDOW_SECONDS

        with self._lock:
            recent_times = [t for t in self._visitor_message_times.get(visitor_id, []) if t > window_start]

            if len(recent_times) >= settings.MAX_MESSAGES_PER_VISITOR:
                self._visitor_message_times[visitor_id] = recent_times
                return False

            recent_times.append(current_time)
            self._visitor_message_times[visitor_id] = recent_times
            self._forget_idle_visitors(window_start)
            return True

    def allow_model_call(self, now: float | None = None) -> bool:
        """True if this instance is under its hourly cap of model calls; records the call when allowed."""
        current_time = now if now is not None else time.time()
        hour_start = current_time - 3600

        with self._lock:
            self._model_call_times = [t for t in self._model_call_times if t > hour_start]

            if len(self._model_call_times) >= settings.MAX_MODEL_CALLS_PER_HOUR_PER_INSTANCE:
                return False

            self._model_call_times.append(current_time)
            return True

    def _forget_idle_visitors(self, window_start: float) -> None:
        """Keep memory small: drop visitors with no recent messages."""
        idle_visitors = [
            visitor_id
            for visitor_id, times in self._visitor_message_times.items()
            if not times or times[-1] <= window_start
        ]
        for visitor_id in idle_visitors:
            del self._visitor_message_times[visitor_id]
