import React, { useState, useEffect, useCallback } from 'react';
import { Row, Col, Input, message, Alert } from 'antd';
import { SearchOutlined, EnvironmentOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import WorldMap from '../components/WorldMap';
import PredictionWidget from '../components/PredictionWidget';
import CurrentAQIWidget from '../components/CurrentAQIWidget';
import { fetchPredictions, fetchCurrentAQI } from '../services/api';

const { Search } = Input;

const PageContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const MapContainer = styled.div`
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-bottom: 24px;
`;

const SearchContainer = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const ActionButtonsContainer = styled.div`
  background: white;
  padding: 24px;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
`;

const WidgetsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 24px;
`;

const HomePage = () => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [currentAQI, setCurrentAQI] = useState(null);
  const [loading, setLoading] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);

  const handleLocationSelect = (lat, lng, cityName) => {
    setSelectedLocation({ lat, lng, name: cityName });
    message.success(`📍 Selected: ${cityName || `Location (${lat.toFixed(4)}, ${lng.toFixed(4)})`}`);
  };

  const handleSearch = async (value) => {
    if (!value.trim()) return;
    
    setLoading(true);
    try {
      // This would call a geocoding service
      const coords = await geocodeCity(value);
      if (coords) {
        handleLocationSelect(coords.lat, coords.lng, value);
        setSearchQuery('');
      } else {
        message.error('City not found. Please try a different search term.');
      }
    } catch (error) {
      message.error('Search failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const geocodeCity = async (cityName) => {
    // Mock geocoding - in real app, use a service like Nominatim
    const cityCoords = {
      'new york': { lat: 40.7128, lng: -74.0060 },
      'london': { lat: 51.5074, lng: -0.1278 },
      'tokyo': { lat: 35.6762, lng: 139.6503 },
      'mumbai': { lat: 19.0760, lng: 72.8777 },
      'karachi': { lat: 24.8607, lng: 67.0011 },
      'beijing': { lat: 39.9042, lng: 116.4074 },
      'sydney': { lat: -33.8688, lng: 151.2093 },
      'cairo': { lat: 30.0444, lng: 31.2357 },
      'sao paulo': { lat: -23.5505, lng: -46.6333 },
      'moscow': { lat: 55.7558, lng: 37.6176 }
    };
    
    const normalizedCity = cityName.toLowerCase();
    return cityCoords[normalizedCity] || null;
  };

  const pollPredictions = useCallback(async () => {
    if (!selectedLocation) return;
    try {
      setPredictionLoading(true);
      const predData = await fetchPredictions(selectedLocation.lat, selectedLocation.lng);
      setPredictions(predData);
    } catch (error) {
      console.error('Prediction polling error:', error);
    } finally {
      setPredictionLoading(false);
    }
  }, [selectedLocation]);

  const fetchCurrentAQIData = useCallback(async () => {
    if (!selectedLocation) return;
    
    try {
      const aqiData = await fetchCurrentAQI(selectedLocation.lat, selectedLocation.lng);
      setCurrentAQI(aqiData);
    } catch (error) {
      console.error('Failed to fetch current AQI:', error);
      message.error('❌ Failed to fetch current AQI data');
    }
  }, [selectedLocation]);

  useEffect(() => {
    if (selectedLocation) {
      fetchCurrentAQIData();
      // initial predictions fetch
      pollPredictions();

      // set up 5-minute polling
      const intervalId = setInterval(() => {
        pollPredictions();
        fetchCurrentAQIData();
      }, 5 * 60 * 1000);

      return () => clearInterval(intervalId);
    }
  }, [selectedLocation, fetchCurrentAQIData]);

  return (
    <PageContainer>
      <h1>AQI Prediction Dashboard</h1>
      <p>Select a location on the map or search for a city to get air quality predictions.</p>

      {/* Search Section */}
      <SearchContainer>
        <Row gutter={16} align="middle">
          <Col span={12}>
            <Search
              placeholder="Search for a city (e.g., New York, London, Tokyo)"
              enterButton={<SearchOutlined />}
              size="large"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onSearch={handleSearch}
              loading={loading}
            />
          </Col>
          <Col span={12}>
            {selectedLocation && (
              <Alert
                message={`📍 Selected: ${selectedLocation.name || `Location (${selectedLocation.lat.toFixed(4)}, ${selectedLocation.lng.toFixed(4)})`}`}
                type="info"
                showIcon
                icon={<EnvironmentOutlined />}
              />
            )}
          </Col>
        </Row>
      </SearchContainer>

      {/* World Map */}
      <MapContainer>
        <WorldMap onLocationSelect={handleLocationSelect} selectedLocation={selectedLocation} />
      </MapContainer>

      {/* Auto-refresh active indicator */}
      {selectedLocation && (
        <ActionButtonsContainer>
          <Row justify="center">
            <Col span={12} style={{ textAlign: 'center' }}>
              <span>Auto-refreshing predictions every 5 minutes...</span>
            </Col>
          </Row>
        </ActionButtonsContainer>
      )}

      {/* Widgets */}
      {selectedLocation && (
        <WidgetsContainer>
          <CurrentAQIWidget data={currentAQI} location={selectedLocation} />
          <PredictionWidget data={predictions} location={selectedLocation} />
        </WidgetsContainer>
      )}
    </PageContainer>
  );
};

export default HomePage; 