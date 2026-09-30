import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Tabs, Descriptions, Table, Tag, Button, Spin, Typography, Card, Space, Row, Col } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import { getStudent, getStudentSchedule } from '../api/students';
import { getIepPlans } from '../api/iep';
import { getSessions } from '../api/sessions';

dayjs.locale('tr');
const { Title } = Typography;

export const StudentDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState<boolean>(true);
  const [student, setStudent] = useState<any>(null);
  const [schedule, setSchedule] = useState<any[]>([]);
  const [iepPlans, setIepPlans] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const [studentData, scheduleData, iepData, sessionsData] = await Promise.all([
          getStudent(id),
          getStudentSchedule(id),
          getIepPlans(id),
          getSessions({ student_id: id })
        ]);
        setStudent(studentData);
        setSchedule(scheduleData || []);
        setIepPlans(iepData || []);
        setSessions(sessionsData?.data || sessionsData || []);
      } catch (error) {
        console.error('Öğrenci verileri alınırken hata oluştu:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

  if (!student) {
    return <div>Öğrenci bulunamadı.</div>;
  }

  const generalInfoItems = [
    { key: '1', label: 'Ad Soyad', children: `${student.firstName} ${student.lastName}` },
    { key: '2', label: 'TC Kimlik', children: student.tcKimlik },
    { key: '3', label: 'Doğum Tarihi', children: dayjs(student.birthDate).format('DD MMMM YYYY') },
    { key: '4', label: 'Cinsiyet', children: student.gender === 'F' ? 'Kız' : 'Erkek' },
    { key: '5', label: 'Engel Türü', children: student.disabilityType },
    { key: '6', label: 'Durum', children: <Tag color={student.status === 'active' ? 'green' : 'red'}>{student.status === 'active' ? 'Aktif' : 'Pasif'}</Tag> },
    { key: '7', label: 'Notlar', children: student.notes || '-' },
  ];

  const guardianItems = student.guardian ? [
    { key: '8', label: 'Veli Ad Soyad', children: student.guardian.name },
    { key: '9', label: 'Telefon', children: student.guardian.phone },
    { key: '10', label: 'E-posta', children: student.guardian.email || '-' },
    { key: '11', label: 'Yakınlık', children: student.guardian.relationship },
  ] : [];

  const ramItems = student.ramReport ? [
    { key: '1', label: 'Rapor No', children: student.ramReport.reportNumber },
    { key: '2', label: 'Düzenleyen RAM', children: student.ramReport.issuingRam },
    { key: '3', label: 'Başlangıç Tarihi', children: dayjs(student.ramReport.issueDate).format('DD MMMM YYYY') },
    { key: '4', label: 'Bitiş Tarihi', children: dayjs(student.ramReport.expiryDate).format('DD MMMM YYYY') },
  ] : [];

  const moduleColumns = [
    { title: 'Modül ID', dataIndex: 'moduleId', key: 'moduleId' },
    { title: 'Kota (Saat)', dataIndex: 'quotaHours', key: 'quotaHours' },
  ];

  const scheduleColumns = [
    { title: 'Gün', dataIndex: 'day', key: 'day', render: (text: string) => dayjs(text).format('dddd') },
    { title: 'Saat', dataIndex: 'time', key: 'time' },
    { title: 'Modül', dataIndex: 'moduleName', key: 'moduleName' },
    { title: 'Durum', dataIndex: 'status', key: 'status', render: (status: string) => (
      <Tag color={status === 'scheduled' ? 'blue' : status === 'completed' ? 'green' : 'red'}>
        {status === 'scheduled' ? 'Planlandı' : status === 'completed' ? 'Tamamlandı' : 'İptal'}
      </Tag>
    )},
  ];

  const sessionColumns = [
    { title: 'Tarih', dataIndex: 'date', key: 'date', render: (text: string) => dayjs(text).format('DD.MM.YYYY') },
    { title: 'Saat', dataIndex: 'time', key: 'time' },
    { title: 'Modül', dataIndex: 'moduleName', key: 'moduleName' },
    { title: 'Durum', dataIndex: 'status', key: 'status', render: (status: string) => (
      <Tag color={status === 'completed' ? 'green' : status === 'missed' ? 'red' : 'default'}>
        {status === 'completed' ? 'Tamamlandı' : status === 'missed' ? 'Devamsız' : status}
      </Tag>
    )},
  ];

  const activeIep = iepPlans.find(plan => plan.status === 'active');
  const mockChartData = [
    { month: 'Oca', score: 65 }, { month: 'Şub', score: 70 }, { month: 'Mar', score: 72 },
    { month: 'Nis', score: 78 }, { month: 'May', score: 85 }
  ];

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space align="center">
              <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/students')} />
              <Title level={3} style={{ margin: 0 }}>{student.firstName} {student.lastName}</Title>
            </Space>
          </Col>
        </Row>

        <Tabs defaultActiveKey="1">
          <Tabs.TabPane tab="Genel Bilgiler" key="1">
            <Card title="Öğrenci Bilgileri" style={{ marginBottom: 16 }}>
              <Descriptions items={generalInfoItems} column={2} bordered />
            </Card>
            {student.guardian && (
              <Card title="Veli Bilgileri">
                <Descriptions items={guardianItems} column={2} bordered />
              </Card>
            )}
          </Tabs.TabPane>
          <Tabs.TabPane tab="RAM Raporu" key="2">
            {student.ramReport ? (
              <Space direction="vertical" style={{ width: '100%' }} size="middle">
                <Descriptions items={ramItems} column={2} bordered title="Rapor Detayları" />
                <Card title="Atanan Modüller" size="small">
                  <Table 
                    dataSource={student.allocatedModules || []} 
                    columns={moduleColumns} 
                    rowKey="moduleId"
                    pagination={false}
                  />
                </Card>
              </Space>
            ) : (
              <div>RAM Raporu bulunmamaktadır.</div>
            )}
          </Tabs.TabPane>
          <Tabs.TabPane tab="Ders Programı" key="3">
            <Table 
              dataSource={schedule} 
              columns={scheduleColumns} 
              rowKey="id"
            />
          </Tabs.TabPane>
          <Tabs.TabPane tab="BEP & İlerleme" key="4">
            {activeIep ? (
              <Space direction="vertical" style={{ width: '100%' }} size="large">
                <Card title="Aktif BEP Hedefleri">
                  {activeIep.goals?.map((goal: any, index: number) => (
                    <div key={index} style={{ marginBottom: 8 }}>
                      <Tag color={goal.status === 'acquired' ? 'success' : goal.status === 'in_progress' ? 'processing' : 'default'}>
                        {goal.status}
                      </Tag>
                      <span style={{ marginLeft: 8 }}>{goal.description}</span>
                    </div>
                  ))}
                </Card>
                <Card title="Gelişim Eğrisi">
                  <div style={{ height: 300 }}>
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={activeIep.progressData || mockChartData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="month" />
                        <YAxis />
                        <Tooltip />
                        <Line type="monotone" dataKey="score" stroke="#1890ff" strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </Card>
              </Space>
            ) : (
              <div>Aktif BEP planı bulunmamaktadır.</div>
            )}
          </Tabs.TabPane>
          <Tabs.TabPane tab="Seans Geçmişi" key="5">
            <Table 
              dataSource={sessions} 
              columns={sessionColumns} 
              rowKey="id"
            />
          </Tabs.TabPane>
        </Tabs>
      </Space>
    </div>
  );
};

export default StudentDetailPage;
