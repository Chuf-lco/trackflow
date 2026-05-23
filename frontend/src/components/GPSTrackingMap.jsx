import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { useEffect, useState } from 'react';

// Fix for default marker icon in React-Leaflet
import L from 'leaflet';
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Northern Corridor Route Checkpoints (Lat, Lng)
const ROUTE_CHECKPOINTS = [
  { name: 'Mombasa Port', lat: -4.0435, lng: 39.6682, status: 'vessel_arrival' },
  { name: 'Mariakani', lat: -3.9833, lng: 39.4833, status: 'customs_declaration' },
  { name: 'Voi', lat: -3.3961, lng: 38.5561, status: 'physical_verification' },
  { name: 'Athi River', lat: -1.4501, lng: 36.9667, status: 'inland_transit' },
  { name: 'Nairobi ICD', lat: -1.2864, lng: 36.8172, status: 'delivered' }
];

export default function GPSTrackingMap({ currentStatus }) {
  const [currentLocation, setCurrentLocation] = useState(null);

  // Determine truck position based on status
  useEffect(() => {
    const checkpoint = ROUTE_CHECKPOINTS.find(cp => cp.status === currentStatus);
    if (checkpoint) {
      setCurrentLocation({ lat: checkpoint.lat, lng: checkpoint.lng, name: checkpoint.name });
    }
  }, [currentStatus]);

  if (!currentLocation) return null; // Don't show map until status is known

  // Route line coordinates (all checkpoints)
  const routeCoords = ROUTE_CHECKPOINTS.map(cp => [cp.lat, cp.lng]);

  // Center map between Mombasa and Nairobi
  const mapCenter = [-2.5, 38.2]; // Approximate center of Kenya
  const mapZoom = 7;

  return (
    <div style={{ marginTop: '15px', borderRadius: '8px', overflow: 'hidden', border: '1px solid #ddd' }}>
      <div style={{ background: '#f8f9fa', padding: '10px', borderBottom: '1px solid #ddd' }}>
        <h3 style={{ margin: 0, fontSize: '14px', color: '#333' }}>📍 Live GPS Tracking (Northern Corridor)</h3>
        <p style={{ margin: '5px 0 0', fontSize: '12px', color: '#666' }}>
          Current Location: <strong>{currentLocation.name}</strong>
        </p>
      </div>
      
      <MapContainer 
        center={mapCenter} 
        zoom={mapZoom} 
        style={{ height: '250px', width: '100%' }}
        scrollWheelZoom={false}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; OpenStreetMap contributors'
        />
        
        {/* Route Line */}
        <Polyline 
          positions={routeCoords} 
          color="#3b82f6" 
          weight={3} 
          opacity={0.6} 
          dashArray="10, 10"
        />
        
        {/* Checkpoint Markers */}
        {ROUTE_CHECKPOINTS.map((cp, index) => (
          <Marker 
            key={cp.name} 
            position={[cp.lat, cp.lng]}
            icon={L.divIcon({
              className: 'custom-marker',
              html: `<div style="background: ${cp.status === currentStatus ? '#22c55e' : '#999'}; width: 12px; height: 12px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
              iconSize: [12, 12],
              iconAnchor: [6, 6]
            })}
          >
            <Popup>
              <div style={{ fontSize: '12px' }}>
                <strong>{cp.name}</strong><br/>
                Status: {cp.status.replace('_', ' ')}
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Truck Marker (Current Location) */}
        <Marker position={[currentLocation.lat, currentLocation.lng]}>
          <Popup>
            <div style={{ fontSize: '12px' }}>
              <strong>🚛 Truck Location</strong><br/>
              {currentLocation.name}<br/>
              <em>Updated: Just now</em>
            </div>
          </Popup>
        </Marker>
      </MapContainer>

      {/* GPS Dead Zone Warning (Northern Corridor specific) */}
      {currentStatus === 'physical_verification' && (
        <div style={{ 
          background: '#fef3c7', 
          padding: '8px', 
          fontSize: '12px', 
          color: '#92400e',
          display: 'flex',
          alignItems: 'center',
          gap: '5px'
        }}>
          ⚠️ <span><strong>GPS Gap:</strong> Voi to Mariakani section has poor connectivity. Last sync was 15 mins ago.</span>
        </div>
      )}
    </div>
  );
}