import { useState } from 'react';

const STATUS_OPTIONS = [
  'customs_declaration',
  'physical_verification',
  'inland_transit',
  'delivered'
];

const SOURCE_SYSTEMS = ['KWATOS', 'Tradex', 'GPS', 'Manual', 'ECTS', 'M-Pesa'];

export default function StatusTransitionModal({ shipment, onClose, onSuccess }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [formData, setFormData] = useState({
    status: 'customs_declaration',
    actor: '',
    source_system: 'Manual',
    geo_location: '',
    offline_synced: false,
    exception_reason: '',
    evidence_urls: ''
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      // Auto-generate EAT timestamp (UTC+3)
      const now = new Date();
      const eatOffset = 3 * 60; // minutes
      const eatDate = new Date(now.getTime() + eatOffset * 60000);
      const timestamp = eatDate.toISOString().replace('Z', '+03:00');

      const payload = {
        ...formData,
        timestamp,
        evidence_urls: formData.evidence_urls ? formData.evidence_urls.split(',').map(u => u.trim()).filter(Boolean) : []
      };

      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/v1/shipments/${shipment.id}/status`,
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
        <h2>Update Status: {shipment.bl_number}</h2>
        {error && <p className="error-text">{error}</p>}
        
        <form onSubmit={handleSubmit} className="transition-form">
          <label>
            Next Status:
            <select name="status" value={formData.status} onChange={handleChange} required>
              {STATUS_OPTIONS.map(s => (
                <option key={s} value={s}>{s.replace('_', ' ').toUpperCase()}</option>
              ))}
            </select>
          </label>

          <label>
            Actor (KRA PIN / Driver ID / System):
            <input name="actor" value={formData.actor} onChange={handleChange} placeholder="e.g., agent_kra_pin_A123456789" required />
          </label>

          <label>
            Source System:
            <select name="source_system" value={formData.source_system} onChange={handleChange}>
              {SOURCE_SYSTEMS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </label>

          <label>
            Geo Location (lat,long):
            <input name="geo_location" value={formData.geo_location} onChange={handleChange} placeholder="-4.0435, 39.6682" />
          </label>

          <label className="checkbox-label">
            <input type="checkbox" name="offline_synced" checked={formData.offline_synced} onChange={handleChange} />
            Offline Synced (Northern Corridor GPS gap)
          </label>

          <label>
            Exception Reason (if delayed &gt; threshold):
            <textarea 
            name="exception_reason" 
            value={formData.exception_reason} 
            onChange={handleChange} 
            rows="2" 
            />
          </label>

          <label>
            Evidence URLs (comma-separated):
            <input name="evidence_urls" value={formData.evidence_urls} onChange={handleChange} placeholder="https://example.com/doc1.pdf, https://example.com/photo.jpg" />
          </label>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
            <button type="submit" disabled={loading} className="btn-primary">
              {loading ? 'Transitioning...' : 'Update Status'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}