import React, { ReactNode } from 'react';
import { Layout, Menu, theme } from 'antd';
import { Link, useLocation } from 'react-router-dom';
import { DashboardOutlined, BarChartOutlined } from '@ant-design/icons';

const { Header, Content, Footer, Sider } = Layout;

interface MainLayoutProps {
  children: ReactNode;
}

const MainLayout: React.FC<MainLayoutProps> = ({ children }) => {
  const location = useLocation();
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  // 根据当前路径确定选中的菜单项
  const selectedKey = location.pathname === '/details' ? '2' : '1';

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ 
        display: 'flex', 
        alignItems: 'center', 
        background: colorBgContainer,
        padding: '0 16px',
        position: 'fixed',
        top: 0,
        width: '100%',
        zIndex: 1,
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)'
      }}>
        <div style={{ 
          fontSize: '20px', 
          fontWeight: 'bold', 
          marginRight: '40px'
        }}>
          数据分析与可视化平台
        </div>
        <Menu
          theme="light"
          mode="horizontal"
          selectedKeys={[selectedKey]}
          style={{ flex: 1, minWidth: 0 }}
          items={[
            {
              key: '1',
              icon: <DashboardOutlined />,
              label: <Link to="/">数据概览</Link>,
            },
            {
              key: '2',
              icon: <BarChartOutlined />,
              label: <Link to="/details">数据详情</Link>,
            },
          ]}
        />
      </Header>
      <Content style={{ padding: '24px', marginTop: 64 }}>
        <div
          style={{
            background: colorBgContainer,
            padding: 24,
            borderRadius: borderRadiusLG,
            minHeight: 'calc(100vh - 140px)',
          }}
        >
          {children}
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>
        数据分析与可视化平台 ©{new Date().getFullYear()}
      </Footer>
    </Layout>
  );
};

export default MainLayout; 