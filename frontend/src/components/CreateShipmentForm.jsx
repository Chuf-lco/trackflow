import { useState } from 'react';

export default function CreateShipmentForm({ onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    bl_number: '',
    container_number: '',
    manifest_date: new Date().toISOString().split('T')[0],
    payment_status: 'pending'
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Generate unique ID: MBA + date + random
      const dateStr = new Date().toISOString().slice(0,10).replace(/-/g,'').slice(2);
      const random = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
      const id = `MBA${dateStr}${random}`;

      // Auto-generate EAT timestamp
      const now = new Date();
      const eatOffset = 3 * 60;
      const eatDate = new Date(now.getTime() + eatOffset * 60000);
      const manifestDate = `${formData.manifest_date}T10:00:00+03:00`;

      const payload = {
        id,
        bl_number: formData.bl_number.toUpperCase(),
        container_number: formData.container_number.toUpperCase(),
        current_status: 'vessel_arrival',
        status_history: [],
        manifest_date: manifestDate,
        payment_status: formData.payment_status,
        gps_tracking_active: false,
        demurrage_days: 0
      };

      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/v1/shipments/`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        }
      );

      if (!res.ok) throw new Error(`Failed: ${res.status}`);
      
      onSuccess();
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()}>
        <h2>📦 Create New Shipment</h2>
        <p style={{color: '#666', fontSize: '14px', marginBottom: '20px'}}>
          Status 1: Vessel Arrival & Manifest (Mombasa Port)
        </p>
        
        {error && <p className="error-text">{error}</p>}
        
        <form onSubmit={handleSubmit} className="transition-form">
          <label>
            Bill of Lading (B/L) Number:
            <input 
              name="bl_number" 
              value={formData.bl_number} 
              onChange={handleChange} 
              placeholder="e.g., MAEU2026MBA123456" 
              required 
              pattern="[A-Z0-9]+"
            />
          </label>

          <label>
            Container Number:
            <input 
              name="container_number" 
              value={formData.container_number} 
              onChange={handleChange} 
              placeholder="e.g., MSKU1234567" 
              required 
              pattern="[A-Z0-9]+"
            />
          </label>

          <label>
            Manifest Date:
            <input 
              type="date"
              name="manifest_date" 
              value={formData.manifest_date} 
              onChange={handleChange} 
              required 
            />
          </label>

          <label>
            Payment Status:
            <select 
              name="payment_status" 
              value={formData.payment_status} 
              onChange={handleChange}
            >
              <option value="pending">Pending</option>
              <option value="paid">Paid (M-Pesa/Bank)</option>
              <option value="failed">Payment Failed</option>
            </select>
          </label>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Creating...' : 'Create Shipment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}