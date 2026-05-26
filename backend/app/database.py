from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

# Use PostgreSQL from environment
SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

from .models.shipment_orm import Base  # Import all models to register with Base

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()