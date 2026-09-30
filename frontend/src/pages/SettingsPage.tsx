import React, { useEffect, useState } from 'react';
import { Tabs, Card, Table, Tag, Form, Input, Button, message, Descriptions } from 'antd';
import { getModules } from '../api/modules';
import { useAuthStore } from '../store/authStore';

const SettingsPage: React.FC = () => {
  const [modules, setModules] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const user = useAuthStore((state: any) => state.user);

  useEffect(() => {
    fetchModules();
  }, []);

  const fetchModules = async () => {
    setLoading(true);
    try {
      const data = await getModules();
      setModules(data);
    } catch (error) {
      message.error('Modüller yüklenirken hata oluştu');
    } finally {
      setLoading(false);
    }
  };

  const handlePasswordChange = (values: any) => {
    console.log('Password change values:', values);
    message.success('Şifreniz başarıyla güncellendi (Demo)');
  };

  const moduleColumns = [
    {
      title: 'Kod',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: 'Modül Adı',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <Tag color={record.color || 'blue'}>{text}</Tag>
      ),
    },
    {
      title: 'Süre (dk)',
      dataIndex: 'duration',
      key: 'duration',
    },
    {
      title: 'Grup Uygunluğu',
      dataIndex: 'isGroupEligible',
      key: 'isGroupEligible',
      render: (eligible: boolean) => (
        <Tag color={eligible ? 'green' : 'red'}>
          {eligible ? 'Evet' : 'Hayır'}
        </Tag>
      ),
    },
  ];

  const tabItems = [
    {
      key: '1',
      label: 'Terapi Modülleri',
      children: (
        <Card title="MEB Onaylı Terapi Modülleri">
          <Table
            columns={moduleColumns}
            dataSource={modules}
            rowKey="id"
            loading={loading}
            pagination={false}
          />
        </Card>
      ),
    },
    {
      key: '2',
      label: 'Kullanıcı Yönetimi',
      children: (
        <Card title="Kullanıcı Bilgileri">
          <div style={{ marginBottom: 24 }}>
            <p><strong>Kullanıcı Adı:</strong> {user?.username}</p>
            <p>
              <strong>Rol:</strong> <Tag color="blue">{user?.role === 'admin' ? 'Yönetici' : 'Kullanıcı'}</Tag>
            </p>
          </div>
          
          <Card title="Şifre Değiştir" type="inner">
            <Form layout="vertical" onFinish={handlePasswordChange} style={{ maxWidth: 400 }}>
              <Form.Item 
                label="Mevcut Şifre" 
                name="currentPassword"
                rules={[{ required: true, message: 'Lütfen mevcut şifrenizi girin!' }]}
              >
                <Input.Password />
              </Form.Item>
              <Form.Item 
                label="Yeni Şifre" 
                name="newPassword"
                rules={[{ required: true, message: 'Lütfen yeni şifrenizi girin!' }]}
              >
                <Input.Password />
              </Form.Item>
              <Form.Item 
                label="Yeni Şifre (Tekrar)" 
                name="confirmPassword"
                dependencies={['newPassword']}
                rules={[
                  { required: true, message: 'Lütfen yeni şifrenizi tekrar girin!' },
                  ({ getFieldValue }) => ({
                    validator(_, value) {
                      if (!value || getFieldValue('newPassword') === value) {
                        return Promise.resolve();
                      }
                      return Promise.reject(new Error('Şifreler eşleşmiyor!'));
                    },
                  }),
                ]}
              >
                <Input.Password />
              </Form.Item>
              <Form.Item>
                <Button type="primary" htmlType="submit">
                  Şifreyi Güncelle
                </Button>
              </Form.Item>
            </Form>
          </Card>
        </Card>
      ),
    },
    {
      key: '3',
      label: 'Sistem Bilgileri',
      children: (
        <Card title="Yazılım ve Sistem Detayları">
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Sistem Versiyonu">1.0.0</Descriptions.Item>
            <Descriptions.Item label="Veritabanı">SQLite</Descriptions.Item>
            <Descriptions.Item label="API Altyapısı">FastAPI (Python)</Descriptions.Item>
            <Descriptions.Item label="Arayüz (Frontend)">React 18 + TypeScript</Descriptions.Item>
          </Descriptions>
        </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: '24px' }}>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '24px' }}>Sistem Ayarları</h1>
      <Tabs defaultActiveKey="1" items={tabItems} />
    </div>
  );
};

export default SettingsPage;
