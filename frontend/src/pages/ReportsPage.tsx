import React, { useEffect, useState } from 'react';
import { Tabs, Card, Select, Spin, Row, Col, Statistic, Typography, Table, Progress, Space } from 'antd';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getStudentProgress, getMonthlyAttendance, getTherapistWorkload, getCapacity } from '../api/reports';
import { getStudents } from '../api/students';

const { Title } = Typography;
const { Option } = Select;

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

export const ReportsPage: React.FC = () => {
  const [students, setStudents] = useState<any[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<string | null>(null);
  
  // Data states
  const [studentProgress, setStudentProgress] = useState<any>(null);
  const [attendance, setAttendance] = useState<any>(null);
  const [therapistWorkload, setTherapistWorkload] = useState<any[]>([]);
  const [capacity, setCapacity] = useState<any>(null);
  
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    // Initial fetch for non-student specific reports
    const fetchReports = async () => {
      setLoading(true);
      try {
        const [studentsData, attendanceData, workloadData, capacityData] = await Promise.all([
          getStudents(),
          getMonthlyAttendance(),
          getTherapistWorkload(),
          getCapacity()
        ]);
        setStudents(Array.isArray(studentsData) ? studentsData : (studentsData.data || studentsData.items || []));
        setAttendance(attendanceData);
        setTherapistWorkload(workloadData || []);
        setCapacity(capacityData);
      } catch (error) {
        console.error('Rapor verileri alınırken hata:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  useEffect(() => {
    if (selectedStudent) {
      const fetchStudentData = async () => {
        try {
          const progress = await getStudentProgress(selectedStudent);
          setStudentProgress(progress);
        } catch (error) {
          console.error('Öğrenci ilerleme verisi alınırken hata:', error);
        }
      };
      fetchStudentData();
    }
  }, [selectedStudent]);

  const renderStudentProgress = () => (
    <div style={{ padding: '16px 0' }}>
      <Select 
        showSearch
        placeholder="Öğrenci seçin..."
        style={{ width: 300, marginBottom: 24 }}
        onChange={(val) => setSelectedStudent(val)}
        optionFilterProp="children"
      >
        {students.map(s => (
          <Option key={s.id} value={s.id}>{s.firstName} {s.lastName}</Option>
        ))}
      </Select>

      {selectedStudent && studentProgress ? (
        <Row gutter={[24, 24]}>
          <Col span={24} md={8}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              <Card>
                <Statistic title="Genel Skor" value={studentProgress.overallScore} suffix="/ 100" />
              </Card>
              <Card>
                <Statistic title="Kazanılan Hedefler" value={studentProgress.milestonesAchieved} suffix={`/ ${studentProgress.milestonesTotal}`} />
                <Progress percent={Math.round((studentProgress.milestonesAchieved / studentProgress.milestonesTotal) * 100)} status="active" />
              </Card>
            </Space>
          </Col>
          <Col span={24} md={16}>
            <Card title="Aylık Gelişim">
              <div style={{ height: 300 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={studentProgress.monthlyData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="skor" stroke="#8884d8" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </Card>
          </Col>
        </Row>
      ) : (
        <div>Raporu görüntülemek için öğrenci seçin.</div>
      )}
    </div>
  );

  const renderAttendance = () => {
    if (!attendance) return <Spin />;
    const pieData = [
      { name: 'Gerçekleşen', value: attendance.totalConducted },
      { name: 'Devamsızlık', value: attendance.totalAbsent },
      { name: 'Telafi', value: attendance.totalMakeups },
    ];
    return (
      <Row gutter={[24, 24]}>
        <Col span={24} md={12}>
          <Row gutter={[16, 16]}>
            <Col span={12}><Card><Statistic title="Katılım Oranı" value={attendance.attendanceRate} suffix="%" /></Card></Col>
            <Col span={12}><Card><Statistic title="Gerçekleşen" value={attendance.totalConducted} /></Card></Col>
            <Col span={12}><Card><Statistic title="Devamsızlık" value={attendance.totalAbsent} /></Card></Col>
            <Col span={12}><Card><Statistic title="Telafi" value={attendance.totalMakeups} /></Card></Col>
          </Row>
        </Col>
        <Col span={24} md={12}>
          <Card title="Dağılım">
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={pieData} cx="50%" cy="50%" outerRadius={100} fill="#8884d8" dataKey="value" label>
                    {pieData.map((entry, index) => <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />)}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
      </Row>
    );
  };

  const renderWorkload = () => {
    const columns = [
      { title: 'Öğretmen', dataIndex: 'therapist', key: 'therapist' },
      { title: 'Saat', dataIndex: 'hours', key: 'hours' },
      { title: 'Maksimum', dataIndex: 'max', key: 'max' },
    ];

    return (
      <Row gutter={[24, 24]}>
        <Col span={24} md={16}>
          <Card title="Öğretmen İş Yükü (Saat)">
            <div style={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={therapistWorkload}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="therapist" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="hours" name="Mevcut Saat" fill="#8884d8" />
                  <Bar dataKey="max" name="Maksimum Saat" fill="#82ca9d" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>
        </Col>
        <Col span={24} md={8}>
          <Table dataSource={therapistWorkload} columns={columns} rowKey="therapist" pagination={false} />
        </Col>
      </Row>
    );
  };

  const renderCapacity = () => {
    if (!capacity) return <Spin />;
    return (
      <Row gutter={[24, 24]}>
        <Col span={24} md={8}>
          <Card style={{ textAlign: 'center' }}>
            <Statistic title="Genel Doluluk" value={capacity.overallUtilization} suffix="%" />
            <Progress type="dashboard" percent={capacity.overallUtilization} />
          </Card>
        </Col>
        <Col span={24} md={16}>
          <Card title="Oda Bazlı Doluluk">
            {capacity.rooms?.map((room: any, idx: number) => (
              <div key={idx} style={{ marginBottom: 16 }}>
                <Typography.Text>{room.room}</Typography.Text>
                <Progress percent={room.rate} status={room.rate > 90 ? 'exception' : 'active'} />
              </div>
            ))}
          </Card>
        </Col>
      </Row>
    );
  };

  return (
    <div style={{ padding: '24px' }}>
      <Title level={3} style={{ marginBottom: 24 }}>Sistem Raporları</Title>
      <Tabs defaultActiveKey="1">
        <Tabs.TabPane tab="Öğrenci İlerleme" key="1">
          {renderStudentProgress()}
        </Tabs.TabPane>
        <Tabs.TabPane tab="Aylık Devamsızlık" key="2">
          {renderAttendance()}
        </Tabs.TabPane>
        <Tabs.TabPane tab="Öğretmen İş Yükü" key="3">
          {renderWorkload()}
        </Tabs.TabPane>
        <Tabs.TabPane tab="Oda Doluluk" key="4">
          {renderCapacity()}
        </Tabs.TabPane>
      </Tabs>
    </div>
  );
};

export default ReportsPage;
