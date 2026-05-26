# backend/app/models/shipment_orm.py
from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime, timezone
from enum import Enum as PyEnum
import json

Base = declarative_base()

# Status Enum (mirror of Pydantic ShipmentStatus)
class ShipmentStatusEnum(str, PyEnum):
    VESSEL_ARRIVAL = "vessel_arrival"
    CUSTOMS_DECLARATION = "customs_declaration"
    PHYSICAL_VERIFICATION = "physical_verification"
    INLAND_TRANSIT = "inland_transit"
    DELIVERED = "delivered"

# StatusTransition ORM Model
class StatusTransitionORM(Base):
    __tablename__ = "status_transitions"
    
    id = Column(String, primary_key=True, index=True)
    shipment_id = Column(String, ForeignKey("shipments.id"), index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String)  # Store enum as string
    actor = Column(String)
    source_system = Column(String)
    geo_location = Column(String, nullable=True)
    offline_synced = Column(Boolean, default=False)
    exception_reason = Column(Text, nullable=True)
    evidence_urls = Column(Text, nullable=True)  # Store as JSON string
    
    # Relationship
    shipment = relationship("ShipmentORM", back_populates="status_history")

# Shipment ORM Model
class ShipmentORM(Base):
    __tablename__ = "shipments"
    
    id = Column(String, primary_key=True, index=True)
    bl_number = Column(String, unique=True, index=True, nullable=False)
    container_number = Column(String, nullable=False)
    current_status = Column(String, default=ShipmentStatusEnum.VESSEL_ARRIVAL.value)
    manifest_date = Column(DateTime, nullable=False)
    payment_status = Column(String, default="pending")
    gps_tracking_active = Column(Boolean, default=False)
    demurrage_days = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    customs_declaration_date = Column(DateTime, nullable=True)
    
    # Relationships
    status_history = relationship("StatusTransitionORM", back_populates="shipment", cascade="all, delete-orphan")