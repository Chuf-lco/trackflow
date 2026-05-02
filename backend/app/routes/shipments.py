from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..models import Shipment, ShipmentStatus, StatusTransition
from datetime import datetime, timezone

# Initialize router with prefix and tags
router = APIRouter(prefix="/api/v1/shipments", tags=["shipments"])

# In-memory storage (we'll add DB in Phase 2)
shipments_db = {}

@router.post("/", response_model=Shipment)
def create_shipment(shipment: Shipment):
    """Create new shipment tracking record"""
    shipments_db[shipment.id] = shipment
    return shipment

@router.get("/", response_model=List[Shipment])
def list_shipments():
    """List all shipments"""
    return list(shipments_db.values())

@router.get("/{shipment_id}", response_model=Shipment)
def get_shipment(shipment_id: str):
    """Get specific shipment with full history"""
    if shipment_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return shipments_db[shipment_id]

@router.post("/{shipment_id}/status")
def update_status(shipment_id: str, transition: StatusTransition):
    """Update shipment status (core workflow)"""
    if shipment_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipment = shipments_db[shipment_id]
    shipment.status_history.append(transition)
    shipment.current_status = transition.status
    shipment.updated_at = datetime.now(timezone.utc)
    
    # Kenya-specific: Track demurrage from customs declaration
    if transition.status == ShipmentStatus.CUSTOMS_DECLARATION:
        shipment.customs_declaration_date = transition.timestamp
    
    return shipment

@router.get("/{shipment_id}/demurrage")
def calculate_demurrage(shipment_id: str):
    """Calculate demurrage days and cost (Kenya-specific)"""
    if shipment_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipment = shipments_db[shipment_id]
    if not shipment.customs_declaration_date:
        return {"demurrage_days": 0, "estimated_cost_kes": 0}
    
    # Use timezone-aware datetime (UTC)
    now_utc = datetime.now(timezone.utc)
    
    # Ensure customs_declaration_date is timezone-aware
    customs_date = shipment.customs_declaration_date
    if customs_date.tzinfo is None:
        # If naive, assume it's UTC
        customs_date = customs_date.replace(tzinfo=timezone.utc)
    
    # Calculate days difference
    delta = now_utc - customs_date
    days = delta.days
    
    # KPA demurrage rates (simplified)
    rate_per_day = 5000  # KES
    free_days = 7
    chargeable_days = max(0, days - free_days)
    cost = chargeable_days * rate_per_day
    
    return {
        "demurrage_days": days,
        "free_days_remaining": max(0, free_days - days),
        "estimated_cost_kes": cost,
        "alert": days > free_days,
        "calculated_at_utc": now_utc.isoformat()
    }