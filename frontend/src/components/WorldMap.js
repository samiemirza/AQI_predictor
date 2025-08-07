import React from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import styled from 'styled-components';

const MapWrapper = styled.div`
  height: 500px;
  width: 100%;
`;

// Fix for default markers in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const WorldMap = ({ onLocationSelect, selectedLocation }) => {
  const majorCities = [
    { name: "New York", lat: 40.7128, lng: -74.0060 },
    { name: "London", lat: 51.5074, lng: -0.1278 },
    { name: "Tokyo", lat: 35.6762, lng: 139.6503 },
    { name: "Mumbai", lat: 19.0760, lng: 72.8777 },
    { name: "Karachi", lat: 24.8607, lng: 67.0011 },
    { name: "Beijing", lat: 39.9042, lng: 116.4074 },
    { name: "Sydney", lat: -33.8688, lng: 151.2093 },
    { name: "Cairo", lat: 30.0444, lng: 31.2357 },
    { name: "São Paulo", lat: -23.5505, lng: -46.6333 },
    { name: "Moscow", lat: 55.7558, lng: 37.6176 }
  ];

  const handleMapClick = (e) => {
    const { lat, lng } = e.latlng;
    onLocationSelect(lat, lng, null);
  };

  const handleCityClick = (city) => {
    onLocationSelect(city.lat, city.lng, city.name);
  };

  return (
    <MapWrapper>
      <MapContainer
        center={[20, 0]}
        zoom={2}
        style={{ height: '100%', width: '100%' }}
        onClick={handleMapClick}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {/* Major cities markers */}
        {majorCities.map((city) => (
          <Marker
            key={city.name}
            position={[city.lat, city.lng]}
            eventHandlers={{
              click: () => handleCityClick(city),
            }}
          >
            <Popup>
              <div>
                <strong>{city.name}</strong>
                <br />
                Click to select this location
              </div>
            </Popup>
          </Marker>
        ))}
        
        {/* Selected location marker */}
        {selectedLocation && (
          <Marker
            position={[selectedLocation.lat, selectedLocation.lng]}
            icon={L.icon({
              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
              iconSize: [25, 41],
              iconAnchor: [12, 41],
              popupAnchor: [1, -34],
              shadowSize: [41, 41]
            })}
          >
            <Popup>
              <div>
                <strong>Selected Location</strong>
                <br />
                {selectedLocation.name || `(${selectedLocation.lat.toFixed(4)}, ${selectedLocation.lng.toFixed(4)})`}
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </MapWrapper>
  );
};

export default WorldMap; 