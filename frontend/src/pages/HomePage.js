import React, { useState, useEffect, useCallback } from 'react';
import { Row, Col, Input, message, Alert, Typography } from 'antd';
import { SearchOutlined, EnvironmentOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import WorldMap from '../components/WorldMap';
import PredictionWidget from '../components/PredictionWidget';
import CurrentAQIWidget from '../components/CurrentAQIWidget';
import { fetchPredictions, fetchCurrentAQI } from '../services/api';

const { Search } = Input;
const { Title, Text } = Typography;

const PageContainer = styled.div`
  max-width: 1400px;
  margin: 0 auto;
`;

const PageHeader = styled.div`
  margin-bottom: 22px;
`;

const HeaderMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 10px;
  color: rgba(235, 235, 245, 0.62);
  flex-wrap: wrap;

  .ant-typography {
    color: rgba(235, 235, 245, 0.62);
  }
`;

const MapContainer = styled.div`
  background: rgba(28, 28, 30, 0.68);
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 22px;
  box-shadow:
    0 26px 80px rgba(0, 0, 0, 0.42),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  overflow: hidden;
  margin-bottom: 24px;
  backdrop-filter: blur(28px) saturate(1.3);
`;

const Panel = styled.div`
  background: rgba(28, 28, 30, 0.72);
  padding: 18px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  border-radius: 22px;
  box-shadow:
    0 22px 70px rgba(0, 0, 0, 0.32),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  margin-bottom: 24px;
  backdrop-filter: blur(28px) saturate(1.35);

  .ant-input-affix-wrapper,
  .ant-input-group-addon,
  .ant-input-search-button {
    border-color: rgba(255, 255, 255, 0.12) !important;
  }

  .ant-input-affix-wrapper,
  .ant-input {
    background: rgba(118, 118, 128, 0.18) !important;
    color: rgba(255, 255, 255, 0.92);
  }

  .ant-input-affix-wrapper {
    border-radius: 14px 0 0 14px !important;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  }

  .ant-input::placeholder {
    color: rgba(235, 235, 245, 0.38);
  }

  .ant-input-search-button {
    border-radius: 0 14px 14px 0 !important;
    background: linear-gradient(180deg, #0a84ff, #0066d6);
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.25);
  }

  .ant-alert {
    background: rgba(10, 132, 255, 0.14);
    border-color: rgba(10, 132, 255, 0.26);
    border-radius: 16px;
  }

  .ant-alert-message {
    color: rgba(255, 255, 255, 0.92);
  }

  .ant-alert-description {
    color: rgba(235, 235, 245, 0.62);
  }
`;

const FieldLabel = styled.div`
  color: rgba(235, 235, 245, 0.72);
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 8px;
`;

const WidgetsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-top: 24px;

  @media (max-width: 1000px) {
    grid-template-columns: 1fr;
  }
`;

const HomePage = () => {
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [predictions, setPredictions] = useState(null);
  const [currentAQI, setCurrentAQI] = useState(null);
  const [loading, setLoading] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [currentLoading, setCurrentLoading] = useState(false);
  const [predictionError, setPredictionError] = useState(null);
  const [currentError, setCurrentError] = useState(null);

  const handleLocationSelect = (lat, lng, cityName) => {
    setSelectedLocation({ lat, lng, name: cityName });
    setPredictions(null);
    setCurrentAQI(null);
    setPredictionError(null);
    setCurrentError(null);
    message.success(`Selected ${cityName || `location (${lat.toFixed(4)}, ${lng.toFixed(4)})`}`);
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
      setPredictionError(null);
      const predData = await fetchPredictions(selectedLocation.lat, selectedLocation.lng);
      setPredictions(predData);
    } catch (error) {
      console.error('Prediction polling error:', error);
      setPredictionError(error?.response?.data?.error || 'Unable to fetch predictions');
    } finally {
      setPredictionLoading(false);
    }
  }, [selectedLocation]);

  const fetchCurrentAQIData = useCallback(async () => {
    if (!selectedLocation) return;

    try {
      setCurrentLoading(true);
      setCurrentError(null);
      const aqiData = await fetchCurrentAQI(selectedLocation.lat, selectedLocation.lng);
      setCurrentAQI(aqiData);
    } catch (error) {
      console.error('Failed to fetch current AQI:', error);
      setCurrentError(error?.response?.data?.error || 'Unable to fetch current AQI data');
    }
    finally {
      setCurrentLoading(false);
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
  }, [selectedLocation, fetchCurrentAQIData, pollPredictions]);

  return (
    <PageContainer>
      <PageHeader>
        <Title level={2} style={{ margin: 0, color: 'rgba(255, 255, 255, 0.94)', fontWeight: 650 }}>
          Air quality forecast
        </Title>
        <HeaderMeta>
          <Text>Select a location to fetch live conditions and 24, 48, and 72 hour AQI forecasts.</Text>
        </HeaderMeta>
      </PageHeader>

      <Panel>
        <Row gutter={[16, 16]} align="bottom">
          <Col xs={24} lg={12}>
            <FieldLabel>Location search</FieldLabel>
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
          <Col xs={24} lg={12}>
            {selectedLocation && (
              <Alert
                message={`Selected: ${selectedLocation.name || `Location (${selectedLocation.lat.toFixed(4)}, ${selectedLocation.lng.toFixed(4)})`}`}
                description={`Coordinates: ${selectedLocation.lat.toFixed(4)}, ${selectedLocation.lng.toFixed(4)}`}
                type="info"
                showIcon
                icon={<EnvironmentOutlined />}
              />
            )}
          </Col>
        </Row>
      </Panel>

      <MapContainer>
        <WorldMap onLocationSelect={handleLocationSelect} selectedLocation={selectedLocation} />
      </MapContainer>

      {selectedLocation && (
        <WidgetsContainer>
          <CurrentAQIWidget
            data={currentAQI}
            location={selectedLocation}
            loading={currentLoading}
            error={currentError}
          />
          <PredictionWidget
            data={predictions}
            location={selectedLocation}
            loading={predictionLoading}
            error={predictionError}
          />
        </WidgetsContainer>
      )}
    </PageContainer>
  );
};

export default HomePage;
