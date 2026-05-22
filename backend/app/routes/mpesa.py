from fastapi import APIRouter, HTTPException, logger
from ..models import Shipment, ShipmentStatus, StatusTransition
from datetime import datetime, timezone
from ..services.notifications import notification_service
import time
import random

router = APIRouter(prefix="/api/v1/shipments", tags=["mpesa"])

@router.post("/{shipment_id}/pay-mpesa")
def simulate_mpesa_payment(shipment_id: str, payload: dict):
    """
    Simulates Safaricom Daraja STK Push.
    In production, this would call Safaricom API and wait for a webhook.
    Here, we simulate the 10-second delay and auto-update the status.
    """
    # 1. Validate Shipment
    from .shipments import shipments_db # Import the in-memory DB
    if shipment_id not in shipments_db:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    shipment = shipments_db[shipment_id]
    
    # 2. Validate Status (Can only pay if at Vessel Arrival)
    if shipment.current_status != ShipmentStatus.VESSEL_ARRIVAL:
        raise HTTPException(status_code=400, detail="Shipment is not ready for payment")

    # 3. Simulate STK Push Delay (User is entering PIN on phone)
    # In real app, this returns 200 immediately and a webhook updates it later.
    # For this demo, we block for 3 seconds to show the "Processing..." UI.
    time.sleep(3) 

    # 4. Simulate Success (90% success rate)
    if random.random() < 0.1:
        raise HTTPException(status_code=500, detail="M-Pesa Transaction Failed. Retry.")

    # 5. Update Shipment Status to Customs Declaration (Green Channel)
    # This matches your README: "Payment Received -> KRA Risk Assessment"
    now_eat = datetime.now(timezone.utc) # Using UTC for storage

    # 6. Send WhatsApp Notification
    try:
        # In production, get phone from shipment.owner_phone
        # For demo, use hardcoded number
        phone = "712345678"  
        message = notification_service.get_status_message(shipment)
        notification_service.send_whatsapp_alert(phone, message)
        
        logger.info(f"✅ WhatsApp sent to {phone}")
    except Exception as e:
        logger.error(f"Failed to send WhatsApp: {e}")
        # Don't fail the payment if notification fails

    return {
        "status": "success",
        "message": "Payment Received. Shipment moved to Customs Declaration.",
        "mpesa_receipt": f"MBA{random.randint(1000, 9999)}",
        "notification_sent": True
    }
    
    transition = StatusTransition(
        timestamp=now_eat,
        status=ShipmentStatus.CUSTOMS_DECLARATION,
        actor="system_mpesa",
        source_system="M-Pesa",
        geo_location="-4.0435, 39.6682", # Mombasa Port
        offline_synced=False,
        exception_reason=None
    )

    shipment.status_history.append(transition)
    shipment.current_status = ShipmentStatus.CUSTOMS_DECLARATION
    shipment.payment_status = "paid"
    shipment.customs_declaration_date = now_eat
    shipment.updated_at = now_eat

    return {
        "status": "success",
        "message": "Payment Received. Shipment moved to Customs Declaration (Green Channel).",
        "mpesa_receipt": f"MBA{random.randint(1000, 9999)}"
    }