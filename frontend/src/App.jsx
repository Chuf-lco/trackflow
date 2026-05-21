import { useState, useEffect } from 'react';
import './App.css';
import StatusTransitionModal from './components/StatusTransitionModal';
import DemurrageWidget from './components/DemurrageWidget';
import CreateShipmentForm from './components/CreateShipmentForm';
import TimelineWidget from './components/TimelineWidget';

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

function App() {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [transitioningShipment, setTransitioningShipment] = useState(null);
  const [creatingShipment, setCreatingShipment] = useState(false);
  useEffect(() => {
    fetchShipments();
  }, []);

  const fetchShipments = async () => {
    try {
      const response = await fetch(`${API_URL}/api/v1/shipments/`);
      if (!response.ok) throw new Error('Failed to fetch shipments');
      const data = await response.json();
      setShipments(data);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusUpdated = () => {
    fetchShipments();
  };

  // Status badge styles (inline for reliability across environments)
  const getStatusStyle = (status) => {
    const styles = {
      vessel_arrival: { background: '#3b82f6', color: '#fff' },
      customs_declaration: { background: '#eab308', color: '#000' },
      physical_verification: { background: '#f97316', color: '#fff' },
      inland_transit: { background: '#a855f7', color: '#fff' },
      delivered: { background: '#22c55e', color: '#fff' }
    };
    return styles[status] || { background: '#6b7280', color: '#fff' };
  };

  const getStatusLabel = (status) => {
    const labels = {
      vessel_arrival: '🚢 Vessel Arrival',
      customs_declaration: '📋 Customs Declaration',
      physical_verification: '🔍 Physical Verification',
      inland_transit: '🚛 Inland Transit',
      delivered: '✅ Delivered'
    };
    return labels[status] || status;
  };

  if (loading) return <div className="loading">Loading TrackFlow...</div>;
  if (error) return <div className="error">Error: {error}</div>;

  return (
    <div className="App">
      <header className="header">
        <h1> TrackFlow - Kenya Logistics</h1>
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
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
    <h2 style={{ margin: 0 }}>Active Shipments</h2>
    <button
      onClick={() => setCreatingShipment(true)}
      style={{
        padding: '10px 20px',
        background: '#22c55e',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer',
        fontWeight: '600',
        fontSize: '14px'
      }}
    >
      ➕ Create Shipment
    </button>
  </div>
          <h2>Active Shipments</h2>
          {shipments.length === 0 ? (
            <p className="empty-state">No shipments found. Create one via the API!</p>
          ) : (
            shipments.map((shipment) => (
              <div key={shipment.id} className="shipment-card">
                <div className="shipment-header">
                  <h3>{shipment.bl_number}</h3>
                  <span 
                    className="status-badge" 
                    style={getStatusStyle(shipment.current_status)}
                  >
                    {getStatusLabel(shipment.current_status)}
                  </span>
                </div>
                
                {/* ✅ INSERT TIMELINE WIDGET HERE */}
  <TimelineWidget 
    currentStatus={shipment.current_status} 
    history={shipment.status_history} 
  />
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

                <div className="shipment-footer">
                  <small>
                    Updated: {new Date(shipment.updated_at).toLocaleString('en-KE', {
                      timeZone: 'Africa/Nairobi'
                    })}
                  </small>
                </div>

                {/* ✅ Update Status Button */}
                <div className="shipment-actions">
                  <DemurrageWidget customsDate={shipment.customs_declaration_date} />
                  <button
                    className="btn-primary"
                    onClick={() => setTransitioningShipment(shipment)}
                    style={{
                      marginTop: '12px',
                      width: '100%',
                      padding: '10px',
                      background: '#667eea',
                      color: 'white',
                      border: 'none',
                      borderRadius: '5px',
                      cursor: 'pointer',
                      fontWeight: '600',
                      fontSize: '14px'
                    }}
                  >
                    🚚 Update Status
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </main>

      {/* ✅ Status Transition Modal */}
      {transitioningShipment && (
        <StatusTransitionModal
          shipment={transitioningShipment}
          onClose={() => setTransitioningShipment(null)}
          onSuccess={handleStatusUpdated}
        />
      )}
      {/* ✅ Create Shipment Modal */}
      {creatingShipment && (
        <CreateShipmentForm
          onClose={() => setCreatingShipment(false)}
          onSuccess={() => {
            setCreatingShipment(false);
            fetchShipments(); //Reuse existing function
          }}
        />
      )}
    </div>
  );
}

export default App;