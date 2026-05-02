from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ShipmentStatus(str, Enum):
    VESSEL_ARRIVAL = "vessel_arrival"
    CUSTOMS_DECLARATION = "customs_declaration"
    PHYSICAL_VERIFICATION = "physical_verification"
    INLAND_TRANSIT = "inland_transit"
    DELIVERED = "delivered"

class StatusTransition(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    status: ShipmentStatus
    geo_location: Optional[str] = None
    actor: str
    source_system: str
    evidence_urls: Optional[List[str]] = []
    offline_synced: bool = False
    exception_reason: Optional[str] = None

class Shipment(BaseModel):
    id: str
    bl_number: str
    container_number: str
    current_status: ShipmentStatus
    status_history: List[StatusTransition] = []
    
    # Explicitly mark as nullable with None defaults
    manifest_date: Optional[datetime] = None
    customs_declaration_date: Optional[datetime] = None
    payment_status: str = "pending"
    kro_number: Optional[str] = None
    gps_tracking_active: bool = False
    demurrage_days: int = 0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)