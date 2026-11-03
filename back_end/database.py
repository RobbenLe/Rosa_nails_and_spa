#This  file is created to CONNECT TP THE DATABASE

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

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