export default function DemurrageWidget({ customsDate }) {
  if (!customsDate) return null; // Don't show if not declared yet

  const now = new Date();
  const declared = new Date(customsDate);
  const daysElapsed = Math.floor((now - declared) / (1000 * 60 * 60 * 24));
  
  const FREE_DAYS = 7;
  const RATE_PER_DAY = 5000; // KES
  
  const daysRemaining = FREE_DAYS - daysElapsed;
  const isOverdue = daysRemaining <= 0;
  const chargeableDays = isOverdue ? daysElapsed - FREE_DAYS : 0;
  const estimatedCost = chargeableDays * RATE_PER_DAY;

  // Progress calculation (0% to 100%)
  const progress = Math.min((daysElapsed / FREE_DAYS) * 100, 100);

  // Dynamic styling based on urgency
  const getColors = () => {
    if (isOverdue) return { bg: '#fee2e2', border: '#ef4444', text: '#991b1b', bar: '#ef4444' }; // Red
    if (daysRemaining <= 2) return { bg: '#fef3c7', border: '#f59e0b', text: '#92400e', bar: '#f59e0b' }; // Yellow
    return { bg: '#dcfce7', border: '#22c55e', text: '#166534', bar: '#22c55e' }; // Green
  };

  const colors = getColors();

  return (
    <div style={{ 
      marginTop: '15px', 
      padding: '15px', 
      background: colors.bg, 
      border: `2px solid ${colors.border}`, 
      borderRadius: '8px' 
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px' }}>
        <strong style={{ color: colors.text }}>KPA Demurrage Risk</strong>
        <span style={{ color: colors.text }}>Day {daysElapsed} of {FREE_DAYS}</span>
      </div>

      {/* Progress Bar */}
      <div style={{ height: '8px', background: '#e5e7eb', borderRadius: '4px', overflow: 'hidden' }}>
        <div style={{ 
          width: `${progress}%`, 
          background: colors.bar, 
          height: '100%', 
          transition: 'width 0.5s' 
        }} />
      </div>

      <div style={{ marginTop: '10px', fontSize: '14px', color: colors.text }}>
        {isOverdue ? (
          <div style={{ fontWeight: 'bold' }}>
            ⚠️ OVERDUE by {daysElapsed - FREE_DAYS} days<br/>
            Est. Cost: KES {estimatedCost.toLocaleString()}
          </div>
        ) : (
          <div>
            {daysRemaining} free days remaining.
          </div>
        )}
      </div>
    </div>
  );
}