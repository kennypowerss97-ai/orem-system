import React, { useEffect, useState } from 'react';
import { Tabs, Card, Table, Tag, Form, Input, Button, message, Descriptions, Space, Modal, InputNumber, Switch, Popconfirm, Tooltip, Row, Col } from 'antd';
import { PlusOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, MedicineBoxOutlined, SettingOutlined, UserOutlined, InfoCircleOutlined, BookOutlined } from '@ant-design/icons';
import { getModules, createModule, updateModule, deleteModule } from '../api/modules';
import { getDisabilities, createDisability, updateDisability, deleteDisability, DisabilityItem } from '../api/disabilities';
import { useAuthStore } from '../store/authStore';

const SettingsPage: React.FC = () => {
  const [modules, setModules] = useState<any[]>([]);
  const [modulesLoading, setModulesLoading] = useState(false);
  const [disabilities, setDisabilities] = useState<DisabilityItem[]>([]);
  const [disabilitiesLoading, setDisabilitiesLoading] = useState(false);
  
  // Modül Modal
  const [isModuleModalOpen, setIsModuleModalOpen] = useState(false);
  const [editingModule, setEditingModule] = useState<any | null>(null);
  const [moduleForm] = Form.useForm();
  const [savingModule, setSavingModule] = useState(false);

  // Tanı Modal
  const [isDisabilityModalOpen, setIsDisabilityModalOpen] = useState(false);
  const [editingDisability, setEditingDisability] = useState<DisabilityItem | null>(null);
  const [disabilityForm] = Form.useForm();
  const [savingDisability, setSavingDisability] = useState(false);

  const user = useAuthStore((state: any) => state.user);

  useEffect(() => {
    fetchModules();
    fetchDisabilities();
  }, []);

  const fetchModules = async () => {
    setModulesLoading(true);
    try {
      const data = await getModules();
      setModules(data || []);
    } catch (error) {
      message.error('Branşlar ve modüller yüklenirken hata oluştu');
    } finally {
      setModulesLoading(false);
    }
  };

  const fetchDisabilities = async () => {
    setDisabilitiesLoading(true);
    try {
      const data = await getDisabilities();
      setDisabilities(data || []);
    } catch (error) {
      message.error('Engel tanıları yüklenirken hata oluştu');
    } finally {
      setDisabilitiesLoading(false);
    }
  };

  // --- Modül / Branş İşlemleri ---
  const handleOpenCreateModule = () => {
    setEditingModule(null);
    moduleForm.resetFields();
    moduleForm.setFieldsValue({
      duration: 45,
      isGroupEligible: true
    });
    setIsModuleModalOpen(true);
  };

  const handleOpenEditModule = (record: any) => {
    setEditingModule(record);
    moduleForm.resetFields();
    moduleForm.setFieldsValue({
      name: record.name,
      code: record.code,
      duration: record.duration || 45,
      isGroupEligible: record.isGroupEligible ?? true
    });
    setIsModuleModalOpen(true);
  };

  const handleSaveModule = async () => {
    try {
      const values = await moduleForm.validateFields();
      setSavingModule(true);
      if (editingModule) {
        await updateModule(editingModule.id, values);
        message.success('Branş bilgileri güncellendi! 🎉');
      } else {
        await createModule(values);
        message.success('Yeni branş başarıyla eklendi! 🎉');
      }
      setIsModuleModalOpen(false);
      moduleForm.resetFields();
      fetchModules();
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Branş kaydedilirken hata oluştu.');
    } finally {
      setSavingModule(false);
    }
  };

  const handleDeleteModule = async (id: string | number) => {
    try {
      await deleteModule(id);
      message.success('Branş silindi.');
      fetchModules();
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Silme işleminde hata oluştu.');
    }
  };

  // --- Engel Tanısı İşlemleri ---
  const handleOpenCreateDisability = () => {
    setEditingDisability(null);
    disabilityForm.resetFields();
    setIsDisabilityModalOpen(true);
  };

  const handleOpenEditDisability = (record: DisabilityItem) => {
    setEditingDisability(record);
    disabilityForm.resetFields();
    disabilityForm.setFieldsValue({
      name: record.name,
      description: record.description
    });
    setIsDisabilityModalOpen(true);
  };

  const handleSaveDisability = async () => {
    try {
      const values = await disabilityForm.validateFields();
      setSavingDisability(true);
      if (editingDisability) {
        await updateDisability(editingDisability.id, values);
        message.success('Engel tanısı güncellendi! 🎉');
      } else {
        await createDisability(values);
        message.success('Yeni engel tanısı başarıyla eklendi! 🎉');
      }
      setIsDisabilityModalOpen(false);
      disabilityForm.resetFields();
      fetchDisabilities();
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Tanı kaydedilirken hata oluştu.');
    } finally {
      setSavingDisability(false);
    }
  };

  const handleDeleteDisability = async (id: number) => {
    try {
      await deleteDisability(id);
      message.success('Tanı türü kaldırıldı.');
      fetchDisabilities();
    } catch (e: any) {
      message.error(e.response?.data?.detail || 'Silme işlemi başarısız.');
    }
  };

  const handlePasswordChange = () => {
    message.success('Şifreniz başarıyla güncellendi (Demo)');
  };

  const moduleColumns = [
    {
      title: 'Branş Kodu',
      dataIndex: 'code',
      key: 'code',
      render: (code: string) => <Tag color="geekblue">{code}</Tag>
    },
    {
      title: 'Branş / Modül Adı',
      dataIndex: 'name',
      key: 'name',
      render: (text: string, record: any) => (
        <strong style={{ color: record.color || '#1890ff' }}>{text}</strong>
      ),
    },
    {
      title: 'Varsayılan Süre',
      dataIndex: 'duration',
      key: 'duration',
      render: (dur: number) => `${dur || 45} dakika`
    },
    {
      title: 'Grup Dersi',
      dataIndex: 'isGroupEligible',
      key: 'isGroupEligible',
      render: (eligible: boolean) => (
        <Tag color={eligible ? 'green' : 'orange'}>
          {eligible ? 'Uygun' : 'Sadece Bireysel'}
        </Tag>
      ),
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (_: any, record: any) => (
        <Space size="small">
          <Tooltip title="Düzenle">
            <Button icon={<EditOutlined />} onClick={() => handleOpenEditModule(record)} />
          </Tooltip>
          <Popconfirm
            title="Bu branşı silmek istediğinize emin misiniz?"
            onConfirm={() => handleDeleteModule(record.id)}
            okText="Evet"
            cancelText="İptal"
          >
            <Tooltip title="Sil">
              <Button danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const disabilityColumns = [
    {
      title: 'Tanı / Engel Adı',
      dataIndex: 'name',
      key: 'name',
      render: (text: string) => <Tag color="blue" style={{ fontSize: '13px', padding: '4px 10px' }}>{text}</Tag>
    },
    {
      title: 'Açıklama / Kategori',
      dataIndex: 'description',
      key: 'description',
      render: (text: string) => text || '-'
    },
    {
      title: 'Durum',
      dataIndex: 'isActive',
      key: 'isActive',
      render: (active: boolean) => (
        <Tag color={active ? 'green' : 'default'}>
          {active ? 'Aktif' : 'Pasif'}
        </Tag>
      )
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (_: any, record: DisabilityItem) => (
        <Space size="small">
          <Tooltip title="Düzenle">
            <Button icon={<EditOutlined />} onClick={() => handleOpenEditDisability(record)} />
          </Tooltip>
          <Popconfirm
            title="Bu tanı türünü silmek istediğinize emin misiniz?"
            onConfirm={() => handleDeleteDisability(record.id)}
            okText="Evet"
            cancelText="İptal"
          >
            <Tooltip title="Sil">
              <Button danger icon={<DeleteOutlined />} />
            </Tooltip>
          </Popconfirm>
        </Space>
      )
    }
  ];

  const tabItems = [
    {
      key: '1',
      label: (
        <span>
          <BookOutlined /> Branşlar & Eğitim Modülleri
        </span>
      ),
      children: (
        <Card
          title="Branşlar ve Terapi Modülleri Yönetimi"
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={fetchModules}>Yenile</Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreateModule}>
                Yeni Branş Ekle
              </Button>
            </Space>
          }
        >
          <div style={{ marginBottom: 16, color: '#666' }}>
            Kurumunuzda uygulanan eğitim alanlarını ve terapileri buradan yönetebilirsiniz. Eklediğiniz veya düzenlediğiniz branşlar anında öğretmen atamalarında ve ders programlarında kullanılabilir.
          </div>
          <Table
            columns={moduleColumns}
            dataSource={modules}
            rowKey="id"
            loading={modulesLoading}
            pagination={false}
          />
        </Card>
      ),
    },
    {
      key: '2',
      label: (
        <span>
          <MedicineBoxOutlined /> Engel & Tanı Türleri
        </span>
      ),
      children: (
        <Card
          title="Engel Tanıları ve Rapor Türleri Yönetimi"
          extra={
            <Space>
              <Button icon={<ReloadOutlined />} onClick={fetchDisabilities}>Yenile</Button>
              <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreateDisability}>
                Yeni Tanı Türü Ekle
              </Button>
            </Space>
          }
        >
          <div style={{ marginBottom: 16, color: '#666' }}>
            Öğrenci kaydı ve RAM raporlarında listelenen tanı türlerini özelleştirebilir, isimlerini değiştirebilir veya yenilerini ekleyebilirsiniz.
          </div>
          <Table
            columns={disabilityColumns}
            dataSource={disabilities}
            rowKey="id"
            loading={disabilitiesLoading}
            pagination={{ pageSize: 15 }}
          />
        </Card>
      ),
    },
    {
      key: '3',
      label: (
        <span>
          <UserOutlined /> Kullanıcı Hesabı
        </span>
      ),
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
      key: '4',
      label: (
        <span>
          <InfoCircleOutlined /> Sistem Bilgisi
        </span>
      ),
      children: (
        <Card title="Yazılım ve Sistem Detayları">
          <Descriptions bordered column={1}>
            <Descriptions.Item label="Sistem Adı">ÖREM - Akıllı Özel Eğitim ve Rehabilitasyon Yönetimi</Descriptions.Item>
            <Descriptions.Item label="Sistem Versiyonu">2.1.0</Descriptions.Item>
            <Descriptions.Item label="Veritabanı">SQLite (Yerel & Bulut Uyumlu)</Descriptions.Item>
            <Descriptions.Item label="API Altyapısı">FastAPI (Python 3)</Descriptions.Item>
            <Descriptions.Item label="Arayüz (Frontend)">React 18 + TypeScript + Ant Design 5</Descriptions.Item>
          </Descriptions>
        </Card>
      ),
    },
  ];

  return (
    <div style={{ padding: '4px' }}>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0, fontSize: '1.4rem' }}>Sistem Ayarları</h2>
        <span style={{ color: '#888' }}>Branşlar, Engel Tanıları, Kullanıcı Hesapları ve Sistem Parametreleri</span>
      </div>

      <Tabs defaultActiveKey="1" items={tabItems} />

      {/* Branş / Modül Ekle & Düzenle Modalı */}
      <Modal
        title={editingModule ? "Branşı Düzenle" : "Yeni Branş / Terapi Modülü Ekle"}
        open={isModuleModalOpen}
        onCancel={() => { setIsModuleModalOpen(false); moduleForm.resetFields(); }}
        footer={null}
        destroyOnClose={true}
      >
        <Form form={moduleForm} layout="vertical" onFinish={handleSaveModule}>
          <Form.Item
            name="name"
            label="Branş / Modül Adı"
            rules={[{ required: true, message: 'Lütfen branş adını giriniz' }]}
          >
            <Input placeholder="Örn: Ergoterapi / Duyu Bütünleme" />
          </Form.Item>

          <Row gutter={12}>
            <Col span={12}>
              <Form.Item name="code" label="Kısa Kod (Opsiyonel)">
                <Input placeholder="Örn: ERGOTERAPI" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="duration" label="Varsayılan Süre (Dakika)">
                <InputNumber min={15} max={120} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item name="isGroupEligible" label="Grup Eğitimine Uygun mu?" valuePropName="checked">
            <Switch checkedChildren="Evet" unCheckedChildren="Hayır" />
          </Form.Item>

          <div style={{ textAlign: 'right', marginTop: 16 }}>
            <Space>
              <Button onClick={() => setIsModuleModalOpen(false)}>Vazgeç</Button>
              <Button type="primary" htmlType="submit" loading={savingModule}>
                {editingModule ? 'Güncelle' : 'Kaydet'}
              </Button>
            </Space>
          </div>
        </Form>
      </Modal>

      {/* Engel Tanısı Ekle & Düzenle Modalı */}
      <Modal
        title={editingDisability ? "Engel Tanısını Düzenle" : "Yeni Engel / Tanı Türü Ekle"}
        open={isDisabilityModalOpen}
        onCancel={() => { setIsDisabilityModalOpen(false); disabilityForm.resetFields(); }}
        footer={null}
        destroyOnClose={true}
      >
        <Form form={disabilityForm} layout="vertical" onFinish={handleSaveDisability}>
          <Form.Item
            name="name"
            label="Tanı / Engel Adı"
            rules={[{ required: true, message: 'Lütfen tanı adını giriniz' }]}
          >
            <Input placeholder="Örn: Gelişimsel Dil Gecikmesi" />
          </Form.Item>

          <Form.Item name="description" label="Açıklama / Detay">
            <Input.TextArea rows={3} placeholder="Tanı ile ilgili ek açıklamalar..." />
          </Form.Item>

          <div style={{ textAlign: 'right', marginTop: 16 }}>
            <Space>
              <Button onClick={() => setIsDisabilityModalOpen(false)}>Vazgeç</Button>
              <Button type="primary" htmlType="submit" loading={savingDisability}>
                {editingDisability ? 'Güncelle' : 'Kaydet'}
              </Button>
            </Space>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default SettingsPage;
