import React from 'react';
import { Card, Statistic, Progress, Tag, Empty } from 'antd';
import { CloudOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const WidgetCard = styled(Card)`
  height: 100%;
  .ant-card-head {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
  }
  .ant-card-head-title {
    color: white;
    font-weight: 600;
  }
`;

const AQIContainer = styled.div`
  text-align: center;
  padding: 20px 0;
`;

const AQICategory = styled.div`
  margin-top: 16px;
  font-size: 18px;
  font-weight: 600;
`;

const getAQIColor = (aqi) => {
  if (aqi <= 50) return { color: '#00e400', category: 'Good', status: 'success' };
  if (aqi <= 100) return { color: '#ffa500', category: 'Moderate', status: 'warning' };
  if (aqi <= 150) return { color: '#ff7e00', category: 'Unhealthy for Sensitive Groups', status: 'warning' };
  if (aqi <= 200) return { color: '#ff0000', category: 'Unhealthy', status: 'error' };
  if (aqi <= 300) return { color: '#8f3f97', category: 'Very Unhealthy', status: 'error' };
  return { color: '#7e0023', category: 'Hazardous', status: 'error' };
};

const getAQIIcon = (aqi) => {
  if (aqi <= 50) return <CheckCircleOutlined style={{ color: '#00e400' }} />;
  if (aqi <= 100) return <CloudOutlined style={{ color: '#ffa500' }} />;
  return <WarningOutlined style={{ color: '#ff0000' }} />;
};

const CurrentAQIWidget = ({ data, location }) => {
  if (!data) {
    return (
      <WidgetCard title="🌡️ Current Air Quality" extra={getAQIIcon(null)}>
        <Empty description="No current AQI data available" />
      </WidgetCard>
    );
  }

  const aqiValue = data.aqi_numerical || data.main_aqi * 50; // Convert 1-5 scale to 0-500
  const aqiInfo = getAQIColor(aqiValue);
  const percentage = (aqiValue / 500) * 100;

  return (
    <WidgetCard 
      title="🌡️ Current Air Quality" 
      extra={getAQIIcon(aqiValue)}
    >
      <AQIContainer>
        <Statistic
          title="Current AQI"
          value={aqiValue.toFixed(0)}
          valueStyle={{ 
            color: aqiInfo.color,
            fontSize: '48px',
            fontWeight: 'bold'
          }}
          suffix={
            <Tag color={aqiInfo.status} style={{ fontSize: '14px', marginLeft: '8px' }}>
              {aqiInfo.category}
            </Tag>
          }
        />
        
        <Progress
          percent={percentage}
          strokeColor={aqiInfo.color}
          showInfo={false}
          style={{ marginTop: '16px' }}
        />
        
        <AQICategory style={{ color: aqiInfo.color }}>
          {aqiInfo.category}
        </AQICategory>
        
        {data.dominant_pollutant && (
          <div style={{ marginTop: '16px' }}>
            <strong>Dominant Pollutant:</strong> {data.dominant_pollutant.toUpperCase()}
          </div>
        )}
        
        {location && (
          <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
            📍 {location.name || `(${location.lat.toFixed(4)}, ${location.lng.toFixed(4)})`}
          </div>
        )}
      </AQIContainer>
    </WidgetCard>
  );
};

export default CurrentAQIWidget; 