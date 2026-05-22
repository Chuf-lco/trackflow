import { useState, useEffect } from 'react';

export default function WhatsAppAlert({ shipment }) {
  const [logs, setLogs] = useState([]);
  const [showLogs, setShowLogs] = useState(false);

  // Simulate fetching notification logs (in production, fetch from API)
  useEffect(() => {
    // Mock logs based on status history
    const mockLogs = shipment.status_history.map((transition, index) => ({
      timestamp: transition.timestamp,
      status: 'sent',
      message: `Status updated to ${transition.status.replace('_', ' ')}`,
      phone: '***-***-678'
    }));
    setLogs(mockLogs);
  }, [shipment]);

  if (!showLogs) {
    return (
      <button
        onClick={() => setShowLogs(true)}
        style={{
          background: 'transparent',
          border: '1px solid #25D366',
          color: '#25D366',
          padding: '5px 10px',
          borderRadius: '5px',
          cursor: 'pointer',
          fontSize: '12px',
          marginTop: '10px'
        }}
      >
        📱 View WhatsApp Alerts ({logs.length})
      </button>
    );
  }

  return (
    <div style={{ 
      marginTop: '10px', 
      padding: '10px', 
      background: '#f0f9f0', 
      border: '1px solid #25D366',
      borderRadius: '5px',
      fontSize: '12px'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
        <strong style={{ color: '#25D366' }}>📱 WhatsApp Notifications</strong>
        <button 
          onClick={() => setShowLogs(false)}
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#666' }}
        >
          ✕
        </button>
      </div>
      
      {logs.length === 0 ? (
        <p style={{ color: '#666' }}>No alerts sent yet</p>
      ) : (
        logs.map((log, index) => (
          <div key={index} style={{ 
            marginBottom: '8px', 
            padding: '8px', 
            background: 'white',
            borderRadius: '4px',
            borderLeft: '3px solid #25D366'
          }}>
            <div style={{ fontSize: '10px', color: '#666' }}>
              {new Date(log.timestamp).toLocaleString('en-KE', { timeZone: 'Africa/Nairobi' })}
            </div>
            <div style={{ marginTop: '4px' }}>{log.message}</div>
            <div style={{ fontSize: '10px', color: '#25D366', marginTop: '2px' }}>
              ✓ Sent to {log.phone}
            </div>
          </div>
        ))
      )}
    </div>
  );
}