#This  file is created to CONNECT TP THE DATABASE

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(bind=engine, autoflush=False)

Base = declarative_base()

def get_db():
    """Give each request its own database session, and always close it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()