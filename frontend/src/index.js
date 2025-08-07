import React from 'react';
import ReactDOM from 'react-dom/client';
import { ConfigProvider } from 'antd';
import App from './App';
import 'antd/dist/reset.css';

const root = ReactDOM.createRoot(document.getElementById('root'));

root.render(
  <React.StrictMode>
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#667eea',
          borderRadius: 8,
        },
      }}
    >
      <App />
    </ConfigProvider>
  </React.StrictMode>
); 