import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from 'antd';
import styled from 'styled-components';
import Navigation from './components/Navigation';
import HomePage from './pages/HomePage';
import AboutPage from './pages/AboutPage';

const { Header, Content } = Layout;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
`;

const StyledHeader = styled(Header)`
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 0 24px;
  display: flex;
  align-items: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`;

const StyledContent = styled(Content)`
  padding: 24px;
  background: #f5f5f5;
`;

const AppTitle = styled.h1`
  color: white;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
`;

function App() {
  return (
    <Router>
      <StyledLayout>
        <StyledHeader>
          <AppTitle>🌬️ AQI Predictor</AppTitle>
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