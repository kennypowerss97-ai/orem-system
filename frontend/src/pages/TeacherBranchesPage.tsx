import React, { useState, useEffect } from 'react';
import { Table, Card, Button, Input, Space, Tag, Modal, Form, message, Popconfirm, Tooltip, Row, Col, Statistic, Badge } from 'antd';
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, ApartmentOutlined, UserOutlined, TeamOutlined } from '@ant-design/icons';
import { getBranches, createBranch, updateBranch, deleteBranch } from '../api/branches';
import { TeacherBranch } from '../types';

const PRESET_COLORS = [
  '#1890ff', '#722ed1', '#eb2f96', '#fa8c16', '#52c41a',
  '#13c2c2', '#2f54eb', '#faad14', '#fa541c', '#a0d911', '#096dd9'
];

export const TeacherBranchesPage: React.FC = () => {
  const [branches, setBranches] = useState<TeacherBranch[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBranch, setEditingBranch] = useState<TeacherBranch | null>(null);
  const [saving, setSaving] = useState(false);
  const [selectedColor, setSelectedColor] = useState('#1890ff');
  const [form] = Form.useForm();

  const fetchBranches = async () => {
    setLoading(true);
    try {
      const data = await getBranches();
      setBranches(data || []);
    } catch (e) {
      message.error('Öğretmen branşları yüklenirken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBranches();
  }, []);

  const handleOpenCreate = () => {
    setEditingBranch(null);
    form.resetFields();
    setSelectedColor('#1890ff');
    setIsModalOpen(true);
  };

  const handleOpenEdit = (branch: TeacherBranch) => {
    setEditingBranch(branch);
    form.resetFields();
    setSelectedColor(branch.color || '#1890ff');
    form.setFieldsValue({
      name: branch.name,
      code: branch.code,
      description: branch.description,
      color: branch.color || '#1890ff',
      isActive: branch.isActive
    });
    setIsModalOpen(true);
  };

  const handleSave = async () => {
    try {
      const values = await form.validateFields();
      setSaving(true);
      const payload = {
        ...values,
        color: selectedColor
      };

      if (editingBranch) {
        await updateBranch(editingBranch.id, payload);
        message.success('Branş bilgileri güncellendi! 🎉');
      } else {
        await createBranch(payload);
        message.success('Yeni öğretmen branşı başarıyla eklendi! 🎉');
      }
      setIsModalOpen(false);
      form.resetFields();
      fetchBranches();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'İşlem sırasında hata oluştu.');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteBranch(id);
      message.success('Branş başarıyla silindi.');
      fetchBranches();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Silme işleminde hata oluştu.');
    }
  };

  const filteredBranches = branches.filter(b =>
    b.name.toLowerCase().includes(search.toLowerCase()) ||
    (b.description && b.description.toLowerCase().includes(search.toLowerCase())) ||
    b.code.toLowerCase().includes(search.toLowerCase())
  );

  const totalTeachers = branches.reduce((sum, b) => sum + (b.teacherCount || 0), 0);

  const columns = [
    {
      title: 'Branş Adı',
      key: 'name',
      render: (_: any, r: TeacherBranch) => (
        <Space>
          <span style={{
            display: 'inline-block',
            width: 12,
            height: 12,
            borderRadius: '50%',
            backgroundColor: r.color || '#1890ff'
          }} />
          <strong>{r.name}</strong>
        </Space>
      )
    },
    {
      title: 'Branş Kodu',
      dataIndex: 'code',
      key: 'code',
      render: (code: string) => <Tag>{code}</Tag>
    },
    {
      title: 'Açıklama / Kapsam',
      dataIndex: 'description',
      key: 'description',
      render: (desc: string) => desc || '-'
    },
    {
      title: 'Kayıtlı Öğretmen',
      key: 'teacherCount',
      render: (_: any, r: TeacherBranch) => (
        <Tag color="cyan" icon={<UserOutlined />}>
          {r.teacherCount || 0} Öğretmen
        </Tag>
      )
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
      key: 'action',
      render: (_: any, record: TeacherBranch) => (
        <Space size="small">
          <Tooltip title="Düzenle">
            <Button icon={<EditOutlined />} onClick={() => handleOpenEdit(record)} />
          </Tooltip>
          <Popconfirm
            title="Bu branşı silmek istediğinize emin misiniz?"
            description="Branşa kayıtlı öğretmenlerin branş alanı boş kalabilir."
            onConfirm={() => handleDelete(record.id)}
            okText="Evet, Sil"
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <ApartmentOutlined style={{ color: '#1890ff' }} /> Öğretmen Branşları Yönetimi
          </h2>
          <span style={{ color: '#888' }}>
            MEB Özel Eğitim standartlarına uygun eğitmen branşları, uzmanlık alanları ve kadro dağılımı
          </span>
        </div>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={fetchBranches}>Yenile</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
            Yeni Branş Ekle
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Toplam Branş Sayısı"
              value={branches.length}
              prefix={<ApartmentOutlined style={{ color: '#1890ff' }} />}
              suffix="Branş"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Kadroda Görevli Öğretmen"
              value={totalTeachers}
              prefix={<TeamOutlined style={{ color: '#52c41a' }} />}
              suffix="Eğitmen"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Aktif MEB Branşları"
              value={branches.filter(b => b.isActive).length}
              prefix={<Badge status="processing" />}
              suffix="Aktif"
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="Branş adı veya açıklamasına göre ara..."
            prefix={<SearchOutlined />}
            style={{ maxWidth: 360 }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
        </div>

        <Table
          loading={loading}
          rowKey="id"
          columns={columns}
          dataSource={filteredBranches}
          pagination={{ pageSize: 12 }}
          scroll={{ x: 750 }}
        />
      </Card>

      <Modal
        title={editingBranch ? "Öğretmen Branşını Düzenle" : "Yeni Öğretmen Branşı Ekle"}
        open={isModalOpen}
        onCancel={() => { setIsModalOpen(false); form.resetFields(); }}
        onOk={handleSave}
        confirmLoading={saving}
        okText="Kaydet"
        cancelText="İptal"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            name="name"
            label="Branş Adı"
            rules={[{ required: true, message: 'Lütfen branş adını giriniz' }]}
          >
            <Input placeholder="Örn: Özel Eğitim Alanı Öğretmeni, Fizyoterapist..." />
          </Form.Item>

          <Form.Item name="code" label="Branş Kodu (Opsiyonel)">
            <Input placeholder="Örn: OZEL_EGITIM, FIZYOTERAPI..." />
          </Form.Item>

          <Form.Item name="description" label="Açıklama / Kapsam">
            <Input.TextArea rows={3} placeholder="Branşın uzmanlık alanı ve uyguladığı eğitim türleri..." />
          </Form.Item>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>Branş Renk Rozeti:</label>
            <Space wrap>
              {PRESET_COLORS.map(c => (
                <div
                  key={c}
                  onClick={() => setSelectedColor(c)}
                  style={{
                    width: 28,
                    height: 28,
                    borderRadius: '50%',
                    backgroundColor: c,
                    cursor: 'pointer',
                    border: selectedColor === c ? '3px solid #000' : '2px solid #fff',
                    boxShadow: '0 0 4px rgba(0,0,0,0.3)',
                    transform: selectedColor === c ? 'scale(1.15)' : 'scale(1)',
                    transition: 'all 0.2s'
                  }}
                />
              ))}
            </Space>
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default TeacherBranchesPage;
