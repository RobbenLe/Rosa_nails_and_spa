"""Reads the live price list for the chatbot, using the READ-ONLY database user.

PROBLEM THIS FILE SOLVES
Prices must come from the real database, never from the model's memory. And the chatbot
must not be able to change or read anything else, so it uses its own database user
(CHATBOT_DATABASE_URL) that can only SELECT from the `services` table.

The price is stored in cents in the column `price` of table `services` (see models.py).
Only services with is_active = true are shown, the same as the website's price list.
"""

from dataclasses import dataclass

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from chatbot import settings

_read_only_engine: Engine | None = None


@dataclass
class PriceListEntry:
    category: str
    name: str
    variant: str
    duration_minutes: int
    price_cents: int


def get_read_only_engine() -> Engine:
    """Create the connection once per server instance, then reuse it."""
    global _read_only_engine

    if _read_only_engine is None:
        database_url = settings.chatbot_database_url()

        for prefix in ("postgres://", "postgresql://"):
            if database_url.startswith(prefix):
                database_url = "postgresql+psycopg://" + database_url.removeprefix(prefix)

        if database_url.startswith("sqlite"):
            _read_only_engine = create_engine(database_url, connect_args={"check_same_thread": False})
        else:
            _read_only_engine = create_engine(database_url, pool_pre_ping=True, pool_size=1, max_overflow=1)

    return _read_only_engine


def load_price_list() -> list[PriceListEntry]:
    """Every active service with its price. Raises an error if the database cannot be read."""
    query = text(
        "SELECT category, name, variant, duration_minutes, price "
        "FROM services WHERE is_active = :is_active ORDER BY id"
    )

    with get_read_only_engine().connect() as connection:
        rows = connection.execute(query, {"is_active": True}).fetchall()

    return [
        PriceListEntry(
            category=row.category or "",
            name=row.name,
            variant=row.variant or "",
            duration_minutes=row.duration_minutes,
            price_cents=row.price,
        )
        for row in rows
    ]


def format_euros(price_cents: int) -> str:
    """2500 -> '€25', 2550 -> '€25.50'."""
    euros, cents = divmod(price_cents, 100)
    if cents == 0:
        return f"€{euros}"
    return f"€{euros}.{cents:02d}"


def format_price_list_for_prompt(price_list: list[PriceListEntry]) -> str:
    """The price list as plain text lines that are pasted into the model's instructions."""
    lines = []
    for entry in price_list:
        option = f" ({entry.variant})" if entry.variant else ""
        lines.append(
            f"- [{entry.category}] {entry.name}{option}: {format_euros(entry.price_cents)}, "
            f"{entry.duration_minutes} minutes"
        )
    return "\n".join(lines)


def allowed_price_amounts_in_euros(price_list: list[PriceListEntry]) -> set[float]:
    """Every price the bot is allowed to mention, in euros."""
    return {entry.price_cents / 100 for entry in price_list}
