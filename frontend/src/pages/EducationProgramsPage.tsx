import React, { useState, useEffect } from 'react';
import { Card, Button, Input, Space, Tag, Modal, Form, message, Popconfirm, Tooltip, Row, Col, Statistic, Collapse, Table, InputNumber, Switch } from 'antd';
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, ReloadOutlined, BookOutlined, AppstoreOutlined, ClockCircleOutlined, CheckCircleOutlined } from '@ant-design/icons';
import {
  getEducationPrograms,
  createEducationProgram,
  updateEducationProgram,
  deleteEducationProgram,
  addProgramModule,
  updateProgramModule,
  deleteProgramModule
} from '../api/programs';
import { EducationProgram, EducationProgramModule } from '../types';

const PRESET_COLORS = [
  '#eb2f96', '#722ed1', '#fa8c16', '#52c41a', '#13c2c2',
  '#fa541c', '#a0d911', '#1890ff', '#2f54eb', '#faad14'
];

export const EducationProgramsPage: React.FC = () => {
  const [programs, setPrograms] = useState<EducationProgram[]>([]);
  const [loading, setLoading] = useState(false);
  const [search, setSearch] = useState('');

  // Program Modal
  const [isProgramModalOpen, setIsProgramModalOpen] = useState(false);
  const [editingProgram, setEditingProgram] = useState<EducationProgram | null>(null);
  const [savingProgram, setSavingProgram] = useState(false);
  const [selectedColor, setSelectedColor] = useState('#1890ff');
  const [programForm] = Form.useForm();

  // Module Modal
  const [isModuleModalOpen, setIsModuleModalOpen] = useState(false);
  const [targetProgramId, setTargetProgramId] = useState<number | null>(null);
  const [editingModule, setEditingModule] = useState<EducationProgramModule | null>(null);
  const [savingModule, setSavingModule] = useState(false);
  const [moduleForm] = Form.useForm();

  const fetchPrograms = async () => {
    setLoading(true);
    try {
      const data = await getEducationPrograms();
      setPrograms(data || []);
    } catch (e) {
      message.error('Destek Eğitim Programları yüklenirken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrograms();
  }, []);

  // Program Handlers
  const handleOpenCreateProgram = () => {
    setEditingProgram(null);
    programForm.resetFields();
    setSelectedColor('#1890ff');
    programForm.setFieldsValue({
      defaultIndividualHours: 8,
      defaultGroupHours: 4
    });
    setIsProgramModalOpen(true);
  };

  const handleOpenEditProgram = (prog: EducationProgram) => {
    setEditingProgram(prog);
    programForm.resetFields();
    setSelectedColor(prog.color || '#1890ff');
    programForm.setFieldsValue({
      name: prog.name,
      code: prog.code,
      description: prog.description,
      defaultIndividualHours: prog.defaultIndividualHours,
      defaultGroupHours: prog.defaultGroupHours
    });
    setIsProgramModalOpen(true);
  };

  const handleSaveProgram = async () => {
    try {
      const values = await programForm.validateFields();
      setSavingProgram(true);
      const payload = {
        ...values,
        color: selectedColor
      };

      if (editingProgram) {
        await updateEducationProgram(editingProgram.id, payload);
        message.success('Destek Eğitim Programı güncellendi! 🎉');
      } else {
        await createEducationProgram(payload);
        message.success('Yeni Destek Eğitim Programı eklendi! 🎉');
      }
      setIsProgramModalOpen(false);
      programForm.resetFields();
      fetchPrograms();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'İşlem sırasında hata oluştu.');
    } finally {
      setSavingProgram(false);
    }
  };

  const handleDeleteProgram = async (id: number) => {
    try {
      await deleteEducationProgram(id);
      message.success('Destek Eğitim Programı silindi.');
      fetchPrograms();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Silme işlemi sırasında hata oluştu.');
    }
  };

  // Module Handlers
  const handleOpenAddModule = (progId: number) => {
    setTargetProgramId(progId);
    setEditingModule(null);
    moduleForm.resetFields();
    moduleForm.setFieldsValue({
      durationMinutes: 45,
      isGroupEligible: true
    });
    setIsModuleModalOpen(true);
  };

  const handleOpenEditModule = (progId: number, mod: EducationProgramModule) => {
    setTargetProgramId(progId);
    setEditingModule(mod);
    moduleForm.resetFields();
    moduleForm.setFieldsValue({
      name: mod.name,
      description: mod.description,
      durationMinutes: mod.durationMinutes || 45,
      isGroupEligible: mod.isGroupEligible
    });
    setIsModuleModalOpen(true);
  };

  const handleSaveModule = async () => {
    try {
      const values = await moduleForm.validateFields();
      setSavingModule(true);

      if (editingModule) {
        await updateProgramModule(editingModule.id, values);
        message.success('Eğitim modülü güncellendi! 🎉');
      } else if (targetProgramId) {
        await addProgramModule(targetProgramId, values);
        message.success('Yeni alt modül programa eklendi! 🎉');
      }
      setIsModuleModalOpen(false);
      moduleForm.resetFields();
      fetchPrograms();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Modül kaydedilirken hata oluştu.');
    } finally {
      setSavingModule(false);
    }
  };

  const handleDeleteModule = async (moduleId: number) => {
    try {
      await deleteProgramModule(moduleId);
      message.success('Modül silindi.');
      fetchPrograms();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Silme işleminde hata oluştu.');
    }
  };

  const filteredPrograms = programs.filter(p =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    (p.description && p.description.toLowerCase().includes(search.toLowerCase())) ||
    p.modules.some(m => m.name.toLowerCase().includes(search.toLowerCase()))
  );

  const totalModulesCount = programs.reduce((sum, p) => sum + (p.modules?.length || 0), 0);

  const collapseItems = filteredPrograms.map(prog => {
    const moduleColumns = [
      {
        title: 'Modül Adı',
        dataIndex: 'name',
        key: 'name',
        render: (name: string) => <strong>{name}</strong>
      },
      {
        title: 'Kazanım ve Açıklama',
        dataIndex: 'description',
        key: 'description',
        render: (desc: string) => desc || '-'
      },
      {
        title: 'Eğitim Türü',
        key: 'type',
        render: (_: any, r: EducationProgramModule) => (
          <Space>
            <Tag color="blue">Bireysel</Tag>
            {r.isGroupEligible ? <Tag color="green">Grup Uygun</Tag> : <Tag color="default">Yalnız Bireysel</Tag>}
          </Space>
        )
      },
      {
        title: 'Ders Süresi',
        dataIndex: 'durationMinutes',
        key: 'durationMinutes',
        render: (mins: number) => <span>{mins || 45} dk</span>
      },
      {
        title: 'İşlemler',
        key: 'actions',
        render: (_: any, mod: EducationProgramModule) => (
          <Space size="small">
            <Tooltip title="Modülü Düzenle">
              <Button size="small" icon={<EditOutlined />} onClick={() => handleOpenEditModule(prog.id, mod)} />
            </Tooltip>
            <Popconfirm
              title="Bu modülü silmek istediğinize emin misiniz?"
              onConfirm={() => handleDeleteModule(mod.id)}
              okText="Evet"
              cancelText="İptal"
            >
              <Tooltip title="Modülü Sil">
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Tooltip>
            </Popconfirm>
          </Space>
        )
      }
    ];

    return {
      key: String(prog.id),
      label: (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', flexWrap: 'wrap', gap: 8 }}>
          <Space size="middle">
            <span style={{
              display: 'inline-block',
              width: 14,
              height: 14,
              borderRadius: '50%',
              backgroundColor: prog.color || '#1890ff'
            }} />
            <span style={{ fontSize: '15px', fontWeight: 600 }}>{prog.name}</span>
            <Tag color="cyan">{prog.modules?.length || 0} Alt Modül</Tag>
            <Tag color="purple">Bireysel: {prog.defaultIndividualHours} Saat/Ay</Tag>
            {prog.defaultGroupHours > 0 && <Tag color="geekblue">Grup: {prog.defaultGroupHours} Saat/Ay</Tag>}
          </Space>
          <div onClick={(e) => e.stopPropagation()} style={{ marginRight: 16 }}>
            <Space>
              <Button size="small" type="primary" ghost icon={<PlusOutlined />} onClick={() => handleOpenAddModule(prog.id)}>
                Modül Ekle
              </Button>
              <Button size="small" icon={<EditOutlined />} onClick={() => handleOpenEditProgram(prog)} />
              <Popconfirm
                title="Bu destek eğitim programını ve tüm modüllerini silmek istediğinize emin misiniz?"
                onConfirm={() => handleDeleteProgram(prog.id)}
                okText="Evet, Sil"
                cancelText="İptal"
              >
                <Button size="small" danger icon={<DeleteOutlined />} />
              </Popconfirm>
            </Space>
          </div>
        </div>
      ),
      children: (
        <div>
          {prog.description && (
            <div style={{ marginBottom: 12, padding: '8px 12px', backgroundColor: '#f5f5f5', borderRadius: 4, color: '#555' }}>
              💡 <strong>Program Kapsamı:</strong> {prog.description}
            </div>
          )}
          <Table
            dataSource={prog.modules || []}
            columns={moduleColumns}
            rowKey="id"
            pagination={false}
            size="small"
          />
        </div>
      )
    };
  });

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.4rem', display: 'flex', alignItems: 'center', gap: 8 }}>
            <BookOutlined style={{ color: '#1890ff' }} /> Öğrencinin Alacağı Destek Eğitim Programları & Modülleri
          </h2>
          <span style={{ color: '#888' }}>
            MEB Rehberlik ve Araştırma Merkezi (RAM) standartlarındaki destek eğitim programları ve alt modül kotaları
          </span>
        </div>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={fetchPrograms}>Yenile</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreateProgram}>
            Yeni Destek Programı Ekle
          </Button>
        </Space>
      </div>

      <Row gutter={[16, 16]} style={{ marginBottom: 20 }}>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Destek Eğitim Programı"
              value={programs.length}
              prefix={<BookOutlined style={{ color: '#1890ff' }} />}
              suffix="Program"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Tanımlı Eğitim Modülleri"
              value={totalModulesCount}
              prefix={<AppstoreOutlined style={{ color: '#52c41a' }} />}
              suffix="Alt Modül"
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card size="small">
            <Statistic
              title="Standart Ders Kotası"
              value="8 Bireysel + 4 Grup"
              prefix={<ClockCircleOutlined style={{ color: '#fa8c16' }} />}
              suffix="Saat/Ay"
            />
          </Card>
        </Col>
      </Row>

      <Card>
        <div style={{ marginBottom: 16 }}>
          <Input
            placeholder="Destek eğitim programı veya modül adına göre ara..."
            prefix={<SearchOutlined />}
            style={{ maxWidth: 400 }}
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            allowClear
          />
        </div>

        <Collapse
          items={collapseItems}
          defaultActiveKey={programs.slice(0, 3).map(p => String(p.id))}
          style={{ background: '#fafafa' }}
        />
      </Card>

      {/* Program Ekle/Düzenle Modal */}
      <Modal
        title={editingProgram ? "Destek Eğitim Programını Düzenle" : "Yeni Destek Eğitim Programı Ekle"}
        open={isProgramModalOpen}
        onCancel={() => { setIsProgramModalOpen(false); programForm.resetFields(); }}
        onOk={handleSaveProgram}
        confirmLoading={savingProgram}
        okText="Kaydet"
        cancelText="İptal"
      >
        <Form form={programForm} layout="vertical">
          <Form.Item
            name="name"
            label="Destek Eğitim Programı Adı"
            rules={[{ required: true, message: 'Lütfen program adını giriniz' }]}
          >
            <Input placeholder="Örn: Zihinsel Engelli Bireyler Destek Eğitim Programı" />
          </Form.Item>

          <Form.Item name="code" label="Program Kodu (Opsiyonel)">
            <Input placeholder="Örn: ZIHINSEL_PROGRAM, OTIZM_PROGRAM..." />
          </Form.Item>

          <Form.Item name="description" label="Açıklama / Kapsam">
            <Input.TextArea rows={3} placeholder="Programın MEB standart tanımı ve hedef kazanımları..." />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="defaultIndividualHours" label="Aylık Standart Bireysel Saat">
                <InputNumber min={0} max={40} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="defaultGroupHours" label="Aylık Standart Grup Saati">
                <InputNumber min={0} max={20} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
          </Row>

          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>Program Renk Rozeti:</label>
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

      {/* Modül Ekle/Düzenle Modal */}
      <Modal
        title={editingModule ? "Alt Modülü Düzenle" : "Programa Yeni Alt Modül Ekle"}
        open={isModuleModalOpen}
        onCancel={() => { setIsModuleModalOpen(false); moduleForm.resetFields(); }}
        onOk={handleSaveModule}
        confirmLoading={savingModule}
        okText="Kaydet"
        cancelText="İptal"
      >
        <Form form={moduleForm} layout="vertical">
          <Form.Item
            name="name"
            label="Modül Adı"
            rules={[{ required: true, message: 'Lütfen modül adını giriniz' }]}
          >
            <Input placeholder="Örn: Öz Bakım Becerileri, Bilişsel Beceriler..." />
          </Form.Item>

          <Form.Item name="description" label="Kazanım ve Açıklama">
            <Input.TextArea rows={3} placeholder="Modülün kapsadığı beceriler ve öğrenci kazanımları..." />
          </Form.Item>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item name="durationMinutes" label="Ders Seans Süresi (Dakika)">
                <InputNumber min={20} max={90} step={5} style={{ width: '100%' }} />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item name="isGroupEligible" label="Grup Eğitimine Uygun mu?" valuePropName="checked">
                <Switch checkedChildren="Uygun" unCheckedChildren="Yalnız Bireysel" />
              </Form.Item>
            </Col>
          </Row>
        </Form>
      </Modal>
    </div>
  );
};

export default EducationProgramsPage;
