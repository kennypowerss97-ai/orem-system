import React, { useEffect, useState } from 'react';
import { Card, Select, Button, Table, Tag, Space, Typography, Modal, Form, DatePicker, Input, Spin, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import { getStudents } from '../api/students';
import { getIepPlans, createIepPlan } from '../api/iep';

dayjs.locale('tr');
const { Title, Text } = Typography;
const { Option } = Select;
const { TextArea } = Input;

export const IepPage: React.FC = () => {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  const [iepPlans, setIepPlans] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    const fetchStudents = async () => {
      try {
        const res = await getStudents();
        setStudents(Array.isArray(res) ? res : (res.data || res.items || []));
      } catch (error) {
        console.error('Öğrenciler alınırken hata:', error);
      }
    };
    fetchStudents();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      const fetchIep = async () => {
        setLoading(true);
        try {
          const plans = await getIepPlans(selectedStudent);
          setIepPlans(plans || []);
        } catch (error) {
          console.error('BEP planları alınırken hata:', error);
        } finally {
          setLoading(false);
        }
      };
      fetchIep();
    } else {
      setIepPlans([]);
    }
  }, [selectedStudent]);

  const handleCreateIep = async (values: any) => {
    if (!selectedStudent) return;
    try {
      const payload = {
        studentId: selectedStudent,
        moduleId: values.moduleId,
        startDate: values.dates[0].toISOString(),
        endDate: values.dates[1].toISOString(),
        notes: values.notes,
        status: 'active'
      };
      await createIepPlan(payload);
      message.success('BEP planı başarıyla oluşturuldu.');
      setIsModalVisible(false);
      form.resetFields();
      
      // Refresh list
      const plans = await getIepPlans(selectedStudent);
      setIepPlans(plans || []);
    } catch (error) {
      console.error(error);
      message.error('BEP planı oluşturulurken hata oluştu.');
    }
  };

  const getStatusTag = (status: string) => {
    switch(status) {
      case 'not_started': return <Tag color="default">Başlamadı</Tag>;
      case 'in_progress': return <Tag color="processing">Devam Ediyor</Tag>;
      case 'acquired': return <Tag color="success">Kazanıldı</Tag>;
      case 'maintained': return <Tag color="purple">Sürdürülüyor</Tag>;
      default: return <Tag>{status}</Tag>;
    }
  };

  const goalColumns = [
    { title: 'Hedef', dataIndex: 'description', key: 'description' },
    { title: 'Durum', dataIndex: 'status', key: 'status', render: (status: string) => getStatusTag(status) },
  ];

  const activePlan = iepPlans.find(p => p.status === 'active');

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Title level={3} style={{ margin: 0 }}>BEP & İlerleme Yönetimi</Title>
        </div>

        <Card>
          <Space direction="vertical" style={{ width: '100%' }}>
            <Text>Öğrenci Seçin:</Text>
            <Select 
              showSearch
              placeholder="Öğrenci ara..."
              style={{ width: 300 }}
              onChange={(val) => setSelectedStudent(val)}
              optionFilterProp="children"
            >
              {students.map(s => (
                <Option key={s.id} value={s.id}>{s.firstName} {s.lastName}</Option>
              ))}
            </Select>
          </Space>
        </Card>

        {selectedStudent && (
          <Spin spinning={loading}>
            {activePlan ? (
              <Card 
                title={`Aktif BEP Planı - ${activePlan.moduleId || 'Genel'}`} 
                extra={<Button type="primary" onClick={() => message.info('Hedef ekleme özelliği yapım aşamasındadır.')}>Hedef Ekle</Button>}
              >
                <div style={{ marginBottom: 16 }}>
                  <Text strong>Tarih: </Text>
                  <Text>{dayjs(activePlan.startDate).format('DD.MM.YYYY')} - {dayjs(activePlan.endDate).format('DD.MM.YYYY')}</Text>
                </div>
                <Table 
                  dataSource={activePlan.goals || []} 
                  columns={goalColumns} 
                  rowKey="id"
                  pagination={false}
                />
              </Card>
            ) : (
              <Card>
                <div style={{ textAlign: 'center', padding: '40px 0' }}>
                  <Text type="secondary" style={{ display: 'block', marginBottom: 16 }}>Bu öğrenci için aktif BEP planı bulunmamaktadır.</Text>
                  <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalVisible(true)}>
                    Yeni BEP Planı
                  </Button>
                </div>
              </Card>
            )}
          </Spin>
        )}
      </Space>

      <Modal
        title="Yeni BEP Planı Oluştur"
        open={isModalVisible}
        onCancel={() => setIsModalVisible(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} layout="vertical" onFinish={handleCreateIep}>
          <Form.Item name="moduleId" label="Modül ID" rules={[{ required: true, message: 'Lütfen modül seçin' }]}>
            <Input placeholder="Örn: mod_001" />
          </Form.Item>
          <Form.Item name="dates" label="Geçerlilik Tarihi" rules={[{ required: true, message: 'Tarih aralığı seçin' }]}>
            <DatePicker.RangePicker style={{ width: '100%' }} />
          </Form.Item>
          <Form.Item name="notes" label="Notlar">
            <TextArea rows={4} />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default IepPage;
