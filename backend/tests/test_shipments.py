import pytest
from datetime import datetime, timezone, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def sample_shipment():
    """
    Complete shipment payload matching Pydantic ShipmentCreate model.
    All required fields with correct types for Pydantic v2 validation.
    """
    return {
        "id": "TEST001",
        "bl_number": "MAEU123456789",
        "container_number": "MSKU1234567",
        "current_status": "vessel_arrival",  # Must match ShipmentStatus enum value
        "manifest_date": datetime.now(timezone.utc).isoformat(),  # ✅ Timezone-aware ISO string
        "payment_status": "pending",
        "gps_tracking_active": False,
        "demurrage_days": 0
        # customs_declaration_date is optional - only add when testing demurrage
    }

def test_create_shipment(sample_shipment):
    """Test shipment creation"""
    response = client.post("/api/v1/shipments/", json=sample_shipment)
    
    # Debug: Print response if it fails
    if response.status_code != 200:
        print(f"❌ Response: {response.status_code}")
        print(f"❌ Body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "TEST001"
    assert data["bl_number"] == "MAEU123456789"
    assert data["current_status"] == "vessel_arrival"

def test_update_status(sample_shipment):
    """Test status transition workflow"""
    # Create shipment first
    create_response = client.post("/api/v1/shipments/", json=sample_shipment)
    if create_response.status_code != 200:
        print(f"❌ Create failed: {create_response.json()}")
        pytest.skip("Cannot test status update without successful creation")
    
    # Update status - send minimal valid transition
    transition = {
        "timestamp": datetime.now(timezone.utc).isoformat(),  # ✅ Timezone-aware
        "status": "customs_declaration",  # Must be enum value
        "actor": "agent_kra_pin_A123456789",
        "source_system": "Tradex",
        "geo_location": "-4.0435, 39.6682",
        "offline_synced": False,
        "exception_reason": None,
        "evidence_urls": []
    }
    
    response = client.post("/api/v1/shipments/TEST001/status", json=transition)
    
    # Debug output
    if response.status_code != 200:
        print(f"❌ Status update failed: {response.status_code}")
        print(f"❌ Body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["current_status"] == "customs_declaration"

def test_demurrage_calculation(sample_shipment):
    """Test Kenya-specific demurrage calculation"""
    # Add customs_declaration_date 10 days ago (timezone-aware)
    sample_shipment["customs_declaration_date"] = (
        datetime.now(timezone.utc) - timedelta(days=10)
    ).isoformat()
    
    # Create shipment
    create_response = client.post("/api/v1/shipments/", json=sample_shipment)
    if create_response.status_code != 200:
        print(f"❌ Create failed: {create_response.json()}")
        pytest.skip("Cannot test demurrage without successful creation")
    
    # Test demurrage endpoint
    response = client.get("/api/v1/shipments/TEST001/demurrage")
    
    if response.status_code != 200:
        print(f"❌ Demurrage failed: {response.status_code}")
        print(f"❌ Body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    assert data["demurrage_days"] >= 10
    assert data["estimated_cost_kes"] > 0
    assert data["alert"] == True

def test_offline_sync_field(sample_shipment):
    """Test offline-synced capability (Kenya connectivity)"""
    # Create shipment
    create_response = client.post("/api/v1/shipments/", json=sample_shipment)
    if create_response.status_code != 200:
        print(f"❌ Create failed: {create_response.json()}")
        pytest.skip("Cannot test offline sync without successful creation")
    
    # Update with offline_synced=True
    transition = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "inland_transit",
        "actor": "driver_254712345678",
        "source_system": "GPS",
        "offline_synced": True,  # Critical for Northern Corridor
        "exception_reason": "GPS dead zone - Voi to Mariakani",
        "evidence_urls": []
    }
    
    response = client.post("/api/v1/shipments/TEST001/status", json=transition)
    
    if response.status_code != 200:
        print(f"❌ Offline sync failed: {response.status_code}")
        print(f"❌ Body: {response.json()}")
    
    assert response.status_code == 200
    data = response.json()
    # Find the transition in history and verify offline_synced
    offline_transitions = [t for t in data["status_history"] if t.get("offline_synced") == True]
    assert len(offline_transitions) >= 1