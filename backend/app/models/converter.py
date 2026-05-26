# backend/app/models/converter.py
from .shipment_orm import ShipmentORM, StatusTransitionORM, ShipmentStatusEnum
from . import Shipment as PydanticShipment, StatusTransition as PydanticTransition, ShipmentStatus
import uuid
from datetime import datetime, timezone
import json

def pydantic_to_orm(pydantic_shipment: PydanticShipment) -> ShipmentORM:
    """Convert Pydantic Shipment to SQLAlchemy ORM"""
    return ShipmentORM(
        id=pydantic_shipment.id,
        bl_number=pydantic_shipment.bl_number,
        container_number=pydantic_shipment.container_number,
        current_status=pydantic_shipment.current_status.value if hasattr(pydantic_shipment.current_status, 'value') else pydantic_shipment.current_status,
        manifest_date=pydantic_shipment.manifest_date,
        payment_status=pydantic_shipment.payment_status,
        gps_tracking_active=pydantic_shipment.gps_tracking_active,
        demurrage_days=pydantic_shipment.demurrage_days,
        customs_declaration_date=pydantic_shipment.customs_declaration_date,
        # Convert status_history
        status_history=[
            StatusTransitionORM(
                id=str(uuid.uuid4()),
                timestamp=t.timestamp,
                status=t.status.value if hasattr(t.status, 'value') else t.status,
                actor=t.actor,
                source_system=t.source_system,
                geo_location=t.geo_location,
                offline_synced=t.offline_synced,
                exception_reason=t.exception_reason,
                evidence_urls=json.dumps(t.evidence_urls) if t.evidence_urls else None
            )
            for t in pydantic_shipment.status_history
        ]
    )

def orm_to_pydantic(orm_shipment: ShipmentORM) -> PydanticShipment:
    """Convert SQLAlchemy ORM to Pydantic Shipment"""
    return PydanticShipment(
        id=orm_shipment.id,
        bl_number=orm_shipment.bl_number,
        container_number=orm_shipment.container_number,
        current_status=ShipmentStatus(orm_shipment.current_status),
        manifest_date=orm_shipment.manifest_date,
        payment_status=orm_shipment.payment_status,
        gps_tracking_active=orm_shipment.gps_tracking_active,
        demurrage_days=orm_shipment.demurrage_days,
        created_at=orm_shipment.created_at,
        updated_at=orm_shipment.updated_at,
        customs_declaration_date=orm_shipment.customs_declaration_date,
        status_history=[
            PydanticTransition(
                timestamp=t.timestamp,
                status=ShipmentStatus(t.status),
                actor=t.actor,
                source_system=t.source_system,
                geo_location=t.geo_location,
                offline_synced=t.offline_synced,
                exception_reason=t.exception_reason,
                evidence_urls=json.loads(t.evidence_urls) if t.evidence_urls else []
            )
            for t in orm_shipment.status_history
        ]
    )