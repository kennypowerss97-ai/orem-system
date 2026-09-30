import React, { useState, useEffect } from 'react';
import { Table, Button, Input, Space, Tag, Modal, Steps, Form, Select, DatePicker, message, Popconfirm, Row, Col, InputNumber, Tooltip } from 'antd';
import { PlusOutlined, SearchOutlined, EyeOutlined, DeleteOutlined, ReloadOutlined, EditOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { getStudents, createStudent, updateStudent, deleteStudent } from '../api/students';
import { getModules } from '../api/modules';
import dayjs from 'dayjs';

const { Step } = Steps;

const DISABILITY_OPTIONS = [
  { value: 'Otizm Spektrum Bozukluğu', label: 'Otizm Spektrum Bozukluğu' },
  { value: 'Serebral Palsi (Bedensel)', label: 'Serebral Palsi (Bedensel)' },
  { value: 'Özel Öğrenme Güçlüğü (Disleksi)', label: 'Özel Öğrenme Güçlüğü (Disleksi)' },
  { value: 'Dil ve Konuşma Bozukluğu', label: 'Dil ve Konuşma Bozukluğu' },
  { value: 'Zihinsel Yetersizlik', label: 'Zihinsel Yetersizlik' },
  { value: 'İşitme Yetersizliği', label: 'İşitme Yetersizliği' },
  { value: 'Down Sendromu', label: 'Down Sendromu' }
];

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

  const fetchAvailableModules = async () => {
    try {
      const res = await getModules();
      setModules(res || []);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchStudents();
    fetchAvailableModules();
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
      const values = await form.validateFields();
      setSaving(true);

      const payload = {
        firstName: values.firstName,
        lastName: values.lastName,
        tcKimlik: values.tcKimlik,
        birthDate: values.birthDate ? (typeof values.birthDate.format === 'function' ? values.birthDate.format('YYYY-MM-DD') : String(values.birthDate)) : '2018-01-01',
        gender: values.gender || 'Erkek',
        disabilityType: values.disabilityType,
        notes: values.notes || '',
        guardian: {
          name: values.guardianName,
          phone: values.guardianPhone,
          email: values.guardianEmail || '',
          relationship: values.guardianRel || 'Veli'
        },
        ramReport: {
          reportNumber: values.ramReportNo,
          issuingRam: values.issuingRam || 'İlçe RAM'
        },
        allocatedModules: (values.selectedModules || []).map((mId: string) => ({
          moduleId: Number(mId),
          quotaHours: values[`quota_${mId}`] || 8
        }))
      };

      if (editingStudent) {
        await updateStudent(editingStudent.id, payload);
        message.success('Öğrenci bilgileri başarıyla güncellendi! 🎉');
      } else {
        await createStudent(payload);
        message.success('Öğrenci başarıyla kaydedildi ve ders programındaki boşluklara otomatik yerleştirildi! 🎉');
      }
      setIsModalVisible(false);
      form.resetFields();
      setEditingStudent(null);
      setCurrentStep(0);
      fetchStudents();
    } catch (err: any) {
      if (err?.errorFields && err.errorFields.length > 0) {
        const errorFieldNames = err.errorFields.map((f: any) => f.name[0]);
        if (errorFieldNames.some((f: string) => ['firstName', 'lastName', 'tcKimlik', 'birthDate', 'disabilityType'].includes(f))) {
          setCurrentStep(0);
        } else if (errorFieldNames.some((f: string) => ['guardianName', 'guardianPhone', 'guardianRel', 'guardianEmail'].includes(f))) {
          setCurrentStep(1);
        } else if (errorFieldNames.some((f: string) => ['ramReportNo', 'issuingRam'].includes(f))) {
          setCurrentStep(2);
        } else {
          setCurrentStep(3);
        }
        message.warning(err.errorFields[0]?.errors[0] || 'Lütfen formu eksiksiz doldurun.');
      } else {
        message.error(err.response?.data?.detail || 'İşlem sırasında hata oluştu.');
      }
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
      render: (d: string) => <Tag color="blue">{d}</Tag>
    },
    {
      title: 'Veli',
      key: 'guardian',
      render: (_: any, r: any) => r.guardian ? `${r.guardian.name} (${r.guardian.phone})` : '-'
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

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <div>
          <h2 style={{ margin: 0, fontSize: '1.4rem' }}>Öğrenci Yönetimi</h2>
          <span style={{ color: '#888' }}>Kayıt, RAM Raporu, Modül ve Veli İşlemleri</span>
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
          options={DISABILITY_OPTIONS}
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
        title={editingStudent ? "Öğrenci Bilgilerini Düzenle" : "Yeni Öğrenci ve RAM Raporu Kaydı"}
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
          <Step title="Modül Atama" />
        </Steps>

        <Form form={form} layout="vertical" preserve={true}>
          <div style={{ display: currentStep === 0 ? 'block' : 'none' }}>
            <Row gutter={[16, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="firstName" label="Öğrenci Adı" rules={[{ required: true, message: 'Zorunlu alan' }]}>
                  <Input placeholder="Örn: Ahmet" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="lastName" label="Öğrenci Soyadı" rules={[{ required: true, message: 'Zorunlu alan' }]}>
                  <Input placeholder="Örn: Yılmaz" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item
                  name="tcKimlik"
                  label="TC Kimlik No"
                  rules={[
                    { required: true, message: 'TC Kimlik numarası zorunludur' },
                    { len: 11, message: 'TC Kimlik 11 haneli olmalıdır' },
                    { pattern: /^[0-9]+$/, message: 'Yalnızca rakamlardan oluşmalıdır' }
                  ]}
                >
                  <Input maxLength={11} placeholder="11 haneli TC Kimlik" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="birthDate" label="Doğum Tarihi" rules={[{ required: true, message: 'Zorunlu alan' }]}>
                  <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" placeholder="Tarih seçiniz" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="gender" label="Cinsiyet" initialValue="Erkek">
                  <Select options={[{ value: 'Erkek', label: 'Erkek' }, { value: 'Kız', label: 'Kız' }]} />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="disabilityType" label="Engel / Tanı Türü" rules={[{ required: true, message: 'Zorunlu alan' }]}>
                  <Select options={DISABILITY_OPTIONS} placeholder="Seçiniz" />
                </Form.Item>
              </Col>
            </Row>
          </div>

          <div style={{ display: currentStep === 1 ? 'block' : 'none' }}>
            <Row gutter={[16, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="guardianName" label="Veli Adı Soyadı" rules={[{ required: true, message: 'Zorunlu alan' }]}>
                  <Input placeholder="Örn: Mehmet Yılmaz" />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="guardianPhone" label="İletişim Telefonu" rules={[{ required: true, message: 'Zorunlu alan' }]}>
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

          <div style={{ display: currentStep === 2 ? 'block' : 'none' }}>
            <Row gutter={[16, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="ramReportNo" label="RAM Rapor Numarası" rules={[{ required: true, message: 'Zorunlu alan' }]}>
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

          <div style={{ display: currentStep === 3 ? 'block' : 'none' }}>
            <div>
              <Form.Item name="selectedModules" label="Öğrencinin Alacağı Destek Eğitim Programları" rules={[{ required: true, message: 'En az bir modül seçiniz' }]}>
                <Select
                  mode="multiple"
                  placeholder="Eğitim Modüllerini Seçin"
                  options={modules.map(m => ({ value: String(m.id), label: m.name }))}
                />
              </Form.Item>
              <div style={{ backgroundColor: '#f6ffed', padding: 12, border: '1px solid #b7eb8f', borderRadius: 6, marginBottom: 16 }}>
                💡 <strong>Otomatik Dağıtım:</strong> Öğrenci kaydedildiği anda, seçilen modüllere ait seanslar ilgili branş öğretmenlerinin ve salonların takvimindeki <strong>en uygun boş saatlere otomatik yerleştirilecektir.</strong>
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
              <Button type="primary" onClick={async () => {
                try {
                  if (currentStep === 0) {
                    await form.validateFields(['firstName', 'lastName', 'tcKimlik', 'birthDate', 'disabilityType']);
                  } else if (currentStep === 1) {
                    await form.validateFields(['guardianName', 'guardianPhone', 'guardianRel']);
                  } else if (currentStep === 2) {
                    await form.validateFields(['ramReportNo', 'issuingRam']);
                  }
                  setCurrentStep(currentStep + 1);
                } catch (e) {
                  // validation error
                }
              }}>
                İleri
              </Button>
            )}
            {currentStep === 3 && (
              <Button type="primary" loading={saving} onClick={handleFinish} style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}>
                {editingStudent ? 'Değişiklikleri Güncelle' : 'Kaydet ve Programı Oluştur'}
              </Button>
            )}
          </div>
        </Form>
      </Modal>
    </div>
  );
};

export default StudentsPage;
