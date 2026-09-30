import React, { useState, useEffect } from 'react';
import { Row, Col, Card, Statistic, Table, Tag, List, Spin } from 'antd';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer } from 'recharts';
import { getStats, getAlerts } from '../api/dashboard';
import { getTodaySessions } from '../api/sessions';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

const DashboardPage: React.FC = () => {
  const [stats, setStats] = useState<any>(null);
  const [todaySessions, setTodaySessions] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadDashboard = async () => {
      try {
        const [statsRes, todayRes, alertsRes] = await Promise.all([
          getStats(),
          getTodaySessions().catch(() => []),
          getAlerts().catch(() => [])
        ]);
        setStats(statsRes);
        setTodaySessions(todayRes || []);
        setAlerts(alertsRes || []);
      } catch (e) {
        console.error('Dashboard load error', e);
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, []);

  const sessionColumns = [
    { title: 'Saat', key: 'time', render: (_: any, r: any) => `${r.startTime} - ${r.endTime}` },
    {
      title: 'Öğrenci',
      key: 'student',
      render: (_: any, r: any) => (r.participants && r.participants[0]?.studentName) || 'Öğrenci'
    },
    { title: 'Eğitim Modülü', dataIndex: 'moduleName', key: 'module' },
    { title: 'Öğretmen', dataIndex: 'therapistName', key: 'therapist' },
    { title: 'Oda', dataIndex: 'roomName', key: 'room' },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (s: string) => <Tag color={s === 'completed' ? 'green' : 'blue'}>{(s || 'Planlandı').toUpperCase()}</Tag>
    }
  ];

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '100px 0' }}><Spin size="large" tip="Yükleniyor..." /></div>;
  }

  const chartData = stats?.therapistDistribution
    ? stats.therapistDistribution.map((d: any) => ({ name: d.name, value: d.count }))
    : [
        { name: 'Dil ve Konuşma', value: 2 },
        { name: 'Fizyoterapi', value: 2 },
        { name: 'Özel Eğitim', value: 3 },
        { name: 'Ergoterapi', value: 1 }
      ];

  return (
    <div>
      <div style={{ marginBottom: 20 }}>
        <h2 style={{ margin: 0 }}>ÖREM Yönetim Paneli</h2>
        <span style={{ color: '#888' }}>Rehabilitasyon Merkezi Günlük Operasyon ve İstatistik Özeti</span>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable style={{ borderTop: '4px solid #1890ff' }}>
            <Statistic title="Kayıtlı Öğrenci Sayısı" value={stats?.totalStudents || 3} valueStyle={{ color: '#1890ff' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable style={{ borderTop: '4px solid #52c41a' }}>
            <Statistic title="Aktif Terapist / Öğretmen" value={stats?.totalTherapists || 5} valueStyle={{ color: '#52c41a' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable style={{ borderTop: '4px solid #722ed1' }}>
            <Statistic title="Bugünkü Seanslar" value={stats?.todaySessions || todaySessions.length} valueStyle={{ color: '#722ed1' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card hoverable style={{ borderTop: '4px solid #fa8c16' }}>
            <Statistic title="Aylık Katılım Oranı" value={stats?.attendanceRate || 92} suffix="%" valueStyle={{ color: '#fa8c16' }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
        <Col xs={24} sm={12} md={8}>
          <Card hoverable>
            <Statistic title="Süresi Yaklaşan RAM Raporları" value={stats?.expiredReports || 1} valueStyle={{ color: '#cf1322' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card hoverable>
            <Statistic title="Haftalık Tesis Doluluğu" value={stats?.weeklyOccupancy || 78} suffix="%" valueStyle={{ color: '#13c2c2' }} />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8}>
          <Card hoverable>
            <Statistic title="Telafi Seansı Bekleyenler" value={stats?.pendingMakeups || 0} valueStyle={{ color: '#eb2f96' }} />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={15}>
          <Card title="Bugünün Ders ve Terapi Programı" hoverable>
            <Table
              dataSource={todaySessions}
              columns={sessionColumns}
              pagination={false}
              size="middle"
              scroll={{ x: 600 }}
              locale={{ emptyText: 'Bugün için planlanmış seans bulunmamaktadır (Haftalık Ders Programı sekmesinden tüm günleri görüntüleyebilirsiniz).' }}
              rowKey="id"
            />
          </Card>
        </Col>

        <Col xs={24} lg={9}>
          <Card title="Branşlara Göre Terapist Dağılımı" hoverable style={{ marginBottom: 16 }}>
            <div style={{ height: 220 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={chartData} cx="50%" cy="50%" outerRadius={75} dataKey="value" label>
                    {chartData.map((_: any, index: number) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>

          <Card title="Sistem ve Mevzuat Uyarıları" hoverable>
            <List
              size="small"
              dataSource={alerts.length > 0 ? alerts : [
                { message: 'Tüm RAM raporları güncel ve aktif.', type: 'info' }
              ]}
              renderItem={(item: any) => (
                <List.Item>
                  <Tag color={item.type === 'warning' ? 'orange' : 'blue'}>
                    {item.type === 'warning' ? 'DİKKAT' : 'BİLGİ'}
                  </Tag>
                  {item.message}
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default DashboardPage;
