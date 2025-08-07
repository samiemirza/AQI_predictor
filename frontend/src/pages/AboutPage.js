import React from 'react';
import { Card, Row, Col, Statistic, Divider, Typography, Space } from 'antd';
import { 
  CloudOutlined, 
  RobotOutlined, 
  GlobalOutlined, 
  ThunderboltOutlined,
  BarChartOutlined,
  SafetyOutlined
} from '@ant-design/icons';
import styled from 'styled-components';

const { Title, Paragraph, Text } = Typography;

const PageContainer = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px;
`;

const FeatureCard = styled(Card)`
  height: 100%;
  text-align: center;
  transition: transform 0.3s ease;
  
  &:hover {
    transform: translateY(-5px);
  }
`;

const AboutPage = () => {
  return (
    <PageContainer>
      <Title level={1}>About AQI Prediction Project</Title>
      
      <Card style={{ marginBottom: '24px' }}>
        <Title level={2}>Air Quality Index (AQI) Prediction System</Title>
        <Paragraph>
          This project uses machine learning to predict air quality index values for locations worldwide.
          It combines real-time air pollution data with advanced forecasting algorithms to provide
          accurate predictions up to 5 days in advance.
        </Paragraph>
      </Card>

      {/* Key Features */}
      <Title level={3}>Key Features</Title>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} lg={8}>
          <FeatureCard>
            <GlobalOutlined style={{ fontSize: '48px', color: '#1890ff', marginBottom: '16px' }} />
            <Title level={4}>Global Coverage</Title>
            <Paragraph>Predict AQI for any location worldwide with interactive world map</Paragraph>
          </FeatureCard>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <FeatureCard>
            <RobotOutlined style={{ fontSize: '48px', color: '#52c41a', marginBottom: '16px' }} />
            <Title level={4}>Machine Learning</Title>
            <Paragraph>Uses multiple ML models (Random Forest, Neural Networks) for accurate predictions</Paragraph>
          </FeatureCard>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <FeatureCard>
            <CloudOutlined style={{ fontSize: '48px', color: '#722ed1', marginBottom: '16px' }} />
            <Title level={4}>Real-time Data</Title>
            <Paragraph>Fetches live air pollution data from OpenWeatherMap API</Paragraph>
          </FeatureCard>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <FeatureCard>
            <ThunderboltOutlined style={{ fontSize: '48px', color: '#fa8c16', marginBottom: '16px' }} />
            <Title level={4}>5-Day Forecast</Title>
            <Paragraph>Predicts air quality up to 5 days in advance with hourly granularity</Paragraph>
          </FeatureCard>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <FeatureCard>
            <BarChartOutlined style={{ fontSize: '48px', color: '#eb2f96', marginBottom: '16px' }} />
            <Title level={4}>Interactive Dashboard</Title>
            <Paragraph>Beautiful visualizations and real-time updates with React</Paragraph>
          </FeatureCard>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <FeatureCard>
            <SafetyOutlined style={{ fontSize: '48px', color: '#f5222d', marginBottom: '16px' }} />
            <Title level={4}>Health Alerts</Title>
            <Paragraph>Automatic alerts for hazardous air quality conditions</Paragraph>
          </FeatureCard>
        </Col>
      </Row>

      {/* How It Works */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={3}>How It Works</Title>
        <Row gutter={[16, 16]}>
          <Col span={24}>
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <div>
                <Title level={4}>1. Data Collection</Title>
                <Paragraph>
                  Fetches historical air pollution data (CO, NO2, PM2.5, PM10, O3, SO2, etc.) from OpenWeatherMap API
                  for the past 5 days to build a comprehensive dataset.
                </Paragraph>
              </div>
              <div>
                <Title level={4}>2. Feature Engineering</Title>
                <Paragraph>
                  Creates time-based features, pollutant ratios, change rates, and rolling statistics to enhance
                  the predictive power of the models.
                </Paragraph>
              </div>
              <div>
                <Title level={4}>3. Model Training</Title>
                <Paragraph>
                  Trains multiple ML models (Random Forest, Ridge Regression, Neural Networks) and selects
                  the best performer based on RMSE and other metrics.
                </Paragraph>
              </div>
              <div>
                <Title level={4}>4. Prediction</Title>
                <Paragraph>
                  Uses the trained model to forecast future AQI values for the next 5 days with hourly precision.
                </Paragraph>
              </div>
              <div>
                <Title level={4}>5. Visualization</Title>
                <Paragraph>
                  Displays results with interactive charts, health alerts, and comprehensive statistics
                  in a modern React dashboard.
                </Paragraph>
              </div>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* Model Performance */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={3}>Model Performance</Title>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={8}>
            <Statistic
              title="Current Model"
              value="Random Forest v6"
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col xs={24} sm={8}>
            <Statistic
              title="RMSE"
              value={8.26}
              precision={2}
              valueStyle={{ color: '#52c41a' }}
              suffix="(Lower is better)"
            />
          </Col>
          <Col xs={24} sm={8}>
            <Statistic
              title="R² Score"
              value={0.796}
              precision={3}
              valueStyle={{ color: '#722ed1' }}
              suffix="(79.6% variance explained)"
            />
          </Col>
        </Row>
      </Card>

      {/* Technical Stack */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={3}>Technical Stack</Title>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12}>
            <Title level={4}>Frontend</Title>
            <ul>
              <li><Text strong>React 18</Text> - Modern UI framework</li>
              <li><Text strong>Ant Design</Text> - Professional UI components</li>
              <li><Text strong>React Leaflet</Text> - Interactive maps</li>
              <li><Text strong>Recharts</Text> - Beautiful data visualizations</li>
              <li><Text strong>Styled Components</Text> - CSS-in-JS styling</li>
            </ul>
          </Col>
          <Col xs={24} sm={12}>
            <Title level={4}>Backend</Title>
            <ul>
              <li><Text strong>Python</Text> - Core programming language</li>
              <li><Text strong>Scikit-learn</Text> - Machine learning library</li>
              <li><Text strong>Pandas</Text> - Data manipulation</li>
              <li><Text strong>OpenWeatherMap API</Text> - Air pollution data source</li>
              <li><Text strong>Flask/FastAPI</Text> - REST API framework</li>
            </ul>
          </Col>
        </Row>
      </Card>

      {/* Use Cases */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={3}>Use Cases</Title>
        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={8}>
            <Card size="small" title="🏥 Public Health">
              Early warning systems for air quality to protect public health
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card size="small" title="🏙️ Urban Planning">
              City air quality management and environmental planning
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card size="small" title="👤 Personal Health">
              Planning outdoor activities based on air quality forecasts
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card size="small" title="📋 Environmental Monitoring">
              Regulatory compliance and environmental standards monitoring
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card size="small" title="🔬 Research">
              Air quality pattern analysis and environmental research
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={8}>
            <Card size="small" title="🚨 Emergency Response">
              Rapid assessment during air quality emergencies
            </Card>
          </Col>
        </Row>
      </Card>

      {/* Getting Started */}
      <Card style={{ marginBottom: '24px' }}>
        <Title level={3}>Getting Started</Title>
        <ol>
          <li><Text strong>Set your OpenWeatherMap API key</Text> in the configuration</li>
          <li><Text strong>Select a location</Text> on the map or search for a city</li>
          <li><Text strong>Update data</Text> to collect latest air pollution data</li>
          <li><Text strong>Train models</Text> to create prediction models</li>
          <li><Text strong>Generate predictions</Text> to get 5-day AQI forecasts</li>
        </ol>
      </Card>

      <Divider />

      <div style={{ textAlign: 'center', color: '#666' }}>
        <Paragraph>
          <Text strong>Built with ❤️ for better air quality monitoring and prediction</Text>
        </Paragraph>
        <Paragraph>
          This project demonstrates a complete data science workflow from data collection to production deployment.
        </Paragraph>
      </div>
    </PageContainer>
  );
};

export default AboutPage; 