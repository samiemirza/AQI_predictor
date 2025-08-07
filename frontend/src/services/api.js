import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add API key
api.interceptors.request.use((config) => {
  const apiKey = localStorage.getItem('openweather_api_key');
  if (apiKey) {
    config.headers['X-API-Key'] = apiKey;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    throw error;
  }
);

export const setApiKey = (apiKey) => {
  localStorage.setItem('openweather_api_key', apiKey);
};

export const getApiKey = () => {
  return localStorage.getItem('openweather_api_key');
};

// API endpoints
export const fetchCurrentAQI = async (lat, lng) => {
  try {
    const response = await api.get('/api/current-aqi', {
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
    const response = await api.get('/api/predictions', {
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
    const response = await api.post('/api/update-data', {
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
    const response = await api.post('/api/train-models');
    return response;
  } catch (error) {
    console.error('Error training models:', error);
    throw error;
  }
};

export const generatePredictions = async (lat, lng) => {
  try {
    const response = await api.post('/api/generate-predictions', {
      lat,
      lng
    });
    return response;
  } catch (error) {
    console.error('Error generating predictions:', error);
    throw error;
  }
}; 