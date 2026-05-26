# Pydantic Models (for API requests/responses) - KEEP THESE
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum
from typing import List, Optional

# Status Enum
class ShipmentStatus(str, Enum):
    VESSEL_ARRIVAL = "vessel_arrival"
    CUSTOMS_DECLARATION = "customs_declaration"
    PHYSICAL_VERIFICATION = "physical_verification"
    INLAND_TRANSIT = "inland_transit"
    DELIVERED = "delivered"

# Status Transition Model
class StatusTransition(BaseModel):
    timestamp: datetime
    status: ShipmentStatus
    actor: str
    source_system: str
    geo_location: Optional[str] = None
    offline_synced: bool = False
    exception_reason: Optional[str] = None
    evidence_urls: List[str] = Field(default_factory=list)

# Shipment Model (Pydantic for API)
class Shipment(BaseModel):
    id: str
    bl_number: str
    container_number: str
    current_status: ShipmentStatus
    status_history: List[StatusTransition] = Field(default_factory=list)
    manifest_date: datetime
    payment_status: str = "pending"
    gps_tracking_active: bool = False
    demurrage_days: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    customs_declaration_date: Optional[datetime] = None
    
    class Config:
        from_attributes = True  # Allows ORM mode

# Request/Response Models
class ShipmentCreate(BaseModel):
    id: str
    bl_number: str
    container_number: str
    current_status: ShipmentStatus
    manifest_date: datetime
    payment_status: str = "pending"
    gps_tracking_active: bool = False
    demurrage_days: int = 0

class ShipmentUpdate(BaseModel):
    current_status: Optional[ShipmentStatus] = None
    payment_status: Optional[str] = None
    gps_tracking_active: Optional[bool] = None

# === NEW: SQLAlchemy User Model (for Auth) ===
# This is separate from Pydantic models
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="customer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)