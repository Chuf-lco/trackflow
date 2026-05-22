import { useState } from 'react';

export default function MpesaPaymentModal({ shipment, onClose, onSuccess }) {
  const [phone, setPhone] = useState('');
  const [status, setStatus] = useState('idle'); // idle, processing, success, error
  const [message, setMessage] = useState('');

  const handlePay = async (e) => {
    e.preventDefault();
    setStatus('processing');
    setMessage('STK Push sent. Waiting for confirmation...');

    try {
      const res = await fetch(
        `${import.meta.env.VITE_API_BASE_URL}/api/v1/shipments/${shipment.id}/pay-mpesa`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ phone: `254${phone}` })
        }
      );
      
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Payment failed');

      setStatus('success');
      setMessage(`Success! Receipt: ${data.mpesa_receipt}`);
      setTimeout(() => {
        onSuccess();
        onClose();
      }, 1500);

    } catch (err) {
      setStatus('error');
      setMessage(err.message);
    }
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={e => e.stopPropagation()} style={{ maxWidth: '400px' }}>
        <h2 style={{ color: '#4CAF50' }}> Pay via M-Pesa</h2>
        
        <div style={{ background: '#f9f9f9', padding: '10px', borderRadius: '5px', marginBottom: '15px' }}>
          <p><strong>Shipment:</strong> {shipment.bl_number}</p>
          <p><strong>Amount:</strong> KES 15,000 (Est. VAT 16%)</p>
          <p style={{ fontSize: '12px', color: '#666' }}>Pay to clear customs (Green Channel)</p>
        </div>

        {status === 'idle' && (
          <form onSubmit={handlePay}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
              <span style={{ fontSize: '18px' }}>📱</span>
              <span>+254</span>
              <input
                type="tel"
                placeholder="712 345 678"
                value={phone}
                onChange={e => setPhone(e.target.value.replace(/\D/g, ''))}
                required
                pattern="[0-9]{9}"
                style={{ flex: 1, padding: '8px', fontSize: '16px' }}
              />
            </label>
            <div className="modal-actions">
              <button type="button" onClick={onClose} className="btn-secondary">Cancel</button>
              <button type="submit" className="btn-primary" style={{ background: '#4CAF50' }}>
                Pay Now
              </button>
            </div>
          </form>
        )}

        {status === 'processing' && (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <div style={{ fontSize: '40px', animation: 'pulse 1s infinite' }}>📱</div>
            <p style={{ fontWeight: 'bold', color: '#4CAF50' }}>Check your phone</p>
            <p style={{ fontSize: '12px', color: '#666' }}>{message}</p>
          </div>
        )}

        {status === 'success' && (
          <div style={{ textAlign: 'center', padding: '20px', color: '#4CAF50' }}>
            <div style={{ fontSize: '40px' }}>✅</div>
            <p style={{ fontWeight: 'bold' }}>Payment Successful!</p>
            <p style={{ fontSize: '12px' }}>{message}</p>
          </div>
        )}

        {status === 'error' && (
          <div style={{ textAlign: 'center', padding: '20px' }}>
            <p style={{ color: 'red', fontWeight: 'bold' }}>Payment Failed</p>
            <p style={{ fontSize: '12px' }}>{message}</p>
            <button onClick={() => setStatus('idle')} className="btn-secondary" style={{ marginTop: '10px' }}>Retry</button>
          </div>
        )}
      </div>
    </div>
  );
}