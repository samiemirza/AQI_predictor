import React from 'react';
import { Card, Statistic, Table, Tag, Empty, Alert } from 'antd';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
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

const ChartContainer = styled.div`
  height: 300px;
  margin: 20px 0;
`;

const StatsContainer = styled.div`
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 16px;
  margin: 20px 0;
`;

const getAQIColor = (aqi) => {
  if (aqi <= 50) return '#66bb6a';
  if (aqi <= 100) return '#ffa500';
  if (aqi <= 150) return '#ff7e00';
  if (aqi <= 200) return '#ff0000';
  if (aqi <= 300) return '#8f3f97';
  return '#7e0023';
};

const getAQICategory = (aqi) => {
  if (aqi <= 50) return { text: 'Good', color: '#66bb6a' };
  if (aqi <= 100) return { text: 'Moderate', color: '#ffa500' };
  if (aqi <= 150) return { text: 'Unhealthy for Sensitive Groups', color: 'warning' };
  if (aqi <= 200) return { text: 'Unhealthy', color: 'error' };
  if (aqi <= 300) return { text: 'Very Unhealthy', color: 'error' };
  return { text: 'Hazardous', color: 'error' };
};

const PredictionWidget = ({ data, location }) => {
  if (!data || !data.length) {
    return (
      <WidgetCard title="AQI Predictions">
        <Empty description="No predictions available. Generate predictions first." />
      </WidgetCard>
    );
  }

  // Prepare chart data
  const chartData = data.map(item => ({
    time: new Date(item.timestamp).toLocaleDateString(),
    aqi: item.predicted_aqi,
    category: getAQICategory(item.predicted_aqi).text
  }));

  // Calculate statistics
  const avgAQI = data.reduce((sum, item) => sum + item.predicted_aqi, 0) / data.length;
  const maxAQI = Math.max(...data.map(item => item.predicted_aqi));
  const minAQI = Math.min(...data.map(item => item.predicted_aqi));

  // Check for hazardous levels
  const hazardousCount = data.filter(item => item.predicted_aqi > 150).length;

  // Prepare table data
  const tableData = data.map((item, index) => ({
    key: index,
    time: new Date(item.timestamp).toLocaleString(),
    aqi: item.predicted_aqi.toFixed(1),
    category: getAQICategory(item.predicted_aqi).text,
    color: getAQICategory(item.predicted_aqi).color
  }));

  const columns = [
    {
      title: 'Time',
      dataIndex: 'time',
      key: 'time',
      width: '40%',
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
    <WidgetCard title="AQI Predictions">
      {/* Hazardous Alert */}
      {hazardousCount > 0 && (
        <Alert
          message={`🚨 ${hazardousCount} hazardous readings predicted`}
          description="Some predicted AQI values exceed the hazardous threshold (150)."
          type="error"
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
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="time" 
              angle={-45}
              textAnchor="end"
              height={80}
              fontSize={12}
            />
            <YAxis 
              domain={[0, 500]}
              label={{ value: 'AQI', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              formatter={(value) => [`${value} AQI`, 'Predicted AQI']}
              labelFormatter={(label) => `Date: ${label}`}
            />
            <Line
              type="monotone"
              dataKey="aqi"
              stroke="#667eea"
              strokeWidth={3}
              dot={{ fill: '#667eea', strokeWidth: 2, r: 4 }}
              activeDot={{ r: 6 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </ChartContainer>

      {/* Predictions Table */}
      <div style={{ marginTop: '20px' }}>
        <h4>📋 Detailed Predictions</h4>
        <Table
          dataSource={tableData}
          columns={columns}
          pagination={false}
          size="small"
          scroll={{ y: 200 }}
        />
      </div>

      {location && (
        <div style={{ marginTop: '16px', fontSize: '14px', color: '#666', textAlign: 'center' }}>
          📍 Predictions for {location.name || `(${location.lat.toFixed(4)}, ${location.lng.toFixed(4)})`}
        </div>
      )}
    </WidgetCard>
  );
};

export default PredictionWidget; 