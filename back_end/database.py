#This  file is created to CONNECT TP THE DATABASE

import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

# Online (Vercel) this is the Postgres URL from the Neon integration.
# On your own computer it is unset, so a local SQLite file is used.
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///database.db"

# Neon gives "postgres://" or "postgresql://"; tell SQLAlchemy to use the psycopg 3 driver.
for prefix in ("postgres://", "postgresql://"):
    if DATABASE_URL.startswith(prefix):
        DATABASE_URL = "postgresql+psycopg://" + DATABASE_URL.removeprefix(prefix)

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # pool_pre_ping: serverless functions sleep between requests, so check the connection is still alive.
    engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=1, max_overflow=2)

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()

def create_tables():
    """
    Create missing tables, then add any columns that were added to a model
    after its table already existed. (create_all alone never alters a table.)
    """
    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    with engine.begin() as connection:
        for table in Base.metadata.sorted_tables:
            existing = {column["name"] for column in inspector.get_columns(table.name)}
            for column in table.columns:
                if column.name in existing:
                    continue
                column_type = column.type.compile(dialect=engine.dialect)
                default = column.server_default.arg if column.server_default is not None else None
                default_sql = f" NOT NULL DEFAULT '{default}'" if default is not None else ""
                connection.execute(
                    text(f'ALTER TABLE {table.name} ADD COLUMN {column.name} {column_type}{default_sql}')
                )

def get_db():
    """Give each request its own database session, and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()