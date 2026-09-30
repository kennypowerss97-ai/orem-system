import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Space, Tag, Progress, Modal, Form, InputNumber, Select, Checkbox, message, Tooltip, Row, Col, Popconfirm } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined, EditOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getTherapists, createTherapist, updateTherapist, deleteTherapist } from '../api/therapists';
import { getModules, DEFAULT_MODULES } from '../api/modules';
import { getBranches } from '../api/branches';
import { Therapist, TeacherBranch } from '../types';

const { Option } = Select;

interface Module {
  id: string;
  name: string;
  color?: string;
}

const TherapistsPage: React.FC = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  
  const [data, setData] = useState<Therapist[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState('');
  const [selectedBranch, setSelectedBranch] = useState<string | undefined>(undefined);
  const [branches, setBranches] = useState<TeacherBranch[]>([]);
  
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingTherapist, setEditingTherapist] = useState<any | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [modules, setModules] = useState<Module[]>(DEFAULT_MODULES);

  useEffect(() => {
    fetchTherapists();
    fetchModules();
    fetchBranches();
  }, [selectedBranch]);

  const fetchBranches = async () => {
    try {
      const bData = await getBranches();
      setBranches(bData || []);
    } catch (e) {
      console.error('Branşlar yüklenemedi', e);
    }
  };

  const fetchTherapists = async () => {
    setLoading(true);
    try {
      const response = await getTherapists();
      setData(response.data);
      setTotal(response.total);
    } catch (error) {
      message.error('Öğretmenler yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const response = await getModules();
      setModules(Array.isArray(response) ? response : (response as any)?.data || []);
    } catch (error) {
      console.error('Modüller yüklenemedi', error);
    }
  };

  const handleOpenCreate = () => {
    setEditingTherapist(null);
    form.resetFields();
    if (branches.length > 0) {
      form.setFieldsValue({ branch: branches[0].name });
    }
    setIsModalVisible(true);
  };

  const handleOpenEdit = (record: any) => {
    setEditingTherapist(record);
    form.resetFields();

    // Map availabilities to days
    const activeDays = new Set((record.availabilities || []).map((a: any) => a.dayOfWeek));

    form.setFieldsValue({
      firstName: record.firstName,
      lastName: record.lastName,
      tcKimlik: record.tcKimlik || '',
      title: record.title || '',
      branch: record.branch || record.title || (branches[0]?.name || 'Özel Eğitim Alanı Öğretmeni'),
      phone: record.phone || '',
      email: record.email || '',
      weeklyHours: record.weeklyHours || 40,
      modules: (record.specializations || []).map((s: any) => String(s.moduleId)),
      monday: activeDays.has(1),
      tuesday: activeDays.has(2),
      wednesday: activeDays.has(3),
      thursday: activeDays.has(4),
      friday: activeDays.has(5)
    });
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    setEditingTherapist(null);
    form.resetFields();
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTherapist(id);
      message.success('Öğretmen silindi.');
      fetchTherapists();
    } catch (error) {
      message.error('Silme işleminde hata oluştu.');
    }
  };

  const handleAddOrUpdate = async (values: any) => {
    setSubmitting(true);
    try {
      // Map module selection to specializations
      const specializations = values.modules?.map((moduleId: string) => ({ moduleId })) || [];
      
      // Map days to availabilities
      const availabilities: any[] = [];
      const days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday'];
      days.forEach((day, index) => {
        if (values[day]) {
          availabilities.push({
            dayOfWeek: index + 1,
            startTime: '09:00',
            endTime: '18:00'
          });
        }
      });

      const payload = {
        ...values,
        tcKimlik: values.tcKimlik || values.identityNumber,
        specializations,
        availabilities,
      };

      if (editingTherapist) {
        await updateTherapist(editingTherapist.id, payload);
        message.success('Öğretmen bilgileri başarıyla güncellendi.');
      } else {
        await createTherapist(payload);
        message.success('Öğretmen başarıyla eklendi.');
      }
      setIsModalVisible(false);
      setEditingTherapist(null);
      form.resetFields();
      fetchTherapists();
    } catch (error: any) {
      message.error(error.response?.data?.detail || error.message || 'Öğretmen kaydedilirken bir hata oluştu.');
    } finally {
      setSubmitting(false);
    }
  };

  const filteredData = data.filter(t => {
    const matchesSearch = `${t.firstName} ${t.lastName} ${t.title || ''} ${t.branch || ''}`.toLowerCase().includes(searchText.toLowerCase());
    const matchesBranch = selectedBranch ? (t.branch === selectedBranch || t.title === selectedBranch) : true;
    return matchesSearch && matchesBranch;
  });

  const columns = [
    {
      title: 'Ad Soyad',
      key: 'name',
      render: (text: string, record: Therapist) => <strong>{record.firstName} {record.lastName}</strong>,
    },
    {
      title: 'Öğretmen Branşı',
      key: 'branch',
      render: (_: any, record: Therapist) => {
        const bName = record.branch || record.title || 'Özel Eğitim Öğretmeni';
        const bObj = branches.find(b => b.name === bName);
        return (
          <Tag color={bObj?.color || "purple"} style={{ fontWeight: 500, fontSize: '13px', padding: '3px 8px' }}>
            {bName}
          </Tag>
        );
      },
    },
    {
      title: 'Kadro / Unvan',
      dataIndex: 'title',
      key: 'title',
      render: (t: string) => t || '-'
    },
    {
      title: 'Uyguladığı Terapi Modülleri',
      key: 'specializations',
      render: (text: string, record: Therapist) => (
        <Space wrap size={[0, 4]}>
          {record.specializations?.map(spec => {
            const mod = modules.find(m => String(m.id) === String(spec.moduleId));
            return (
              <Tag color={mod?.color || "blue"} key={spec.moduleId}>
                {mod ? mod.name : `Modül ${spec.moduleId}`}
              </Tag>
            );
          })}
        </Space>
      ),
    },
    {
      title: 'Haftalık Saat',
      dataIndex: 'weeklyHours',
      key: 'weeklyHours',
      render: (h: number) => `${h || 40} Saat`
    },
    {
      title: 'Doluluk',
      key: 'workload',
      render: (text: string, record: Therapist) => {
        const percent = (record.weeklyHours && record.currentWorkload) ? Math.round((record.currentWorkload / record.weeklyHours) * 100) : 0;
        return <Progress percent={percent} size="small" status={percent >= 100 ? "exception" : "active"} />;
      },
    },
    {
      title: 'İşlemler',
      key: 'actions',
      render: (text: string, record: Therapist) => (
        <Space size="small">
          <Tooltip title="Detay">
            <Button 
              type="text" 
              icon={<EyeOutlined />} 
              onClick={() => navigate(`/therapists/${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="Düzenle">
            <Button 
              type="text" 
              icon={<EditOutlined style={{ color: '#1890ff' }} />} 
              onClick={() => handleOpenEdit(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Öğretmeni silmek istediğinize emin misiniz?"
            onConfirm={() => handleDelete(record.id)}
            okText="Evet"
            cancelText="İptal"
          >
            <Tooltip title="Sil">
              <Button 
                type="text" 
                danger 
                icon={<DeleteOutlined />} 
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.4rem' }}>Öğretmenler & Terapistler</h2>
          <span style={{ color: '#888' }}>Eğitmen kadrosu, MEB branş atamaları ve haftalık ders dolulukları</span>
        </div>
        <Space wrap>
          <Input 
            placeholder="İsim veya branşla ara..." 
            prefix={<SearchOutlined />} 
            value={searchText}
            onChange={e => setSearchText(e.target.value)}
            style={{ width: 220 }}
            allowClear
          />
          <Select
            allowClear
            placeholder="Branşa Göre Filtrele"
            style={{ minWidth: 220 }}
            value={selectedBranch}
            onChange={setSelectedBranch}
            options={branches.map(b => ({ value: b.name, label: `${b.name} (${b.teacherCount || 0})` }))}
          />
          <Button icon={<ReloadOutlined />} onClick={() => { fetchTherapists(); fetchBranches(); }}>Yenile</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
            Yeni Öğretmen Ekle
          </Button>
        </Space>
      </div>

      <Table 
        columns={columns} 
        dataSource={filteredData} 
        rowKey="id" 
        loading={loading}
        pagination={{ total: filteredData.length, showSizeChanger: true }}
        scroll={{ x: 800 }}
      />

      <Modal 
        title={editingTherapist ? "Öğretmen Bilgilerini Düzenle" : "Yeni Öğretmen Ekle"} 
        open={isModalVisible} 
        onCancel={handleCancel}
        footer={null}
        width="95%"
        style={{ maxWidth: 700 }}
      >
        <Form layout="vertical" form={form} onFinish={handleAddOrUpdate}>
          <Row gutter={[16, 12]}>
            <Col xs={24} sm={12}>
              <Form.Item name="firstName" label="Ad">
                <Input placeholder="Örn: Ayşe" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="lastName" label="Soyad">
                <Input placeholder="Örn: Demir" />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={[16, 12]}>
            <Col xs={24} sm={12}>
              <Form.Item name="tcKimlik" label="TC Kimlik (Opsiyonel)">
                <Input maxLength={11} placeholder="Girilmezse otomatik atanır" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="branch" label="Öğretmen Branşı" rules={[{ required: true, message: 'Lütfen branş seçiniz' }]}>
                <Select
                  placeholder="Branş seçiniz (Örn: Özel Eğitim, Fizyoterapist...)"
                  showSearch
                  optionFilterProp="label"
                  options={branches.map(b => ({ value: b.name, label: b.name }))}
                />
              </Form.Item>
            </Col>
          </Row>
          
          <Row gutter={[16, 12]}>
            <Col xs={24} sm={12}>
              <Form.Item name="title" label="Kadro / Unvan (Opsiyonel)" initialValue="Öğretmen">
                <Input placeholder="Örn: Uzman Öğretici, Terapist, Zümre Başkanı" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="phone" label="Telefon (Opsiyonel)">
                <Input placeholder="05XX XXX XX XX" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="email" label="Email (Opsiyonel)">
                <Input placeholder="ornek@eposta.com" />
              </Form.Item>
            </Col>
            <Col xs={24} sm={12}>
              <Form.Item name="weeklyHours" label="Haftalık Saat" initialValue={40}>
                <InputNumber min={1} max={60} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={[16, 12]}>
            <Col xs={24}>
              <Form.Item name="modules" label="Verdiği Terapi & Destek Modülleri">
                <Select mode="multiple" placeholder="Eğitim modüllerini seçiniz">
                  {modules.map(m => (
                    <Option key={m.id} value={m.id}>{m.name}</Option>
                  ))}
                </Select>
              </Form.Item>
            </Col>
          </Row>

          <Form.Item label="Müsaitlik (Günler)">
            <Space wrap>
              <Form.Item name="monday" valuePropName="checked" noStyle initialValue={true}>
                <Checkbox>Pzt</Checkbox>
              </Form.Item>
              <Form.Item name="tuesday" valuePropName="checked" noStyle initialValue={true}>
                <Checkbox>Sal</Checkbox>
              </Form.Item>
              <Form.Item name="wednesday" valuePropName="checked" noStyle initialValue={true}>
                <Checkbox>Çar</Checkbox>
              </Form.Item>
              <Form.Item name="thursday" valuePropName="checked" noStyle initialValue={true}>
                <Checkbox>Per</Checkbox>
              </Form.Item>
              <Form.Item name="friday" valuePropName="checked" noStyle initialValue={true}>
                <Checkbox>Cum</Checkbox>
              </Form.Item>
            </Space>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0 }}>
            <Space style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={handleCancel}>İptal</Button>
              <Button type="primary" htmlType="submit" loading={submitting}>
                Kaydet
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default TherapistsPage;
