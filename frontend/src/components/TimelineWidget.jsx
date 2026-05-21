export default function TimelineWidget({ currentStatus, history }) {
  // Define the 5 stages from your README
  const stages = [
    { key: 'vessel_arrival', label: 'Vessel Arrival', icon: '🚢' },
    { key: 'customs_declaration', label: 'Customs Declaration', icon: '📋' },
    { key: 'physical_verification', label: 'Verification', icon: '🔍' },
    { key: 'inland_transit', label: 'Inland Transit', icon: '🚛' },
    { key: 'delivered', label: 'Delivered', icon: '✅' }
  ];

  // Find index of current status
  const currentIndex = stages.findIndex(s => s.key === currentStatus);

  return (
    <div style={{ marginTop: '15px', marginBottom: '15px' }}>
      {/* Connecting Line */}
      <div style={{ 
        height: '4px', 
        background: '#e5e7eb', 
        borderRadius: '2px', 
        position: 'relative', 
        top: '10px' 
      }}>
        {/* Active Progress Line */}
        <div style={{ 
          height: '100%', 
          background: '#22c55e', 
          width: `${(currentIndex / (stages.length - 1)) * 100}%`, 
          borderRadius: '2px', 
          transition: 'width 0.5s ease' 
        }} />
      </div>

      {/* Dots and Labels */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'space-between', 
        marginTop: '-12px' // Pull up to overlap line 
      }}>
        {stages.map((stage, index) => {
          const isCompleted = index < currentIndex;
          const isCurrent = index === currentIndex;
          
          return (
            <div key={stage.key} style={{ textAlign: 'center', flex: 1 }}>
              {/* Dot */}
              <div style={{
                width: isCurrent ? '24px' : '16px',
                height: isCurrent ? '24px' : '16px',
                borderRadius: '50%',
                background: isCompleted || isCurrent ? '#22c55e' : '#e5e7eb',
                border: isCurrent ? '3px solid #3b82f6' : 'none',
                margin: '0 auto',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontSize: isCurrent ? '12px' : '8px',
                fontWeight: 'bold',
                zIndex: 2,
                position: 'relative'
              }}>
                {isCompleted ? '✓' : ''}
              </div>
              
              {/* Label */}
              <div style={{ 
                fontSize: '10px', 
                marginTop: '4px', 
                color: isCompleted || isCurrent ? '#333' : '#999',
                fontWeight: isCurrent ? 'bold' : 'normal'
              }}>
                {stage.icon} <br /> {stage.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}