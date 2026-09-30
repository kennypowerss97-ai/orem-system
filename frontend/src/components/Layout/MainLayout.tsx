import React, { useState } from 'react';
import { Layout, Menu, theme, Dropdown, Space, Avatar, Drawer, Button, Grid } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  DashboardOutlined,
  TeamOutlined,
  UserOutlined,
  CalendarOutlined,
  FileTextOutlined,
  HomeOutlined,
  FormOutlined,
  BarChartOutlined,
  SettingOutlined,
  LogoutOutlined,
  MenuOutlined,
  ApartmentOutlined,
  BookOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Header, Sider, Content } = Layout;
const { useBreakpoint } = Grid;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileDrawerOpen, setMobileDrawerOpen] = useState(false);
  const screens = useBreakpoint();
  const isMobile = screens.md === false; // screens.md false ise ekran < 768px (mobil/tablet)

  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const handleMenuClick = ({ key }: { key: string }) => {
    navigate(key);
    if (isMobile) {
      setMobileDrawerOpen(false);
    }
  };

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Ana Panel' },
    { key: '/students', icon: <TeamOutlined />, label: 'Öğrenciler' },
    { key: '/programs', icon: <BookOutlined />, label: 'Destek Programları' },
    { key: '/therapists', icon: <UserOutlined />, label: 'Öğretmenler' },
    { key: '/branches', icon: <ApartmentOutlined />, label: 'Öğretmen Branşları' },
    { key: '/schedule', icon: <CalendarOutlined />, label: 'Ders Programı' },
    { key: '/sessions', icon: <FileTextOutlined />, label: 'Seanslar' },
    { key: '/rooms', icon: <HomeOutlined />, label: 'Odalar' },
    { key: '/iep', icon: <FormOutlined />, label: 'BEP & İlerleme' },
    { key: '/reports', icon: <BarChartOutlined />, label: 'Raporlar' },
    { key: '/settings', icon: <SettingOutlined />, label: 'Ayarlar' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      {/* Masaüstü Sider */}
      {!isMobile && (
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={(value) => setCollapsed(value)}
          theme="dark"
          width={240}
        >
          <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold' }}>
            {collapsed ? 'ÖREM' : 'ÖREM Yönetim'}
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>
      )}

      {/* Mobil Drawer Menü */}
      <Drawer
        title="ÖREM Yönetim Sistemi"
        placement="left"
        onClose={() => setMobileDrawerOpen(false)}
        open={mobileDrawerOpen}
        styles={{ body: { padding: 0, backgroundColor: '#001529' } }}
        width={260}
      >
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={handleMenuClick}
        />
      </Drawer>

      <Layout>
        <Header style={{
          padding: isMobile ? '0 16px' : '0 24px',
          background: colorBgContainer,
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          boxShadow: '0 1px 4px rgba(0,21,41,.08)',
          zIndex: 1
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            {isMobile && (
              <Button
                type="text"
                icon={<MenuOutlined style={{ fontSize: 18 }} />}
                onClick={() => setMobileDrawerOpen(true)}
              />
            )}
            <span style={{ fontWeight: 'bold', fontSize: isMobile ? '1.05rem' : '1.2rem', color: '#1890ff' }}>
              ÖREM
            </span>
          </div>

          <Dropdown menu={{ items: [{ key: 'logout', icon: <LogoutOutlined />, label: 'Çıkış Yap', onClick: handleLogout }] }}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              <span style={{ display: isMobile ? 'none' : 'inline' }}>
                {user?.username || 'Kullanıcı'}
              </span>
            </Space>
          </Dropdown>
        </Header>

        <Content style={{
          margin: isMobile ? '12px 8px' : '24px 16px',
          padding: isMobile ? 12 : 24,
          minHeight: 280,
          background: colorBgContainer,
          borderRadius: borderRadiusLG,
          overflowX: 'hidden'
        }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
