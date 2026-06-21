import React from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import styled from 'styled-components';

const MapWrapper = styled.div`
  height: 520px;
  width: 100%;
  background: #111114;

  .leaflet-container {
    font-family: inherit;
    background: #111114;
  }

  .leaflet-control-zoom a,
  .leaflet-control-attribution {
    background: rgba(28, 28, 30, 0.82) !important;
    border-color: rgba(255, 255, 255, 0.12) !important;
    color: rgba(255, 255, 255, 0.82) !important;
    backdrop-filter: blur(18px);
  }

  .leaflet-control-zoom {
    border: 1px solid rgba(255, 255, 255, 0.12) !important;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 14px 42px rgba(0, 0, 0, 0.34);
  }

  .leaflet-control-zoom a:hover {
    background: rgba(58, 58, 60, 0.9) !important;
  }

  .leaflet-popup-content-wrapper,
  .leaflet-popup-tip {
    background: rgba(28, 28, 30, 0.94);
    color: rgba(255, 255, 255, 0.9);
    border: 1px solid rgba(255, 255, 255, 0.12);
    box-shadow: 0 18px 50px rgba(0, 0, 0, 0.42);
    backdrop-filter: blur(22px);
  }

  .leaflet-popup-content-wrapper {
    border-radius: 16px;
  }

  .leaflet-popup-content {
    margin: 12px 14px;
  }

  .leaflet-popup-close-button {
    color: rgba(235, 235, 245, 0.62) !important;
  }

  @media (max-width: 768px) {
    height: 420px;
  }
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

  const handleCityClick = (city) => {
    onLocationSelect(city.lat, city.lng, city.name);
  };

  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        const { lat, lng } = e.latlng;
        onLocationSelect(lat, lng, null);
      },
    });
    return null;
  };

  return (
    <MapWrapper>
      <MapContainer
        center={[20, 0]}
        zoom={2}
        style={{ height: '100%', width: '100%' }}
      >
        <MapClickHandler />
        <TileLayer
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>'
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
                Select this location
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
