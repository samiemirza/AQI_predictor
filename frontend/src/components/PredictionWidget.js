import React from 'react';
import { Card, Statistic, Table, Tag, Empty, Alert, Spin } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
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

  .ant-empty-description,
  .ant-statistic-title {
    color: rgba(235, 235, 245, 0.58);
  }

  .ant-alert {
    background: rgba(255, 159, 10, 0.12);
    border-color: rgba(255, 159, 10, 0.24);
    border-radius: 16px;
  }

  .ant-table {
    background: transparent;
    color: rgba(255, 255, 255, 0.84);
  }

  .ant-table-container,
  .ant-table-cell {
    border-color: rgba(255, 255, 255, 0.08) !important;
  }

  .ant-table-thead > tr > th {
    background: rgba(118, 118, 128, 0.16) !important;
    color: rgba(235, 235, 245, 0.68) !important;
    font-weight: 600;
  }

  .ant-table-tbody > tr > td {
    background: rgba(255, 255, 255, 0.02);
  }

  .ant-table-tbody > tr:hover > td {
    background: rgba(10, 132, 255, 0.12) !important;
  }
`;

const ChartContainer = styled.div`
  height: 300px;
  margin: 20px 0;
`;

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
  margin: 18px 0;

  .ant-statistic {
    background: rgba(118, 118, 128, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 12px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
  }

  @media (max-width: 640px) {
    grid-template-columns: 1fr;
  }
`;

const getAQIColor = (aqi) => {
  if (aqi <= 50) return '#00a65a';
  if (aqi <= 100) return '#b7791f';
  if (aqi <= 150) return '#ff7e00';
  if (aqi <= 200) return '#dc2626';
  if (aqi <= 300) return '#8f3f97';
  return '#7e0023';
};

const getAQICategory = (aqi) => {
  if (aqi <= 50) return { text: 'Good', color: 'green' };
  if (aqi <= 100) return { text: 'Moderate', color: 'gold' };
  if (aqi <= 150) return { text: 'Unhealthy for Sensitive Groups', color: 'orange' };
  if (aqi <= 200) return { text: 'Unhealthy', color: 'red' };
  if (aqi <= 300) return { text: 'Very Unhealthy', color: 'purple' };
  return { text: 'Hazardous', color: 'volcano' };
};

const PredictionWidget = ({ data, location, loading, error }) => {
  if (loading && (!data || !data.length)) {
    return (
      <WidgetCard title="AQI Forecast">
        <div style={{ minHeight: 260, display: 'grid', placeItems: 'center' }}>
          <Spin tip="Fetching forecast" />
        </div>
      </WidgetCard>
    );
  }

  if (error) {
    return (
      <WidgetCard title="AQI Forecast">
        <Alert
          type="error"
          showIcon
          message="Forecast unavailable"
          description={error}
        />
      </WidgetCard>
    );
  }

  if (!data || !data.length) {
    return (
      <WidgetCard title="AQI Forecast">
        <Empty description="Select a location to fetch forecast horizons." />
      </WidgetCard>
    );
  }

  // Prepare chart data
  const chartData = data.map(item => ({
    time: `+${item.hour_ahead || 0}h`,
    date: new Date(item.timestamp).toLocaleString(),
    aqi: Number(item.predicted_aqi),
    category: item.aqi_category || getAQICategory(item.predicted_aqi).text
  }));

  // Calculate statistics
  const values = data.map(item => Number(item.predicted_aqi));
  const avgAQI = values.reduce((sum, item) => sum + item, 0) / values.length;
  const maxAQI = Math.max(...values);
  const minAQI = Math.min(...values);

  // Check for hazardous levels
  const hazardousCount = values.filter(item => item > 150).length;

  // Prepare table data
  const tableData = data.map((item, index) => ({
    key: index,
    horizon: `${item.hour_ahead || 0}h`,
    time: new Date(item.timestamp).toLocaleString(),
    aqi: Number(item.predicted_aqi).toFixed(1),
    category: item.aqi_category || getAQICategory(item.predicted_aqi).text,
    color: getAQICategory(item.predicted_aqi).color
  }));

  const columns = [
    {
      title: 'Horizon',
      dataIndex: 'horizon',
      key: 'horizon',
      width: 90,
    },
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
      width: '38%',
    },
    {
      title: 'AQI',
      dataIndex: 'aqi',
      key: 'aqi',
      width: '30%',
      render: (aqi) => (
        <span style={{ fontWeight: 'bold', color: getAQIColor(parseFloat(aqi)) }}>
          {aqi}
        </span>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: '30%',
      render: (category, record) => (
        <Tag color={record.color}>
          {category}
        </Tag>
      ),
    },
  ];

  return (
    <WidgetCard title="AQI Forecast" loading={loading}>
      {/* Hazardous Alert */}
      {hazardousCount > 0 && (
        <Alert
          message={`${hazardousCount} forecast horizons exceed AQI 150`}
          description="Sensitive groups and outdoor activity planning need attention."
          type="warning"
          showIcon
          style={{ marginBottom: '16px' }}
        />
      )}

      {/* Statistics */}
      <StatsContainer>
        <Statistic
          title="Average AQI"
          value={avgAQI.toFixed(1)}
          valueStyle={{ color: getAQIColor(avgAQI) }}
        />
        <Statistic
          title="Maximum AQI"
          value={maxAQI.toFixed(1)}
          valueStyle={{ color: getAQIColor(maxAQI) }}
        />
        <Statistic
          title="Minimum AQI"
          value={minAQI.toFixed(1)}
          valueStyle={{ color: getAQIColor(minAQI) }}
        />
      </StatsContainer>

      {/* Chart */}
      <ChartContainer>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid stroke="rgba(255,255,255,0.08)" strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              height={42}
              fontSize={12}
              tick={{ fill: 'rgba(235, 235, 245, 0.58)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.12)' }}
              tickLine={{ stroke: 'rgba(255,255,255,0.12)' }}
            />
            <YAxis
              domain={[0, 500]}
              tick={{ fill: 'rgba(235, 235, 245, 0.58)' }}
              axisLine={{ stroke: 'rgba(255,255,255,0.12)' }}
              tickLine={{ stroke: 'rgba(255,255,255,0.12)' }}
              label={{ value: 'AQI', angle: -90, position: 'insideLeft', fill: 'rgba(235, 235, 245, 0.58)' }}
            />
            <Tooltip
              contentStyle={{
                background: 'rgba(28, 28, 30, 0.92)',
                border: '1px solid rgba(255,255,255,0.14)',
                borderRadius: 14,
                boxShadow: '0 18px 50px rgba(0,0,0,0.38)',
                color: 'rgba(255,255,255,0.9)'
              }}
              labelStyle={{ color: 'rgba(255,255,255,0.9)' }}
              formatter={(value) => [`${Number(value).toFixed(1)} AQI`, 'Predicted AQI']}
              labelFormatter={(label, payload) => {
                const point = payload?.[0]?.payload;
                return point ? `${label} (${point.date})` : label;
              }}
            />
            <Line
              type="monotone"
              dataKey="aqi"
              stroke="#0a84ff"
              strokeWidth={3}
              dot={{ fill: '#0a84ff', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>

      {/* Predictions Table */}
      <div style={{ marginTop: '20px' }}>
        <Table
          dataSource={tableData}
          columns={columns}
          pagination={false}
          size="small"
          scroll={{ y: 200 }}
        />
      </div>

      {location && (
        <div style={{ marginTop: '16px', fontSize: '14px', color: 'rgba(235, 235, 245, 0.58)', textAlign: 'center' }}>
          Forecast for {location.name || `(${location.lat.toFixed(4)}, ${location.lng.toFixed(4)})`}
        </div>
      )}
    </WidgetCard>
  );
};

export default PredictionWidget;
