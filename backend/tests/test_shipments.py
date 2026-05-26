import pytest
from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient
from app.main import app

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))  # Adjust path to import app modules
from app.models import Shipment, ShipmentStatus

client = TestClient(app)

@pytest.fixture
def sample_shipment():
    """Complete shipment payload matching Pydantic ShipmentCreate model"""
    return {
        "id": "TEST001",
        "bl_number": "MAEU123456789",
        "container_number": "MSKU1234567",
        "current_status": "vessel_arrival",
        #  REQUIRED: manifest_date must be timezone-aware ISO string
        "manifest_date": datetime.now(timezone.utc).isoformat(),
        "payment_status": "pending",
        "gps_tracking_active": False,
        "demurrage_days": 0
        # customs_declaration_date is optional - only add when testing demurrage
    }

def test_create_shipment(sample_shipment):
    """Test shipment creation"""
    response = client.post("/api/v1/shipments/", json=sample_shipment)
    assert response.status_code == 200
    data = response.json()
    assert data["bl_number"] == "MAEU123456789"
    assert data["current_status"] == "vessel_arrival"

def test_update_status(sample_shipment):
    """Test status transition workflow"""
    # Create shipment
    client.post("/api/v1/shipments/", json=sample_shipment)
    
    # Update status
    transition = {
        "status": "customs_declaration",
        "actor": "agent_kra_pin_A123456789",
        "source_system": "Tradex",
        "geo_location": "-4.0435, 39.6682",  # Mombasa Port
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    response = client.post("/api/v1/shipments/TEST001/status", json=transition)
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == "customs_declaration"
    assert len(data["status_history"]) == 1

def test_demurrage_calculation(sample_shipment):
    """Test Kenya-specific demurrage calculation"""
    from datetime import datetime, timedelta, timezone
    
    # Create shipment with customs declaration 10 days ago (timezone-aware)
    sample_shipment["customs_declaration_date"] = (
        datetime.now(timezone.utc) - timedelta(days=10)
    ).isoformat()
    
    # Create the shipment first
    create_response = client.post("/api/v1/shipments/", json=sample_shipment)
    
    # Debug: Print response if creation fails
    if create_response.status_code != 200:
        print(f"❌ Creation failed: {create_response.status_code} - {create_response.json()}")
    
    assert create_response.status_code == 200, f"Failed to create: {create_response.json()}"
    
    # Now test demurrage
    response = client.get("/api/v1/shipments/TEST001/demurrage")
    assert response.status_code == 200
    
    data = response.json()
    assert data["demurrage_days"] >= 10
    assert data["estimated_cost_kes"] > 0
    assert data["alert"] == True

def test_offline_sync_field(sample_shipment):
    """Test offline-synced capability (Kenya connectivity)"""
    client.post("/api/v1/shipments/", json=sample_shipment)
    
    transition = {
        "status": "inland_transit",
        "actor": "driver_254712345678",
        "source_system": "GPS",
        "offline_synced": True,  # Critical for Northern Corridor
        "exception_reason": "GPS dead zone - Voi to Mariakani"
    }
    
    response = client.post("/api/v1/shipments/TEST001/status", json=transition)
    assert response.status_code == 200
    data = response.json()
    assert data["status_history"][0]["offline_synced"] == True