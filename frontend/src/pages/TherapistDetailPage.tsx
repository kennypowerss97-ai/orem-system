import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Tabs, Descriptions, Table, Tag, Button, Spin, Typography, Card, Space, Row, Col, Progress, Statistic } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import { getTherapist, getTherapistSchedule, getTherapistWorkload } from '../api/therapists';
import { DEFAULT_MODULES } from '../api/modules';


dayjs.locale('tr');
const { Title } = Typography;

export const TherapistDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [loading, setLoading] = useState<boolean>(true);
  const [therapist, setTherapist] = useState<any>(null);
  const [schedule, setSchedule] = useState<any[]>([]);
  const [workload, setWorkload] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const [therapistData, scheduleData, workloadData] = await Promise.all([
          getTherapist(id),
          getTherapistSchedule(id),
          getTherapistWorkload(id)
        ]);
        setTherapist(therapistData);
        setSchedule(scheduleData || []);
        setWorkload(workloadData);
      } catch (error) {
        console.error('Öğretmen verileri alınırken hata oluştu:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}><Spin size="large" /></div>;
  }

  if (!therapist) {
    return <div>Öğretmen bulunamadı.</div>;
  }

  const generalInfoItems = [
    { key: '1', label: 'Ad Soyad', children: `${therapist.firstName} ${therapist.lastName}` },
    { key: '2', label: 'Unvan', children: therapist.title },
    { key: '3', label: 'Telefon', children: therapist.phone },
    { key: '4', label: 'E-posta', children: therapist.email },
    { key: '5', label: 'Branşlar', children: (
      <Space wrap size={[0, 4]}>
        {therapist.specializations?.map((spec: any, idx: number) => {
          const mod = DEFAULT_MODULES.find(m => String(m.id) === String(spec.moduleId));
          return (
            <Tag color={mod?.color || "cyan"} key={idx}>
              {mod ? mod.name : `Branş ${spec.moduleId}`}
            </Tag>
          );
        })}
      </Space>
    )}
  ];

  const availabilityColumns = [
    { title: 'Gün', dataIndex: 'dayOfWeek', key: 'dayOfWeek', render: (day: number) => {
      const days = ['Pazar', 'Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi'];
      return days[day];
    }},
    { title: 'Başlangıç', dataIndex: 'startTime', key: 'startTime' },
    { title: 'Bitiş', dataIndex: 'endTime', key: 'endTime' },
  ];

  const scheduleColumns = [
    { title: 'Tarih', dataIndex: 'date', key: 'date', render: (text: string) => dayjs(text).format('DD.MM.YYYY dddd') },
    { title: 'Saat', dataIndex: 'time', key: 'time' },
    { title: 'Modül', dataIndex: 'moduleName', key: 'moduleName' },
    { title: 'Oda', dataIndex: 'room', key: 'room' },
    { title: 'Durum', dataIndex: 'status', key: 'status', render: (status: string) => (
      <Tag color={status === 'scheduled' ? 'blue' : status === 'completed' ? 'green' : 'red'}>
        {status === 'scheduled' ? 'Planlandı' : status === 'completed' ? 'Tamamlandı' : 'İptal'}
      </Tag>
    )},
  ];

  const workloadPercentage = workload ? Math.round((workload.currentWorkload / workload.weeklyHours) * 100) : 0;

  return (
    <div style={{ padding: '24px' }}>
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Row align="middle" justify="space-between">
          <Col>
            <Space align="center">
              <Button icon={<ArrowLeftOutlined />} onClick={() => navigate('/therapists')} />
              <Title level={3} style={{ margin: 0 }}>{therapist.firstName} {therapist.lastName}</Title>
            </Space>
          </Col>
        </Row>

        <Tabs defaultActiveKey="1">
          <Tabs.TabPane tab="Genel Bilgiler" key="1">
            <Card title="Öğretmen Bilgileri">
              <Descriptions items={generalInfoItems} column={1} bordered />
            </Card>
          </Tabs.TabPane>
          <Tabs.TabPane tab="Müsaitlik" key="2">
            <Table 
              dataSource={therapist.availabilities || []} 
              columns={availabilityColumns} 
              rowKey={(record: any) => `${record.dayOfWeek}-${record.startTime}`}
              pagination={false}
            />
          </Tabs.TabPane>
          <Tabs.TabPane tab="Ders Programı" key="3">
            <Table 
              dataSource={schedule} 
              columns={scheduleColumns} 
              rowKey="id"
            />
          </Tabs.TabPane>
          <Tabs.TabPane tab="İş Yükü" key="4">
            <Card title="Haftalık İş Yükü Özeti">
              <Row gutter={24} align="middle">
                <Col span={8}>
                  <Statistic title="Planlanan Saat" value={workload?.currentWorkload || 0} suffix={`/ ${workload?.weeklyHours || 40} saat`} />
                </Col>
                <Col span={16}>
                  <div style={{ textAlign: 'center' }}>
                    <Progress type="dashboard" percent={workloadPercentage} status={workloadPercentage > 90 ? 'exception' : 'normal'} />
                    <div style={{ marginTop: 8 }}>Doluluk Oranı</div>
                  </div>
                </Col>
              </Row>
            </Card>
          </Tabs.TabPane>
        </Tabs>
      </Space>
    </div>
  );
};

export default TherapistDetailPage;
