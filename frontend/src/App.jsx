import { useState, useEffect } from 'react'
import './App.css'
import StatusTransitionModal from './components/StatusTransitionModal';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

function App() {
  // 1. Check what URL is being used
  const API_URL = import.meta.env.VITE_API_BASE_URL;
  console.log("CURRENT API URL:", API_URL);

  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transitioningShipment, setTransitioningShipment] = useState(null);

  useEffect(() => {
    fetchShipments();
  }, []);

  const fetchShipments = async () => {
    try {
      // 2. Log the full URL before fetching
      const fullUrl = `${API_URL}/api/v1/shipments/`;
      console.log("FETCHING FROM:", fullUrl);

      const response = await fetch(fullUrl);

      if (!response.ok) throw new Error(`Server responded with ${response.status}`);

      const data = await response.json()
      setShipments(data);
      setError(null);
    } catch (err) {
      console.error("Fetch Error:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const getStatusColor = (status) => {
    const colors = {
      vessel_arrival: 'bg-blue-500',
      customs_declaration: 'bg-yellow-500',
      physical_verification: 'bg-orange-500',
      inland_transit: 'bg-purple-500',
      delivered: 'bg-green-500'
    }
    return colors[status] || 'bg-gray-500'
  }

  const getStatusLabel = (status) => {
    const labels = {
      vessel_arrival: '🚢 Vessel Arrival',
      customs_declaration: '📋 Customs Declaration',
      physical_verification: '🔍 Physical Verification',
      inland_transit: '🚛 Inland Transit',
      delivered: '✅ Delivered'
    }
    return labels[status] || status
  }

  if (loading) return <div className="loading">Loading TrackFlow...</div>
  if (error) return <div className="error">Error: {error}</div>

  return (
    <div className="App">
      <header className="header">
        <h1>🇰 TrackFlow - Kenya Logistics</h1>
        <p>Mombasa Port Shipment Tracking System</p>
      </header>

      <main className="main">
        <div className="stats">
          <div className="stat-card">
            <h3>Total Shipments</h3>
            <p className="stat-number">{shipments.length}</p>
          </div>
          <div className="stat-card">
            <h3>In Transit</h3>
            <p className="stat-number">
              {shipments.filter(s => s.current_status !== 'delivered').length}
            </p>
          </div>
          <div className="stat-card">
            <h3>Delivered</h3>
            <p className="stat-number">
              {shipments.filter(s => s.current_status === 'delivered').length}
            </p>
          </div>
        </div>

        <div className="shipments-list">
          <h2>Active Shipments</h2>
          {shipments.length === 0 ? (
            <p className="empty-state">No shipments found. Create one via the API!</p>
          ) : (
            shipments.map((shipment) => (
              <div key={shipment.id} className="shipment-card">
                <div className="shipment-header">
                  <h3>{shipment.bl_number}</h3>
                  <span className={`status-badge ${getStatusColor(shipment.current_status)}`}>
                    {getStatusLabel(shipment.current_status)}
                  </span>
                </div>
                <div className="shipment-details">
                  <p><strong>Container:</strong> {shipment.container_number}</p>
                  <p><strong>ID:</strong> {shipment.id}</p>
                  <p><strong>Payment:</strong> {shipment.payment_status}</p>
                  {shipment.demurrage_days > 0 && (
                    <p className="demurrage-warning">
                      ⚠️ Demurrage: {shipment.demurrage_days} days
                    </p>
                  )}
                </div>
                <div className="shipment-actions">
                <button 
                  className="btn-primary"
                  onClick={() => setTransitioningShipment(shipment)}
                >
                  Update Status
                </button>
              </div>

                <div className="shipment-footer">
                  <small>
                    Updated: {new Date(shipment.updated_at).toLocaleString('en-KE', {
                      timeZone: 'Africa/Nairobi'
                    })}
                  </small>
                </div>
              </div>
            ))
          )}
        </div>
      </main>
      {transitioningShipment && (
        <StatusTransitionModal
          shipment={transitioningShipment}
          onClose={() => setTransitioningShipment(null)}
          onSuccess={handleStatusUpdated}
        />
      )}
    </div>
  )
}

export default App