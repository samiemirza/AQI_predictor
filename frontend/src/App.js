import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import { CloudOutlined } from '@ant-design/icons';
import styled from 'styled-components';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';

const { Header, Content } = Layout;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
  background: #eef3f7;
`;

const StyledHeader = styled(Header)`
  background: #0f172a;
  padding: 0 28px;
  display: flex;
  align-items: center;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.18);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const StyledContent = styled(Content)`
  padding: 28px;
  background:
    linear-gradient(180deg, rgba(225, 235, 244, 0.9) 0%, rgba(248, 250, 252, 1) 280px),
    #f8fafc;

  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const AppTitle = styled.h1`
  color: white;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  letter-spacing: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
`;

function App() {
  return (
    <Router>
      <StyledLayout>
        <StyledHeader>
          <AppTitle>
            <CloudOutlined />
            AQI Predictor
          </AppTitle>
          <Navigation />
        </StyledHeader>
        <StyledContent>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </StyledContent>
      </StyledLayout>
    </Router>
  );
}

export default App;
