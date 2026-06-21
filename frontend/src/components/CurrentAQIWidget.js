import React from 'react';
import { Alert, Card, Empty, Progress, Spin, Statistic, Tag } from 'antd';
import { CloudOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const WidgetCard = styled(Card)`
  height: 100%;
  border-radius: 8px;
  border: 1px solid #d9e2ec;
  box-shadow: 0 12px 32px rgba(15, 23, 42, 0.06);

  .ant-card-head {
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
  }
  .ant-card-head-title {
    color: #0f172a;
    font-weight: 600;
  }
`;

const AQIContainer = styled.div`
  text-align: center;
  padding: 18px 0 8px;
`;

const AQICategory = styled.div`
  margin-top: 16px;
  font-size: 18px;
  font-weight: 600;
`;

const PollutantGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 8px;
  margin-top: 18px;

  @media (max-width: 640px) {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
`;

const PollutantCell = styled.div`
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 8px;
  text-align: left;
`;

const PollutantName = styled.div`
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
`;

const PollutantValue = styled.div`
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
  margin-top: 2px;
`;

const getAQIColor = (aqi) => {
  if (aqi <= 50) return { color: '#00a65a', category: 'Good', status: 'success' };
  if (aqi <= 100) return { color: '#b7791f', category: 'Moderate', status: 'warning' };
  if (aqi <= 150) return { color: '#ff7e00', category: 'Unhealthy for Sensitive Groups', status: 'warning' };
  if (aqi <= 200) return { color: '#dc2626', category: 'Unhealthy', status: 'error' };
  if (aqi <= 300) return { color: '#8f3f97', category: 'Very Unhealthy', status: 'error' };
  return { color: '#7e0023', category: 'Hazardous', status: 'error' };
};

const getAQIIcon = (aqi) => {
  if (aqi === null || aqi === undefined) return <CloudOutlined style={{ color: '#64748b' }} />;
  if (aqi <= 50) return <CheckCircleOutlined style={{ color: '#66bb6a' }} />;
  if (aqi <= 100) return <CloudOutlined style={{ color: '#ffa500' }} />;
  return <WarningOutlined style={{ color: '#ff0000' }} />;
};

const CurrentAQIWidget = ({ data, location, loading, error }) => {
  if (loading && !data) {
    return (
      <WidgetCard title="Current Air Quality" extra={getAQIIcon(null)}>
        <div style={{ minHeight: 260, display: 'grid', placeItems: 'center' }}>
          <Spin tip="Fetching current AQI" />
        </div>
      </WidgetCard>
    );
  }

  if (error) {
    return (
      <WidgetCard title="Current Air Quality" extra={getAQIIcon(null)}>
        <Alert
          type="error"
          showIcon
          message="Current AQI unavailable"
          description={error}
        />
      </WidgetCard>
    );
  }

  if (!data) {
    return (
      <WidgetCard title="Current Air Quality" extra={getAQIIcon(null)}>
        <Empty description="No current AQI data available" />
      </WidgetCard>
    );
  }

  const aqiValue = data.aqi_numerical ?? (data.main_aqi ? data.main_aqi * 50 : null);
  if (aqiValue === null || Number.isNaN(Number(aqiValue))) {
    return (
      <WidgetCard title="Current Air Quality" extra={getAQIIcon(null)}>
        <Empty description="Current AQI value was not returned by the API" />
      </WidgetCard>
    );
  }

  const aqiInfo = getAQIColor(aqiValue);
  const category = data.aqi_category || aqiInfo.category;
  const percentage = Math.max(0, Math.min(100, (aqiValue / 500) * 100));
  const pollutantEntries = Object.entries(data.pollutants || {}).filter(([, value]) => Number.isFinite(Number(value)));

  return (
    <WidgetCard
      title="Current Air Quality"
      extra={getAQIIcon(aqiValue)}
      loading={loading}
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
            <Tag color={aqiInfo.color} style={{ fontSize: '14px', marginLeft: '8px' }}>
              {category}
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
          {category}
        </AQICategory>

        {data.dominant_pollutant && (
          <div style={{ marginTop: '16px' }}>
            <strong>Dominant Pollutant:</strong> {data.dominant_pollutant.toUpperCase()}
          </div>
        )}

        {pollutantEntries.length > 0 && (
          <PollutantGrid>
            {pollutantEntries.slice(0, 8).map(([name, value]) => (
              <PollutantCell key={name}>
                <PollutantName>{name.replace('_', '.')}</PollutantName>
                <PollutantValue>{Number(value).toFixed(1)}</PollutantValue>
              </PollutantCell>
            ))}
          </PollutantGrid>
        )}

        {location && (
          <div style={{ marginTop: '16px', fontSize: '14px', color: '#666' }}>
            {location.name || `(${location.lat.toFixed(4)}, ${location.lng.toFixed(4)})`}
          </div>
        )}
      </AQIContainer>
    </WidgetCard>
  );
};

export default CurrentAQIWidget;
