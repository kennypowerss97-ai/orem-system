import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Space, Tag, Modal, Steps, Form, Select, DatePicker, message, Popconfirm, Row, Col, Tooltip } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined, DeleteOutlined, ReloadOutlined, EditOutlined, UserOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getStudents, createStudent, updateStudent, deleteStudent } from '../api/students';
import { getModules } from '../api/modules';
import { getTherapists } from '../api/therapists';
import { getDisabilities, DisabilityItem } from '../api/disabilities';
import dayjs from 'dayjs';

const { Step } = Steps;

const StudentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [students, setStudents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedDisability, setSelectedDisability] = useState<string | undefined>(undefined);
  
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [editingStudent, setEditingStudent] = useState<any | null>(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [modules, setModules] = useState<any[]>([]);
  const [therapists, setTherapists] = useState<any[]>([]);
  const [disabilities, setDisabilities] = useState<DisabilityItem[]>([]);
  const [form] = Form.useForm();

  const fetchStudents = async () => {
    setLoading(true);
    try {
      const res = await getStudents({ search, disability_type: selectedDisability });
      setStudents(res.data || []);
    } catch (e) {
      message.error('Öğrenciler yüklenemedi.');
    } finally {
      setLoading(false);
    }
  };

  const fetchDependencies = async () => {
    try {
      const [mRes, tRes, dRes] = await Promise.all([
        getModules().catch(() => []),
        getTherapists().catch(() => ({ data: [] })),
        getDisabilities().catch(() => [])
      ]);
      setModules(Array.isArray(mRes) ? mRes : (mRes as any)?.data || []);
      setTherapists(Array.isArray(tRes) ? tRes : (tRes as any)?.data || []);
      setDisabilities(Array.isArray(dRes) ? dRes : (dRes as any)?.data || []);
    } catch (e) {
      console.error('Bağımlılıklar yüklenirken hata:', e);
    }
  };

  useEffect(() => {
    fetchStudents();
    fetchDependencies();
  }, [selectedDisability]);

  const handleDelete = async (id: string) => {
    try {
      await deleteStudent(id);
      message.success('Öğrenci silindi.');
      fetchStudents();
    } catch (e) {
      message.error('Silme işleminde hata oluştu.');
    }
  };

  const handleOpenCreate = () => {
    setEditingStudent(null);
    form.resetFields();
    setCurrentStep(0);
    setIsModalVisible(true);
  };

  const handleOpenEdit = (student: any) => {
    setEditingStudent(student);
    setCurrentStep(0);
    form.resetFields();
    form.setFieldsValue({
      firstName: student.firstName,
      lastName: student.lastName,
      tcKimlik: student.tcKimlik,
      birthDate: student.birthDate ? dayjs(student.birthDate) : undefined,
      gender: student.gender || 'Erkek',
      disabilityType: student.disabilityType,
      preferredTherapistId: student.preferredTherapistId,
      notes: student.notes || '',
      guardianName: student.guardian?.name || '',
      guardianPhone: student.guardian?.phone || '',
      guardianRel: student.guardian?.relationship || 'Anne',
      guardianEmail: student.guardian?.email || '',
      ramReportNo: student.ramReport?.reportNumber || '',
      issuingRam: student.ramReport?.issuingRam || 'Kadıköy RAM',
      selectedModules: student.allocatedModules?.map((m: any) => String(m.moduleId)) || []
    });
    setIsModalVisible(true);
  };

  const handleFinish = async () => {
    try {
      // Zorunlu alan yok - getFieldsValue ile tüm değerler okunur
      const values = form.getFieldsValue(true);
      setSaving(true);

      const payload = {
        firstName: values.firstName || 'Yeni Öğrenci',
        lastName: values.lastName || '',
        tcKimlik: values.tcKimlik || '',
        birthDate: values.birthDate ? (typeof values.birthDate.format === 'function' ? values.birthDate.format('YYYY-MM-DD') : String(values.birthDate)) : '2018-01-01',
        gender: values.gender || 'Erkek',
        disabilityType: values.disabilityType || (disabilities[0]?.name || 'Özel Eğitim'),
        preferredTherapistId: values.preferredTherapistId || null,
        notes: values.notes || '',
        guardian: {
          name: values.guardianName || '',
          phone: values.guardianPhone || '',
          email: values.guardianEmail || '',
          relationship: values.guardianRel || 'Veli'
        },
        ramReport: {
          reportNumber: values.ramReportNo || '',
          issuingRam: values.issuingRam || 'İlçe RAM'
        },
        allocatedModules: (values.selectedModules && values.selectedModules.length > 0)
          ? values.selectedModules.map((mId: string) => ({
              moduleId: Number(mId),
              quotaHours: values[`quota_${mId}`] || 8
            }))
          : modules.slice(0, 1).map(m => ({ moduleId: Number(m.id), quotaHours: 8 }))
      };

      if (editingStudent) {
        await updateStudent(editingStudent.id, payload);
        message.success('Öğrenci bilgileri başarıyla güncellendi! 🎉');
      } else {
        await createStudent(payload);
        message.success('Öğrenci başarıyla kaydedildi ve ders programına yerleştirildi! 🎉');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingStudent(null);
      setCurrentStep(0);
      fetchStudents();
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'İşlem sırasında hata oluştu.');
    } finally {
      setSaving(false);
    }
  };

  const columns = [
    {
      title: 'Ad Soyad',
      key: 'name',
      render: (_: any, r: any) => <strong>{r.firstName} {r.lastName}</strong>
    },
    { title: 'TC Kimlik', dataIndex: 'tcKimlik', key: 'tcKimlik' },
    { title: 'Doğum Tarihi', dataIndex: 'birthDate', key: 'birthDate' },
    {
      title: 'Engel / Tanı Türü',
      dataIndex: 'disabilityType',
      key: 'disabilityType',
      render: (d: string) => <Tag color="blue">{d || 'Belirtilmemiş'}</Tag>
    },
    {
      title: 'Bireysel Öğretmen',
      key: 'preferredTherapist',
      render: (_: any, r: any) => r.preferredTherapistName ? (
        <Tag color="purple" icon={<UserOutlined />}>{r.preferredTherapistName}</Tag>
      ) : (
        <span style={{ color: '#aaa' }}>Otomatik Dağıtım</span>
      )
    },
    {
      title: 'Veli',
      key: 'guardian',
      render: (_: any, r: any) => r.guardian?.name ? `${r.guardian.name} (${r.guardian.phone || '-'})` : '-'
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => <Tag color={status === 'active' ? 'green' : 'red'}>{status === 'active' ? 'Aktif' : 'Pasif'}</Tag>
    },
    {
      title: 'İşlemler',
      key: 'action',
      render: (_: any, record: any) => (
        <Space size="small">
          <Tooltip title="Detay">
            <Button icon={<EyeOutlined />} onClick={() => navigate(`/students/${record.id}`)} />
          </Tooltip>
          <Tooltip title="Düzenle">
            <Button icon={<EditOutlined />} onClick={() => handleOpenEdit(record)} />
          </Tooltip>
          <Popconfirm
            title="Öğrenciyi silmek istediğinize emin misiniz?"
            onConfirm={() => handleDelete(record.id)}
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

  const disabilityOptions = disabilities.map(d => ({ value: d.name, label: d.name }));

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.4rem' }}>Öğrenci Yönetimi</h2>
          <span style={{ color: '#888' }}>Kayıt, RAM Raporu, Bireysel Öğretmen Seçimi ve Modül İşlemleri</span>
        </div>
        <Space wrap>
          <Button icon={<ReloadOutlined />} onClick={fetchStudents}>Yenile</Button>
          <Button type="primary" icon={<PlusOutlined />} onClick={handleOpenCreate}>
            Yeni Öğrenci Ekle
          </Button>
        </Space>
      </div>

      <div style={{ marginBottom: 16, display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <Input
          placeholder="Öğrenci Adı, Soyadı veya TC ile Ara..."
          prefix={<SearchOutlined />}
          style={{ minWidth: 240, flex: 1 }}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          onPressEnter={fetchStudents}
        />
        <Select
          allowClear
          placeholder="Engel Türüne Göre Filtrele"
          style={{ minWidth: 220, flex: 1 }}
          value={selectedDisability}
          onChange={setSelectedDisability}
          options={disabilityOptions}
        />
        <Button type="primary" onClick={fetchStudents}>Filtrele</Button>
      </div>

      <Table
        loading={loading}
        rowKey="id"
        columns={columns}
        dataSource={students}
        pagination={{ pageSize: 10 }}
        scroll={{ x: 800 }}
      />

      <Modal
        title={editingStudent ? "Öğrenci Bilgilerini Düzenle" : "Yeni Öğrenci Kaydı (Zorunlu Alan Yok)"}
        open={isModalVisible}
        onCancel={() => { setIsModalVisible(false); setEditingStudent(null); setCurrentStep(0); form.resetFields(); }}
        footer={null}
        width="95%"
        style={{ maxWidth: 720 }}
        destroyOnClose={false}
      >
        <Steps current={currentStep} size="small" responsive={true} style={{ marginBottom: 24 }}>
          <Step title="Kişisel Bilgiler" />
          <Step title="Veli Bilgisi" />
          <Step title="RAM Raporu" />
          <Step title="Öğretmen & Modül" />
        </Steps>

        <Form form={form} layout="vertical" preserve={true}>
          {/* Adım 1: Kişisel Bilgiler */}
          <div style={{ display: currentStep === 0 ? 'block' : 'none' }}>
            <Row gutter={[16, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="firstName" label="Öğrenci Adı">
                  <Input placeholder="Örn: Ahmet (Opsiyonel)" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="lastName" label="Öğrenci Soyadı">
                  <Input placeholder="Örn: Yılmaz (Opsiyonel)" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="tcKimlik" label="TC Kimlik No (Opsiyonel)">
                  <Input maxLength={11} placeholder="Girilmezse otomatik üretilir" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="birthDate" label="Doğum Tarihi (Opsiyonel)">
                  <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" placeholder="Tarih seçiniz" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="gender" label="Cinsiyet" initialValue="Erkek">
                  <Select options={[{ value: 'Erkek', label: 'Erkek' }, { value: 'Kız', label: 'Kız' }]} />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="disabilityType" label="Engel / Tanı Türü">
                  <Select
                    options={disabilityOptions}
                    placeholder="Tanı seçiniz (Ayarlardan düzenlenebilir)"
                    allowClear
                    showSearch
                  />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* Adım 2: Veli Bilgisi */}
          <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
            <Row gutter={[16, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="guardianName" label="Veli Adı Soyadı (Opsiyonel)">
                  <Input placeholder="Örn: Mehmet Yılmaz" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="guardianPhone" label="İletişim Telefonu (Opsiyonel)">
                  <Input placeholder="Örn: 0532 123 4567" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="guardianRel" label="Yakınlık Derecesi" initialValue="Anne">
                  <Select options={[{ value: 'Anne', label: 'Anne' }, { value: 'Baba', label: 'Baba' }, { value: 'Vasi', label: 'Vasi' }]} />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="guardianEmail" label="E-Posta (Opsiyonel)">
                  <Input placeholder="veli@eposta.com" />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* Adım 3: RAM Raporu */}
          <div style={{ display: currentStep === 2 ? 'block' : 'none' }}>
            <Row gutter={[16, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="ramReportNo" label="RAM Rapor Numarası (Opsiyonel)">
                  <Input placeholder="Örn: RAM-2026-9812" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="issuingRam" label="Düzenleyen RAM Merkezi" initialValue="Kadıköy RAM">
                  <Input placeholder="Örn: Kadıköy RAM" />
                </Form.Item>
              </Col>
            </Row>
          </div>

          {/* Adım 4: Öğretmen Seçimi ve Modül Atama */}
          <div style={{ display: currentStep === 3 ? 'block' : 'none' }}>
            <div style={{ marginBottom: 16 }}>
              <Form.Item
                name="preferredTherapistId"
                label={
                  <span>
                    <strong>Bireysel Öğretmen / Tercih Edilen Eğitmen</strong> (Özel İstek)
                  </span>
                }
                tooltip="Öğrencinin derslerini özellikle almasını istediğiniz bir öğretmen varsa seçin. Otomatik ders programında bu öğretmene öncelik tanınacaktır."
              >
                <Select
                  allowClear
                  showSearch
                  placeholder="Bireysel seanslar için öğretmen seçiniz (İsteğe bağlı)"
                  optionFilterProp="label"
                  options={therapists.map(t => ({
                    value: t.id,
                    label: `${t.firstName} ${t.lastName} (${t.title || 'Öğretmen'})`
                  }))}
                />
              </Form.Item>

              <Form.Item name="selectedModules" label="Destek Eğitim Modülleri (Seçilmezse varsayılan atanır)">
                <Select
                  mode="multiple"
                  placeholder="Eğitim Modüllerini Seçin"
                  options={modules.map(m => ({ value: String(m.id), label: m.name }))}
                />
              </Form.Item>

              <div style={{ backgroundColor: '#f6ffed', padding: 12, border: '1px solid #b7eb8f', borderRadius: 6, marginBottom: 16 }}>
                💡 <strong>Esnek Kayıt:</strong> Hiçbir alan zorunlu değildir. İsterseniz sadece öğrenci adını girip kaydedebilirsiniz. Seçtiğiniz öğretmen ve modüllere göre seanslar programdaki en uygun boşluklara yerleştirilir.
              </div>
            </div>
          </div>

          <div style={{ marginTop: 24, textAlign: 'right' }}>
            {currentStep > 0 && (
              <Button style={{ marginRight: 8 }} onClick={() => setCurrentStep(currentStep - 1)}>
                Geri
              </Button>
            )}
            {currentStep < 3 && (
              <Button type="primary" onClick={() => setCurrentStep(currentStep + 1)}>
                İleri
              </Button>
            )}
            {currentStep === 3 && (
              <Button type="primary" loading={saving} onClick={handleFinish} style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}>
                {editingStudent ? 'Değişiklikleri Güncelle' : 'Kaydet ve Tamamla'}
              </Button>
            )}
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default StudentsPage;
