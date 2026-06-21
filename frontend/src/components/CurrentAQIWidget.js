import React from 'react';
import { Alert, Card, Empty, Progress, Spin, Statistic, Tag } from 'antd';
import { CloudOutlined, WarningOutlined, CheckCircleOutlined } from '@ant-design/icons';
import styled from 'styled-components';

const WidgetCard = styled(Card)`
  height: 100%;
  background: rgba(28, 28, 30, 0.72);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow:
    0 24px 70px rgba(0, 0, 0, 0.36),
    inset 0 1px 0 rgba(255, 255, 255, 0.08);
  backdrop-filter: blur(28px) saturate(1.35);
  overflow: hidden;

  .ant-card-head {
    background: rgba(255, 255, 255, 0.03);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    min-height: 52px;
  }

  .ant-card-head-title {
    color: rgba(255, 255, 255, 0.92);
    font-weight: 600;
  }

  .ant-card-body {
    color: rgba(255, 255, 255, 0.88);
  }

  .ant-statistic-title,
  .ant-empty-description {
    color: rgba(235, 235, 245, 0.58);
  }

  .ant-progress-bg {
    box-shadow: 0 0 18px currentColor;
  }

  .ant-alert {
    background: rgba(255, 69, 58, 0.12);
    border-color: rgba(255, 69, 58, 0.24);
    border-radius: 16px;
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
  background: rgba(118, 118, 128, 0.14);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  padding: 10px;
  text-align: left;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
`;

const PollutantName = styled.div`
  color: rgba(235, 235, 245, 0.52);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
`;

const PollutantValue = styled.div`
  color: rgba(255, 255, 255, 0.92);
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
            <Tag color={aqiInfo.color} style={{ fontSize: '14px', marginLeft: '8px', borderRadius: '999px' }}>
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
          <div style={{ marginTop: '16px', fontSize: '14px', color: 'rgba(235, 235, 245, 0.58)' }}>
            {location.name || `(${location.lat.toFixed(4)}, ${location.lng.toFixed(4)})`}
          </div>
        )}
      </AQIContainer>
    </WidgetCard>
  );
};

export default CurrentAQIWidget;
