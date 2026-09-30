import os

BASE_DIR = r"C:\Users\Pc\.gemini\antigravity\scratch\orem-system\frontend"

FILES = {
    "src/types/index.ts": """export interface User {
  id: string;
  username: string;
  email: string;
  role: 'admin' | 'therapist' | 'staff';
}

export interface Guardian {
  name: string;
  phone: string;
  email: string;
  relationship: string;
}

export interface RamReport {
  reportNumber: string;
  issuingRam: string;
  issueDate: string;
  expiryDate: string;
}

export interface AllocatedModule {
  moduleId: string;
  quotaHours: number;
}

export interface Student {
  id: string;
  firstName: string;
  lastName: string;
  tcKimlik: string;
  birthDate: string;
  gender: string;
  disabilityType: string;
  status: 'active' | 'inactive';
  guardian?: Guardian;
  ramReport?: RamReport;
  allocatedModules?: AllocatedModule[];
}

export interface TherapistSpecialization {
  moduleId: string;
}

export interface TherapistAvailability {
  dayOfWeek: number;
  startTime: string;
  endTime: string;
}

export interface Therapist {
  id: string;
  firstName: string;
  lastName: string;
  title: string;
  specializations: TherapistSpecialization[];
  availabilities: TherapistAvailability[];
  weeklyHours: number;
  currentWorkload: number;
}

export interface TherapyModule {
  id: string;
  name: string;
  color: string;
}

export interface Room {
  id: string;
  name: string;
  code: string;
  capacity: number;
  supportedModules: string[];
  status: 'active' | 'maintenance';
}

export interface SessionParticipant {
  studentId: string;
  attendanceStatus?: 'present' | 'absent' | 'excused';
}

export interface TherapySession {
  id: string;
  moduleId: string;
  therapistId: string;
  roomId: string;
  date: string;
  startTime: string;
  endTime: string;
  status: 'planned' | 'completed' | 'student_absent' | 'cancelled';
  participants: SessionParticipant[];
}

export interface IepGoal {
  id: string;
  description: string;
  status: 'not_started' | 'in_progress' | 'achieved';
}

export interface IepPlan {
  id: string;
  studentId: string;
  moduleId: string;
  startDate: string;
  endDate: string;
  goals: IepGoal[];
}

export interface ProgressRecord {
  id: string;
  sessionId: string;
  goalId: string;
  notes: string;
  rating: number;
}

export interface DashboardStats {
  totalStudents: number;
  totalTherapists: number;
  todaySessions: number;
  attendanceRate: number;
  expiredReports: number;
  weeklyOccupancy: number;
  pendingMakeups: number;
  therapistDistribution: { name: string; count: number }[];
}

export interface Alert {
  id: string;
  message: string;
  type: 'warning' | 'error' | 'info';
  date: string;
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
}
""",
    "src/api/client.ts": """import axios from 'axios';
import { useAuthStore } from '../store/authStore';

const apiClient = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      useAuthStore.getState().logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default apiClient;
""",
    "src/api/auth.ts": """import apiClient from './client';
import { User } from '../types';

export const login = async (credentials: any): Promise<{ user: User; token: string }> => {
  const res = await apiClient.post('/auth/login', credentials);
  return res.data;
};

export const register = async (userData: any): Promise<void> => {
  await apiClient.post('/auth/register', userData);
};

export const getMe = async (): Promise<User> => {
  const res = await apiClient.get('/auth/me');
  return res.data;
};
""",
    "src/api/students.ts": """import apiClient from './client';
import { Student, PaginatedResponse } from '../types';

export const getStudents = async (params?: any): Promise<PaginatedResponse<Student>> => {
  const res = await apiClient.get('/students', { params });
  return res.data;
};

export const getStudent = async (id: string): Promise<Student> => {
  const res = await apiClient.get(`/students/${id}`);
  return res.data;
};

export const createStudent = async (data: any): Promise<Student> => {
  const res = await apiClient.post('/students', data);
  return res.data;
};

export const updateStudent = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.put(`/students/${id}`, data);
  return res.data;
};

export const deleteStudent = async (id: string): Promise<void> => {
  await apiClient.delete(`/students/${id}`);
};

export const addGuardian = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.post(`/students/${id}/guardian`, data);
  return res.data;
};

export const addRamReport = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.post(`/students/${id}/ram-report`, data);
  return res.data;
};

export const addAllocatedModule = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.post(`/students/${id}/modules`, data);
  return res.data;
};

export const getStudentSchedule = async (id: string): Promise<any> => {
  const res = await apiClient.get(`/students/${id}/schedule`);
  return res.data;
};
""",
    "src/api/therapists.ts": """import apiClient from './client';
import { Therapist, PaginatedResponse } from '../types';

export const getTherapists = async (params?: any): Promise<PaginatedResponse<Therapist>> => {
  const res = await apiClient.get('/therapists', { params });
  return res.data;
};

export const getTherapist = async (id: string): Promise<Therapist> => {
  const res = await apiClient.get(`/therapists/${id}`);
  return res.data;
};

export const createTherapist = async (data: any): Promise<Therapist> => {
  const res = await apiClient.post('/therapists', data);
  return res.data;
};

export const updateTherapist = async (id: string, data: any): Promise<Therapist> => {
  const res = await apiClient.put(`/therapists/${id}`, data);
  return res.data;
};

export const addSpecialization = async (id: string, data: any): Promise<Therapist> => {
  const res = await apiClient.post(`/therapists/${id}/specializations`, data);
  return res.data;
};

export const addAvailability = async (id: string, data: any): Promise<Therapist> => {
  const res = await apiClient.post(`/therapists/${id}/availability`, data);
  return res.data;
};

export const getTherapistSchedule = async (id: string): Promise<any> => {
  const res = await apiClient.get(`/therapists/${id}/schedule`);
  return res.data;
};

export const getTherapistWorkload = async (id: string): Promise<any> => {
  const res = await apiClient.get(`/therapists/${id}/workload`);
  return res.data;
};
""",
    "src/api/sessions.ts": """import apiClient from './client';
import { TherapySession, PaginatedResponse } from '../types';

export const getSessions = async (params?: any): Promise<PaginatedResponse<TherapySession>> => {
  const res = await apiClient.get('/sessions', { params });
  return res.data;
};

export const getSession = async (id: string): Promise<TherapySession> => {
  const res = await apiClient.get(`/sessions/${id}`);
  return res.data;
};

export const markAttendance = async (id: string, data: any): Promise<TherapySession> => {
  const res = await apiClient.post(`/sessions/${id}/attendance`, data);
  return res.data;
};

export const cancelSession = async (id: string, reason: string): Promise<TherapySession> => {
  const res = await apiClient.post(`/sessions/${id}/cancel`, { reason });
  return res.data;
};

export const getTodaySessions = async (): Promise<TherapySession[]> => {
  const res = await apiClient.get('/sessions/today');
  return res.data;
};
""",
    "src/api/schedule.ts": """import apiClient from './client';

export const generateSchedule = async (startDate: string, endDate: string): Promise<any> => {
  const res = await apiClient.post('/schedule/generate', { startDate, endDate });
  return res.data;
};

export const addStudentToSchedule = async (studentId: string, data: any): Promise<any> => {
  const res = await apiClient.post(`/schedule/student/${studentId}`, data);
  return res.data;
};

export const getWeeklySchedule = async (params: any): Promise<any> => {
  const res = await apiClient.get('/schedule/weekly', { params });
  return res.data;
};

export const moveSession = async (sessionId: string, newTime: any): Promise<any> => {
  const res = await apiClient.put(`/schedule/sessions/${sessionId}/move`, newTime);
  return res.data;
};

export const getConflicts = async (): Promise<any> => {
  const res = await apiClient.get('/schedule/conflicts');
  return res.data;
};
""",
    "src/api/rooms.ts": """import apiClient from './client';
import { Room } from '../types';

export const getRooms = async (): Promise<Room[]> => {
  const res = await apiClient.get('/rooms');
  return res.data;
};

export const createRoom = async (data: any): Promise<Room> => {
  const res = await apiClient.post('/rooms', data);
  return res.data;
};

export const updateRoom = async (id: string, data: any): Promise<Room> => {
  const res = await apiClient.put(`/rooms/${id}`, data);
  return res.data;
};
""",
    "src/api/modules.ts": """import apiClient from './client';
import { TherapyModule } from '../types';

export const getModules = async (): Promise<TherapyModule[]> => {
  const res = await apiClient.get('/modules');
  return res.data;
};

export const createModule = async (data: any): Promise<TherapyModule> => {
  const res = await apiClient.post('/modules', data);
  return res.data;
};
""",
    "src/api/iep.ts": """import apiClient from './client';
import { IepPlan, ProgressRecord } from '../types';

export const getIepPlans = async (studentId: string): Promise<IepPlan[]> => {
  const res = await apiClient.get(`/iep/student/${studentId}`);
  return res.data;
};

export const createIepPlan = async (data: any): Promise<IepPlan> => {
  const res = await apiClient.post('/iep', data);
  return res.data;
};

export const addGoal = async (planId: string, data: any): Promise<IepPlan> => {
  const res = await apiClient.post(`/iep/${planId}/goals`, data);
  return res.data;
};

export const updateGoal = async (planId: string, goalId: string, data: any): Promise<IepPlan> => {
  const res = await apiClient.put(`/iep/${planId}/goals/${goalId}`, data);
  return res.data;
};

export const addProgressRecord = async (data: any): Promise<ProgressRecord> => {
  const res = await apiClient.post('/iep/progress', data);
  return res.data;
};

export const getStudentProgress = async (studentId: string): Promise<ProgressRecord[]> => {
  const res = await apiClient.get(`/iep/progress/student/${studentId}`);
  return res.data;
};
""",
    "src/api/reports.ts": """import apiClient from './client';

export const getStudentProgress = async (studentId: string): Promise<any> => {
  const res = await apiClient.get(`/reports/student-progress/${studentId}`);
  return res.data;
};

export const getMonthlyAttendance = async (month: string): Promise<any> => {
  const res = await apiClient.get(`/reports/attendance`, { params: { month } });
  return res.data;
};

export const getTherapistWorkload = async (): Promise<any> => {
  const res = await apiClient.get('/reports/therapist-workload');
  return res.data;
};

export const getCapacity = async (): Promise<any> => {
  const res = await apiClient.get('/reports/capacity');
  return res.data;
};
""",
    "src/api/dashboard.ts": """import apiClient from './client';
import { DashboardStats, Alert } from '../types';

export const getStats = async (): Promise<DashboardStats> => {
  const res = await apiClient.get('/dashboard/stats');
  return res.data;
};

export const getToday = async (): Promise<any> => {
  const res = await apiClient.get('/dashboard/today');
  return res.data;
};

export const getAlerts = async (): Promise<Alert[]> => {
  const res = await apiClient.get('/dashboard/alerts');
  return res.data;
};
""",
    "src/store/authStore.ts": """import { create } from 'zustand';
import { User } from '../types';
import * as authApi from '../api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: any) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  login: async (credentials) => {
    const { user, token } = await authApi.login(credentials);
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  checkAuth: async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const user = await authApi.getMe();
        set({ user, isAuthenticated: true });
      } catch (error) {
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      }
    }
  },
}));
""",
    "src/components/Layout/MainLayout.tsx": """import React, { useState } from 'react';
import { Layout, Menu, theme, Dropdown, Space, Avatar } from 'antd';
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
  LogoutOutlined
} from '@ant-design/icons';
import { useAuthStore } from '../../store/authStore';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { token: { colorBgContainer, borderRadiusLG } } = theme.useToken();
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const menuItems = [
    { key: '/', icon: <DashboardOutlined />, label: 'Ana Panel' },
    { key: '/students', icon: <TeamOutlined />, label: 'Öğrenciler' },
    { key: '/therapists', icon: <UserOutlined />, label: 'Öğretmenler' },
    { key: '/schedule', icon: <CalendarOutlined />, label: 'Ders Programı' },
    { key: '/sessions', icon: <FileTextOutlined />, label: 'Seanslar' },
    { key: '/rooms', icon: <HomeOutlined />, label: 'Odalar' },
    { key: '/iep', icon: <FormOutlined />, label: 'BEP & İlerleme' },
    { key: '/reports', icon: <BarChartOutlined />, label: 'Raporlar' },
    { key: '/settings', icon: <SettingOutlined />, label: 'Ayarlar' },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(value) => setCollapsed(value)} theme="dark" width={240}>
        <div style={{ height: 32, margin: 16, background: 'rgba(255, 255, 255, 0.2)', borderRadius: 6, display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#fff', fontWeight: 'bold' }}>
          {collapsed ? 'ÖREM' : 'ÖREM Yönetim'}
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={({ key }) => navigate(key)}
        />
      </Sider>
      <Layout>
        <Header style={{ padding: '0 24px', background: colorBgContainer, display: 'flex', justifyContent: 'flex-end', alignItems: 'center' }}>
          <Dropdown menu={{ items: [{ key: 'logout', icon: <LogoutOutlined />, label: 'Çıkış Yap', onClick: handleLogout }] }}>
            <Space style={{ cursor: 'pointer' }}>
              <Avatar icon={<UserOutlined />} />
              {user?.username || 'Kullanıcı'}
            </Space>
          </Dropdown>
        </Header>
        <Content style={{ margin: '24px 16px', padding: 24, minHeight: 280, background: colorBgContainer, borderRadius: borderRadiusLG }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
""",
    "src/components/Layout/ProtectedRoute.tsx": """import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuthStore } from '../../store/authStore';

const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;
""",
    "src/pages/LoginPage.tsx": """import React, { useState } from 'react';
import { Form, Input, Button, Card, Typography, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import './LoginPage.css';

const { Title } = Typography;

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login } = useAuthStore();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    setLoading(true);
    try {
      await login(values);
      message.success('Giriş başarılı!');
      navigate('/');
    } catch (error) {
      message.error('Giriş başarısız, lütfen bilgilerinizi kontrol edin.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <Card className="login-card">
        <div style={{ textAlign: 'center', marginBottom: 24 }}>
          <Title level={2} style={{ color: '#1890ff', margin: 0 }}>ÖREM</Title>
          <Title level={4} style={{ marginTop: 8 }}>Yönetim Sistemi</Title>
        </div>
        <Form name="login" onFinish={onFinish} size="large">
          <Form.Item name="username" rules={[{ required: true, message: 'Lütfen kullanıcı adınızı girin!' }]}>
            <Input prefix={<UserOutlined />} placeholder="Kullanıcı Adı" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Lütfen şifrenizi girin!' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Şifre" />
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block loading={loading}>
              Giriş Yap
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
""",
    "src/pages/LoginPage.css": """.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #1890ff 0%, #08979c 100%);
}

.login-card {
  width: 400px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
""",
    "src/pages/DashboardPage.tsx": """import React from 'react';
import { Row, Col, Card, Statistic, Table, Tag, List } from 'antd';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Dil ve Konuşma', value: 4 },
  { name: 'Fizyoterapi', value: 3 },
  { name: 'Özel Eğitim', value: 5 },
  { name: 'Otizm', value: 2 },
];
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

const DashboardPage: React.FC = () => {
  const sessionColumns = [
    { title: 'Saat', dataIndex: 'time', key: 'time' },
    { title: 'Öğrenci', dataIndex: 'student', key: 'student' },
    { title: 'Öğretmen', dataIndex: 'therapist', key: 'therapist' },
    { title: 'Oda', dataIndex: 'room', key: 'room' },
    { title: 'Durum', dataIndex: 'status', key: 'status', render: (status: string) => <Tag color="blue">{status}</Tag> },
  ];

  const sessionsData = [
    { key: '1', time: '09:00 - 09:45', student: 'Ahmet Yılmaz', therapist: 'Ayşe Kaya', room: 'Oda 1', status: 'Planlandı' },
    { key: '2', time: '10:00 - 10:45', student: 'Elif Demir', therapist: 'Mehmet Öz', room: 'Oda 2', status: 'Planlandı' },
  ];

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>Ana Panel</h2>
      <Row gutter={[16, 16]}>
        <Col span={6}><Card hoverable><Statistic title="Toplam Öğrenci" value={120} /></Card></Col>
        <Col span={6}><Card hoverable><Statistic title="Toplam Öğretmen" value={15} /></Card></Col>
        <Col span={6}><Card hoverable><Statistic title="Bugünkü Seanslar" value={45} /></Card></Col>
        <Col span={6}><Card hoverable><Statistic title="Katılım Oranı" value={92} suffix="%" /></Card></Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col span={8}><Card hoverable><Statistic title="Süresi Dolan Raporlar" value={3} valueStyle={{ color: '#cf1322' }} /></Card></Col>
        <Col span={8}><Card hoverable><Statistic title="Haftalık Doluluk" value={78} suffix="%" /></Card></Col>
        <Col span={8}><Card hoverable><Statistic title="Telafi Bekleyen" value={5} /></Card></Col>
      </Row>
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col span={16}>
          <Card title="Bugünün Programı" hoverable>
            <Table dataSource={sessionsData} columns={sessionColumns} pagination={false} size="small" />
          </Card>
        </Col>
        <Col span={8}>
          <Card title="Branş Dağılımı" hoverable style={{ marginBottom: 16 }}>
            <div style={{ height: 200 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={data} cx="50%" cy="50%" outerRadius={80} fill="#8884d8" dataKey="value" label>
                    {data.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
          <Card title="Uyarılar" hoverable>
            <List
              size="small"
              dataSource={['Ahmet Yılmaz\'ın RAM raporu 15 gün içinde doluyor.', 'Oda 3 bakıma alındı.']}
              renderItem={item => <List.Item><Tag color="warning">Uyarı</Tag> {item}</List.Item>}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
""",
    "src/pages/StudentsPage.tsx": """import React, { useState } from 'react';
import { Table, Button, Input, Space, Tag, Modal, Steps, Form, Select, DatePicker, message, Popconfirm } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined, EditOutlined, DeleteOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const { Step } = Steps;

const StudentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const columns = [
    { title: 'Ad Soyad', dataIndex: 'name', key: 'name' },
    { title: 'TC Kimlik', dataIndex: 'tc', key: 'tc' },
    { title: 'Doğum Tarihi', dataIndex: 'birthDate', key: 'birthDate' },
    { title: 'Engel Türü', dataIndex: 'disability', key: 'disability' },
    { title: 'Durum', dataIndex: 'status', key: 'status', render: (status: string) => <Tag color={status === 'Aktif' ? 'green' : 'red'}>{status}</Tag> },
    {
      title: 'İşlemler', key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/students/${record.key}`)} />
          <Button icon={<EditOutlined />} />
          <Popconfirm title="Silmek istediğinize emin misiniz?"><Button danger icon={<DeleteOutlined />} /></Popconfirm>
        </Space>
      )
    }
  ];

  const data = [
    { key: '1', name: 'Ahmet Yılmaz', tc: '12345678901', birthDate: '01.01.2015', disability: 'Otizm', status: 'Aktif' }
  ];

  const handleFinish = () => {
    message.success('Öğrenci kaydedildi ve ders programı otomatik oluşturuldu!');
    setIsModalVisible(false);
    setCurrentStep(0);
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Öğrenciler</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>Yeni Öğrenci Ekle</Button>
      </div>
      <div style={{ marginBottom: 16 }}>
        <Input placeholder="Öğrenci Ara..." prefix={<SearchOutlined />} style={{ width: 300, marginRight: 16 }} />
        <Select placeholder="Engel Türü" style={{ width: 200 }} options={[{ value: 'otizm', label: 'Otizm' }]} />
      </div>
      <Table columns={columns} dataSource={data} />

      <Modal title="Yeni Öğrenci Ekle" open={isModalVisible} onCancel={() => setIsModalVisible(false)} footer={null} width={800}>
        <Steps current={currentStep} style={{ marginBottom: 24 }}>
          <Step title="Kişisel Bilgiler" />
          <Step title="Veli Bilgileri" />
          <Step title="RAM Raporu" />
          <Step title="Modül Ataması" />
        </Steps>
        <Form layout="vertical">
          {currentStep === 0 && (
            <>
              <Form.Item label="Ad Soyad"><Input /></Form.Item>
              <Form.Item label="TC Kimlik"><Input /></Form.Item>
              <Form.Item label="Doğum Tarihi"><DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" /></Form.Item>
            </>
          )}
          {currentStep === 1 && (
            <>
              <Form.Item label="Veli Adı"><Input /></Form.Item>
              <Form.Item label="Telefon"><Input /></Form.Item>
            </>
          )}
          {currentStep === 2 && (
            <>
              <Form.Item label="Rapor Numarası"><Input /></Form.Item>
            </>
          )}
          {currentStep === 3 && (
            <>
              <Form.Item label="Modüller"><Select mode="multiple" options={[{ value: 'dil', label: 'Dil ve Konuşma' }]} /></Form.Item>
            </>
          )}
          <div style={{ marginTop: 24, textAlign: 'right' }}>
            {currentStep > 0 && <Button style={{ marginRight: 8 }} onClick={() => setCurrentStep(currentStep - 1)}>Geri</Button>}
            {currentStep < 3 && <Button type="primary" onClick={() => setCurrentStep(currentStep + 1)}>İleri</Button>}
            {currentStep === 3 && <Button type="primary" onClick={handleFinish}>Kaydet</Button>}
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default StudentsPage;
""",
    "src/pages/StudentDetailPage.tsx": """import React from 'react';
import { Tabs, Descriptions, Card, Table, Tag } from 'antd';
import { useParams } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';

const { TabPane } = Tabs;

const chartData = [
  { name: '1. Hafta', score: 20 },
  { name: '2. Hafta', score: 40 },
  { name: '3. Hafta', score: 35 },
  { name: '4. Hafta', score: 60 },
];

const StudentDetailPage: React.FC = () => {
  const { id } = useParams();

  return (
    <div>
      <h2>Öğrenci Detayı</h2>
      <Card>
        <Tabs defaultActiveKey="1">
          <TabPane tab="Genel Bilgiler" key="1">
            <Descriptions title="Kişisel Bilgiler" bordered>
              <Descriptions.Item label="Ad Soyad">Ahmet Yılmaz</Descriptions.Item>
              <Descriptions.Item label="TC Kimlik">12345678901</Descriptions.Item>
              <Descriptions.Item label="Doğum Tarihi">01.01.2015</Descriptions.Item>
              <Descriptions.Item label="Engel Türü">Otizm</Descriptions.Item>
            </Descriptions>
            <Descriptions title="Veli Bilgileri" bordered style={{ marginTop: 24 }}>
              <Descriptions.Item label="Veli Adı">Ayşe Yılmaz</Descriptions.Item>
              <Descriptions.Item label="Telefon">0555 555 5555</Descriptions.Item>
              <Descriptions.Item label="Yakınlık">Anne</Descriptions.Item>
            </Descriptions>
          </TabPane>
          <TabPane tab="RAM Raporu" key="2">
            <Descriptions bordered>
              <Descriptions.Item label="Rapor No">RM-2023-123</Descriptions.Item>
              <Descriptions.Item label="Bitiş Tarihi">15.10.2024</Descriptions.Item>
            </Descriptions>
          </TabPane>
          <TabPane tab="Ders Programı" key="3">
            <Table columns={[{ title: 'Gün', dataIndex: 'day' }, { title: 'Saat', dataIndex: 'time' }, { title: 'Modül', dataIndex: 'module' }]} dataSource={[]} />
          </TabPane>
          <TabPane tab="BEP & İlerleme" key="4">
            <div style={{ height: 300, marginTop: 16 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Line type="monotone" dataKey="score" stroke="#1890ff" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </TabPane>
          <TabPane tab="Seans Geçmişi" key="5">
            <Table columns={[{ title: 'Tarih', dataIndex: 'date' }, { title: 'Durum', dataIndex: 'status', render: () => <Tag color="green">Katıldı</Tag> }]} dataSource={[]} />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default StudentDetailPage;
""",
    "src/pages/TherapistsPage.tsx": """import React from 'react';
import { Table, Button, Input, Tag, Space, Progress } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';

const TherapistsPage: React.FC = () => {
  const navigate = useNavigate();

  const columns = [
    { title: 'Ad Soyad', dataIndex: 'name', key: 'name' },
    { title: 'Unvan', dataIndex: 'title', key: 'title' },
    { title: 'Branşlar', dataIndex: 'specializations', key: 'specs', render: (specs: string[]) => specs.map(s => <Tag key={s} color="blue">{s}</Tag>) },
    { title: 'Haftalık Saat', dataIndex: 'hours', key: 'hours' },
    { title: 'Doluluk', dataIndex: 'workload', key: 'workload', render: (val: number) => <Progress percent={val} size="small" /> },
    {
      title: 'İşlemler', key: 'action',
      render: (_: any, record: any) => (
        <Space size="middle">
          <Button icon={<EyeOutlined />} onClick={() => navigate(`/therapists/${record.key}`)} />
        </Space>
      )
    }
  ];

  const data = [
    { key: '1', name: 'Ayşe Kaya', title: 'Dil ve Konuşma Terapisti', specializations: ['Dil ve Konuşma'], hours: 40, workload: 85 }
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Öğretmenler</h2>
        <Button type="primary" icon={<PlusOutlined />}>Yeni Öğretmen Ekle</Button>
      </div>
      <div style={{ marginBottom: 16 }}>
        <Input placeholder="Ara..." prefix={<SearchOutlined />} style={{ width: 300 }} />
      </div>
      <Table columns={columns} dataSource={data} />
    </div>
  );
};

export default TherapistsPage;
""",
    "src/pages/TherapistDetailPage.tsx": """import React from 'react';
import { Tabs, Descriptions, Card, Progress } from 'antd';

const { TabPane } = Tabs;

const TherapistDetailPage: React.FC = () => {
  return (
    <div>
      <h2>Öğretmen Detayı</h2>
      <Card>
        <Tabs defaultActiveKey="1">
          <TabPane tab="Genel Bilgiler" key="1">
            <Descriptions bordered>
              <Descriptions.Item label="Ad Soyad">Ayşe Kaya</Descriptions.Item>
              <Descriptions.Item label="Unvan">Dil ve Konuşma Terapisti</Descriptions.Item>
            </Descriptions>
          </TabPane>
          <TabPane tab="Müsaitlik" key="2">Müsaitlik Tablosu (Pzt-Cum)</TabPane>
          <TabPane tab="Ders Programı" key="3">Haftalık Program</TabPane>
          <TabPane tab="İş Yükü" key="4">
            <Progress type="dashboard" percent={85} />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default TherapistDetailPage;
""",
    "src/pages/SchedulePage.tsx": """import React from 'react';
import { Button, Select, Space, Card } from 'antd';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import trLocale from '@fullcalendar/core/locales/tr';

const SchedulePage: React.FC = () => {
  const events = [
    { title: 'Ahmet Y. - Dil (Oda 1)', start: '2023-10-18T10:00:00', end: '2023-10-18T10:45:00', backgroundColor: '#1890ff' }
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Ders Programı</h2>
        <Space>
          <Select placeholder="Öğretmen Seç" style={{ width: 150 }} />
          <Select placeholder="Oda Seç" style={{ width: 150 }} />
          <Button type="primary">Otomatik Program Oluştur</Button>
        </Space>
      </div>
      <Card>
        <div style={{ height: '70vh' }}>
          <FullCalendar
            plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
            initialView="timeGridWeek"
            locales={[trLocale]}
            locale="tr"
            slotMinTime="08:00:00"
            slotMaxTime="18:00:00"
            slotDuration="00:15:00"
            businessHours={{ daysOfWeek: [1, 2, 3, 4, 5], startTime: '09:00', endTime: '17:00' }}
            events={events}
            headerToolbar={{ left: 'prev,next today', center: 'title', right: 'timeGridWeek,timeGridDay' }}
            allDaySlot={false}
            height="100%"
          />
        </div>
      </Card>
    </div>
  );
};

export default SchedulePage;
""",
    "src/pages/SessionsPage.tsx": """import React from 'react';
import { Table, DatePicker, Select, Space, Tag, Button } from 'antd';
import { CheckOutlined } from '@ant-design/icons';

const SessionsPage: React.FC = () => {
  const columns = [
    { title: 'Tarih', dataIndex: 'date' },
    { title: 'Saat', dataIndex: 'time' },
    { title: 'Öğrenci', dataIndex: 'student' },
    { title: 'Öğretmen', dataIndex: 'therapist' },
    { title: 'Durum', dataIndex: 'status', render: (status: string) => <Tag color={status === 'Planlandı' ? 'blue' : 'green'}>{status}</Tag> },
    { title: 'İşlem', render: () => <Button size="small" icon={<CheckOutlined />}>Yoklama</Button> }
  ];

  const data = [
    { key: '1', date: '18.10.2023', time: '10:00', student: 'Ahmet Y.', therapist: 'Ayşe K.', status: 'Planlandı' }
  ];

  return (
    <div>
      <h2>Seanslar</h2>
      <Space style={{ marginBottom: 16 }}>
        <DatePicker format="DD.MM.YYYY" />
        <Select placeholder="Durum" style={{ width: 120 }} />
      </Space>
      <Table columns={columns} dataSource={data} />
    </div>
  );
};

export default SessionsPage;
""",
    "src/pages/RoomsPage.tsx": """import React from 'react';
import { Table, Button, Progress } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const RoomsPage: React.FC = () => {
  const columns = [
    { title: 'Oda Adı', dataIndex: 'name' },
    { title: 'Kodu', dataIndex: 'code' },
    { title: 'Kapasite', dataIndex: 'capacity' },
    { title: 'Doluluk Oranı', dataIndex: 'occupancy', render: (val: number) => <Progress percent={val} size="small" /> },
  ];

  const data = [{ key: '1', name: 'Bireysel Eğitim 1', code: 'BE-01', capacity: 2, occupancy: 60 }];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Odalar</h2>
        <Button type="primary" icon={<PlusOutlined />}>Yeni Oda</Button>
      </div>
      <Table columns={columns} dataSource={data} />
    </div>
  );
};

export default RoomsPage;
""",
    "src/pages/IepPage.tsx": """import React from 'react';
import { Select, Card, List, Tag, Button } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const IepPage: React.FC = () => {
  return (
    <div>
      <h2>BEP & İlerleme</h2>
      <Select placeholder="Öğrenci Seç" style={{ width: 300, marginBottom: 16 }} />
      <Card title="Aktif BEP Planı" extra={<Button icon={<PlusOutlined />}>Hedef Ekle</Button>}>
        <List
          dataSource={['İki kelimelik cümle kurar.', 'Renkleri eşleştirir.']}
          renderItem={item => (
            <List.Item>
              <List.Item.Meta title={item} />
              <Tag color="processing">Devam Ediyor</Tag>
            </List.Item>
          )}
        />
      </Card>
    </div>
  );
};

export default IepPage;
""",
    "src/pages/ReportsPage.tsx": """import React from 'react';
import { Tabs, Card } from 'antd';

const { TabPane } = Tabs;

const ReportsPage: React.FC = () => {
  return (
    <div>
      <h2>Raporlar</h2>
      <Card>
        <Tabs defaultActiveKey="1">
          <TabPane tab="Öğrenci İlerleme Raporu" key="1">Öğrenci seçimi ve ilerleme grafikleri</TabPane>
          <TabPane tab="Aylık Devamsızlık" key="2">Aylık devamsızlık tablosu</TabPane>
          <TabPane tab="Öğretmen İş Yükü" key="3">İş yükü çubuk grafiği (BarChart)</TabPane>
          <TabPane tab="Oda Doluluk" key="4">Oda doluluk istatistikleri</TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default ReportsPage;
""",
    "src/pages/SettingsPage.tsx": """import React from 'react';
import { Tabs, Card } from 'antd';

const { TabPane } = Tabs;

const SettingsPage: React.FC = () => {
  return (
    <div>
      <h2>Ayarlar</h2>
      <Card>
        <Tabs defaultActiveKey="1" tabPosition="left">
          <TabPane tab="Terapi Modülleri" key="1">Modül CRUD</TabPane>
          <TabPane tab="Kullanıcı Yönetimi" key="2">Kullanıcı Ekle/Düzenle</TabPane>
          <TabPane tab="Sistem Bilgileri" key="3">Versiyon: 1.0.0</TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

export default SettingsPage;
""",
    "src/App.css": """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, 'Noto Sans', sans-serif;
  background-color: #f0f2f5;
}

::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

.ant-card {
  transition: all 0.3s;
}

.ant-card-hoverable:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
"""
}

for rel_path, content in FILES.items():
    full_path = os.path.join(BASE_DIR, os.path.normpath(rel_path))
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Created {rel_path}")
