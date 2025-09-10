from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.infrastructure.core.config import Settings

settings = Settings()

DATABASE_URL = f"postgresql://{settings.db_username}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_name}"

# Create the SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a SessionLocal class to manage database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a declarative base class for model definitions
Base = declarative_base()


def get_db():
    """Yields a database session and ensures it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
