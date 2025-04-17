import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/lib/locale/zh_CN';
import MainLayout from './layouts/MainLayout';
import OverviewPage from './pages/Overview';
import DetailsPage from './pages/Details';
import { DateProvider } from './hooks/useDateContext';
import './App.css';

function App() {
  return (
    <ConfigProvider locale={zhCN}>
      <DateProvider>
        <Router>
          <MainLayout>
            <Routes>
              <Route path="/" element={<OverviewPage />} />
              <Route path="/details" element={<DetailsPage />} />
            </Routes>
          </MainLayout>
        </Router>
      </DateProvider>
    </ConfigProvider>
  );
}

export default App;
