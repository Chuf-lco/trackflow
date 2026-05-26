from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timezone
import uuid
import json

from ..database import get_db
from ..models import (
    Shipment as PydanticShipment, 
    ShipmentStatus, 
    StatusTransition as PydanticTransition, 
    ShipmentCreate, 
    ShipmentUpdate
)
from ..models.shipment_orm import ShipmentORM, StatusTransitionORM
from ..models.converter import pydantic_to_orm, orm_to_pydantic
from ..auth import get_current_user  # Optional: for protected routes

router = APIRouter(prefix="/api/v1/shipments", tags=["shipments"])

# In-memory fallback for development
shipments_db = {}

@router.post("/", response_model=PydanticShipment, status_code=status.HTTP_201_CREATED)
def create_shipment(shipment: ShipmentCreate, db: Session = Depends(get_db)):
    """Create new shipment tracking record"""
    try:
        # Check if exists in DB
        existing = db.query(ShipmentORM).filter(ShipmentORM.id == shipment.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Shipment ID already exists")
        
        # Convert Pydantic → ORM and save
        orm_shipment = pydantic_to_orm(shipment)
        db.add(orm_shipment)
        db.commit()
        db.refresh(orm_shipment)
        return orm_to_pydantic(orm_shipment)
    except HTTPException:
        raise
    except Exception as e:
        # Fallback to in-memory for development
        if shipment.id in shipments_db:
            raise HTTPException(status_code=400, detail="Shipment ID already exists")
        shipments_db[shipment.id] = shipment
        return shipment

@router.get("/", response_model=List[PydanticShipment])
def list_shipments(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all shipments"""
    try:
        orm_shipments = db.query(ShipmentORM).offset(skip).limit(limit).all()
        return [orm_to_pydantic(s) for s in orm_shipments]
    except:
        # Fallback to in-memory
        return list(shipments_db.values())[skip:skip + limit]

@router.get("/{shipment_id}", response_model=PydanticShipment)
def get_shipment(shipment_id: str, db: Session = Depends(get_db)):
    """Get specific shipment with full history"""
    try:
        orm_shipment = db.query(ShipmentORM).filter(ShipmentORM.id == shipment_id).first()
        if not orm_shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return orm_to_pydantic(orm_shipment)
    except HTTPException:
        raise
    except:
        # Fallback to in-memory
        if shipment_id not in shipments_db:
            raise HTTPException(status_code=404, detail="Shipment not found")
        return shipments_db[shipment_id]

@router.post("/{shipment_id}/status", response_model=PydanticShipment)
def update_status(
    shipment_id: str, 
    transition: PydanticTransition, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Optional auth
):
    """Update shipment status (core workflow)"""
    try:
        orm_shipment = db.query(ShipmentORM).filter(ShipmentORM.id == shipment_id).first()
        if not orm_shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        
        # Add transition to history
        new_transition = StatusTransitionORM(
            id=str(uuid.uuid4()),
            shipment_id=shipment_id,
            timestamp=transition.timestamp,
            status=transition.status.value if hasattr(transition.status, 'value') else transition.status,
            actor=transition.actor,
            source_system=transition.source_system,
            geo_location=transition.geo_location,
            offline_synced=transition.offline_synced,
            exception_reason=transition.exception_reason,
            evidence_urls=json.dumps(transition.evidence_urls) if transition.evidence_urls else None
        )
        orm_shipment.status_history.append(new_transition)
        orm_shipment.current_status = transition.status.value if hasattr(transition.status, 'value') else transition.status
        orm_shipment.updated_at = datetime.now(timezone.utc)
        
        # Kenya-specific: Track demurrage
        if transition.status == ShipmentStatus.CUSTOMS_DECLARATION:
            orm_shipment.customs_declaration_date = transition.timestamp
        
        db.commit()
        db.refresh(orm_shipment)
        return orm_to_pydantic(orm_shipment)
    except HTTPException:
        raise
    except:
        # Fallback to in-memory
        if shipment_id not in shipments_db:
            raise HTTPException(status_code=404, detail="Shipment not found")
        shipment = shipments_db[shipment_id]
        shipment.status_history.append(transition)
        shipment.current_status = transition.status
        shipment.updated_at = datetime.now(timezone.utc)
        if transition.status == ShipmentStatus.CUSTOMS_DECLARATION:
            shipment.customs_declaration_date = transition.timestamp
        return shipment

@router.get("/{shipment_id}/demurrage")
def calculate_demurrage(shipment_id: str, db: Session = Depends(get_db)):
    """Calculate demurrage days and cost (Kenya-specific)"""
    # This endpoint is read-only, so we can use either source
    try:
        orm_shipment = db.query(ShipmentORM).filter(ShipmentORM.id == shipment_id).first()
        if not orm_shipment:
            raise HTTPException(status_code=404, detail="Shipment not found")
        shipment = orm_to_pydantic(orm_shipment)
    except:
        if shipment_id not in shipments_db:
            raise HTTPException(status_code=404, detail="Shipment not found")
        shipment = shipments_db[shipment_id]
    
    if not shipment.customs_declaration_date:
        return {"demurrage_days": 0, "estimated_cost_kes": 0}
    
    now_utc = datetime.now(timezone.utc)
    customs_date = shipment.customs_declaration_date
    if customs_date.tzinfo is None:
        customs_date = customs_date.replace(tzinfo=timezone.utc)
    
    delta = now_utc - customs_date
    days = delta.days
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