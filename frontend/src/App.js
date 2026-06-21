import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, Layout, theme as antdTheme } from 'antd';
import { CloudOutlined } from '@ant-design/icons';
import styled, { createGlobalStyle } from 'styled-components';
import HomePage from './pages/HomePage';

const { Header, Content } = Layout;

const GlobalStyle = createGlobalStyle`
  html,
  body,
  #root {
    min-height: 100%;
    background: #050507;
  }

  body {
    margin: 0;
    color: rgba(255, 255, 255, 0.9);
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
    -webkit-font-smoothing: antialiased;
    text-rendering: optimizeLegibility;
  }

  * {
    box-sizing: border-box;
  }

  ::selection {
    background: rgba(10, 132, 255, 0.35);
  }

  .ant-message-notice-content {
    background: rgba(28, 28, 30, 0.88);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 14px;
    color: rgba(255, 255, 255, 0.92);
    box-shadow: 0 24px 70px rgba(0, 0, 0, 0.45);
    backdrop-filter: blur(22px);
  }
`;

const StyledLayout = styled(Layout)`
  min-height: 100vh;
  background: #050507;
`;

const StyledHeader = styled(Header)`
  height: 58px;
  background: rgba(22, 22, 26, 0.72);
  padding: 0 22px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.09);
  box-shadow: 0 18px 60px rgba(0, 0, 0, 0.32);
  backdrop-filter: blur(28px) saturate(1.35);
  position: sticky;
  top: 0;
  z-index: 1000;
`;

const StyledContent = styled(Content)`
  padding: 28px;
  background: transparent;

  @media (max-width: 768px) {
    padding: 16px;
  }
`;

const AppTitle = styled.h1`
  color: rgba(255, 255, 255, 0.92);
  margin: 0;
  font-size: 15px;
  font-weight: 600;
  letter-spacing: 0;
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;

  .anticon {
    color: #0a84ff;
    font-size: 17px;
  }
`;

function App() {
  return (
    <ConfigProvider
      theme={{
        algorithm: antdTheme.darkAlgorithm,
        token: {
          colorPrimary: '#0a84ff',
          colorInfo: '#0a84ff',
          colorBgBase: '#050507',
          colorBgContainer: 'rgba(28, 28, 30, 0.82)',
          colorBorder: 'rgba(255, 255, 255, 0.12)',
          colorText: 'rgba(255, 255, 255, 0.9)',
          colorTextSecondary: 'rgba(235, 235, 245, 0.62)',
          borderRadius: 14,
          fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Helvetica Neue", Arial, sans-serif',
        },
      }}
    >
      <GlobalStyle />
      <Router>
        <StyledLayout>
          <StyledHeader>
            <AppTitle>
              <CloudOutlined />
              AQI Predictor
            </AppTitle>
          </StyledHeader>
          <StyledContent>
            <Routes>
              <Route path="/" element={<HomePage />} />
            </Routes>
          </StyledContent>
        </StyledLayout>
      </Router>
    </ConfigProvider>
  );
}

export default App;
