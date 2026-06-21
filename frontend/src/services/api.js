import axios from 'axios';

const isLocalDev = typeof window !== 'undefined' &&
  (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1');
const API_BASE_URL = process.env.REACT_APP_API_URL || (isLocalDev ? 'http://localhost:5001' : '/api');
const API_ROUTE_PREFIX = API_BASE_URL.replace(/\/$/, '').endsWith('/api') ? '' : '/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

// API endpoints
export const fetchCurrentAQI = async (lat, lng) => {
  try {
    const response = await api.get(`${API_ROUTE_PREFIX}/current-aqi`, {
      params: { lat, lng }
    });
    return response;
  } catch (error) {
    console.error('Error fetching current AQI:', error);
    throw error;
  }
};

export const fetchPredictions = async (lat, lng) => {
  try {
    const response = await api.get(`${API_ROUTE_PREFIX}/predictions`, {
      params: { lat, lng }
    });
    return response;
  } catch (error) {
    console.error('Error fetching predictions:', error);
    throw error;
  }
};

export const updateData = async (lat, lng, daysBack = 5) => {
  try {
    const response = await api.post(`${API_ROUTE_PREFIX}/update-data`, {
      lat,
      lng,
      days_back: daysBack
    });
    return response;
  } catch (error) {
    console.error('Error updating data:', error);
    throw error;
  }
};

export const trainModels = async () => {
  try {
    const response = await api.post(`${API_ROUTE_PREFIX}/train-models`);
    return response;
  } catch (error) {
    console.error('Error training models:', error);
    throw error;
  }
};

export const generatePredictions = async (lat, lng) => {
  try {
    const response = await api.post(`${API_ROUTE_PREFIX}/generate-predictions`, {
      lat,
      lng
    });
    return response;
  } catch (error) {
    console.error('Error generating predictions:', error);
    throw error;
  }
}; 
