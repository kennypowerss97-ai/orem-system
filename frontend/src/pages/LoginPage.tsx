import React, { useState } from 'react';
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

  const [form] = Form.useForm();

  React.useEffect(() => {
    // URL parametrelerinde auto=1 veya hızlı giriş istenmişse otomatik giriş yap
    const params = new URLSearchParams(window.location.search);
    if (params.get('auto') === '1' || params.get('quick') === '1') {
      quickLogin();
    }
  }, []);

  const quickLogin = async () => {
    setLoading(true);
    try {
      await login({ username: 'admin', password: 'admin123' });
      message.success('Yönetici girişi başarılı!');
      navigate('/');
    } catch (error) {
      message.error('Giriş başarısız, lütfen sunucunun açık olduğundan emin olun.');
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
        <Form form={form} name="login" onFinish={onFinish} size="large" initialValues={{ username: 'admin', password: 'admin123' }}>
          <Form.Item name="username" rules={[{ required: true, message: 'Lütfen kullanıcı adınızı girin!' }]}>
            <Input prefix={<UserOutlined />} placeholder="Kullanıcı Adı" />
          </Form.Item>
          <Form.Item name="password" rules={[{ required: true, message: 'Lütfen şifrenizi girin!' }]}>
            <Input.Password prefix={<LockOutlined />} placeholder="Şifre" />
          </Form.Item>
          <Form.Item style={{ marginBottom: 12 }}>
            <Button type="primary" htmlType="submit" block loading={loading}>
              Giriş Yap
            </Button>
          </Form.Item>
          <Form.Item style={{ marginBottom: 0 }}>
            <Button type="dashed" block onClick={quickLogin} loading={loading}>
              ⚡ Tek Tıkla Yönetici Girişi (admin)
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
