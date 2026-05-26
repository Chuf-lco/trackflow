from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings

# Use PostgreSQL from environment
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from .models.user import Base  # Import all models to register with Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()