import React, { useState, useEffect } from 'react';
import { Table, Button, Space, Tag, Modal, Popconfirm, message, DatePicker, Select } from 'antd';
import { CheckCircleOutlined, CloseCircleOutlined, StopOutlined } from '@ant-design/icons';
import dayjs from 'dayjs';
import 'dayjs/locale/tr';
import { getSessions, markAttendance, cancelSession } from '../api/sessions';
import { getTherapists } from '../api/therapists';

dayjs.locale('tr');

const { Option } = Select;

interface Participant {
  studentId: string;
  studentName: string;
  attendanceStatus: string;
}

interface Session {
  id: string;
  moduleName: string;
  therapistName: string;
  roomName: string;
  date: string;
  startTime: string;
  endTime: string;
  status: string;
  participants: Participant[];
}

interface Therapist {
  id: string;
  firstName: string;
  lastName: string;
}

const SessionsPage: React.FC = () => {
  const [data, setData] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const [therapists, setTherapists] = useState<Therapist[]>([]);
  
  const [filterDate, setFilterDate] = useState<dayjs.Dayjs | null>(null);
  const [filterTherapist, setFilterTherapist] = useState<string | undefined>(undefined);
  const [filterStatus, setFilterStatus] = useState<string | undefined>(undefined);

  const [attendanceModalVisible, setAttendanceModalVisible] = useState(false);
  const [selectedSession, setSelectedSession] = useState<Session | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchSessions();
  }, [filterDate, filterTherapist, filterStatus]);

  useEffect(() => {
    fetchTherapists();
  }, []);

  const fetchSessions = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (filterDate) params.date = filterDate.format('YYYY-MM-DD');
      if (filterTherapist) params.therapistId = filterTherapist;
      if (filterStatus) params.status = filterStatus;
      
      const response = await getSessions(params);
      setData(response.data);
      setTotal(response.total);
    } catch (error) {
      message.error('Seanslar yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const fetchTherapists = async () => {
    try {
      const response = await getTherapists();
      setTherapists(response.data);
    } catch (error) {
      console.error('Öğretmenler yüklenemedi', error);
    }
  };

  const showAttendanceModal = (record: Session) => {
    setSelectedSession(record);
    setAttendanceModalVisible(true);
  };

  const handleAttendance = async (status: string) => {
    if (!selectedSession || selectedSession.participants.length === 0) return;
    
    setSubmitting(true);
    try {
      const studentId = selectedSession.participants[0].studentId;
      await markAttendance(selectedSession.id, { 
        attended: status === 'present',
        absence_reason: status === 'absent' ? 'Mazeretsiz' : 'Mazeretli'
      });
      message.success('Yoklama kaydedildi.');
      setAttendanceModalVisible(false);
      fetchSessions();
    } catch (error) {
      message.error('Yoklama kaydedilirken bir hata oluştu.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCancelSession = async (id: string) => {
    try {
      await cancelSession(id, 'İptal edildi');
      message.success('Seans iptal edildi.');
      fetchSessions();
    } catch (error) {
      message.error('Seans iptal edilirken bir hata oluştu.');
    }
  };

  const getStatusTag = (status: string) => {
    switch (status) {
      case 'Planlandı': return <Tag color="blue">Planlandı</Tag>;
      case 'Tamamlandı': return <Tag color="green">Tamamlandı</Tag>;
      case 'Devamsız': return <Tag color="red">Devamsız</Tag>;
      case 'İptal': return <Tag color="default">İptal</Tag>;
      default: return <Tag>{status}</Tag>;
    }
  };

  const columns = [
    {
      title: 'Tarih',
      dataIndex: 'date',
      key: 'date',
      render: (text: string) => dayjs(text).format('DD.MM.YYYY'),
    },
    {
      title: 'Saat',
      key: 'time',
      render: (text: string, record: Session) => `${record.startTime} - ${record.endTime}`,
    },
    {
      title: 'Öğrenci',
      key: 'student',
      render: (text: string, record: Session) => record.participants.map(p => p.studentName).join(', '),
    },
    {
      title: 'Öğretmen',
      dataIndex: 'therapistName',
      key: 'therapistName',
    },
    {
      title: 'Modül',
      dataIndex: 'moduleName',
      key: 'moduleName',
    },
    {
      title: 'Oda',
      dataIndex: 'roomName',
      key: 'roomName',
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => getStatusTag(status),
    },
    {
      title: 'İşlem',
      key: 'action',
      render: (text: string, record: Session) => (
        <Space size="middle">
          {record.status === 'Planlandı' && (
            <>
              <Button 
                type="primary" 
                size="small" 
                onClick={() => showAttendanceModal(record)}
              >
                Yoklama
              </Button>
              <Popconfirm
                title="Seansı iptal etmek istediğinize emin misiniz?"
                onConfirm={() => handleCancelSession(record.id)}
                okText="Evet"
                cancelText="Hayır"
              >
                <Button danger size="small" icon={<StopOutlined />}>İptal</Button>
              </Popconfirm>
            </>
          )}
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16, flexWrap: 'wrap', gap: 12 }}>
        <h2 style={{ margin: 0, fontSize: '1.4rem' }}>Seanslar</h2>
        <Space wrap style={{ flex: 1, justifyContent: 'flex-end' }}>
          <DatePicker 
            placeholder="Tarih seçin" 
            value={filterDate}
            onChange={setFilterDate}
            format="DD.MM.YYYY"
            style={{ minWidth: 140 }}
          />
          <Select
            placeholder="Öğretmen Filtresi"
            style={{ minWidth: 160 }}
            allowClear
            value={filterTherapist}
            onChange={setFilterTherapist}
          >
            {therapists.map(t => (
              <Option key={t.id} value={t.id}>{`${t.firstName} ${t.lastName}`}</Option>
            ))}
          </Select>
          <Select
            placeholder="Durum Filtresi"
            style={{ minWidth: 130 }}
            allowClear
            value={filterStatus}
            onChange={setFilterStatus}
          >
            <Option value="Planlandı">Planlandı</Option>
            <Option value="Tamamlandı">Tamamlandı</Option>
            <Option value="Devamsız">Devamsız</Option>
            <Option value="İptal">İptal</Option>
          </Select>
        </Space>
      </div>

      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="id" 
        loading={loading}
        pagination={{ total, showSizeChanger: true }}
        scroll={{ x: 800 }}
      />

      <Modal
        title="Yoklama"
        open={attendanceModalVisible}
        onCancel={() => setAttendanceModalVisible(false)}
        footer={null}
        width="95%"
        style={{ maxWidth: 480 }}
      >
        <div style={{ textAlign: 'center', padding: '20px 0' }}>
          <h3>Öğrenci geldi mi?</h3>
          <p>{selectedSession?.participants.map(p => p.studentName).join(', ')}</p>
          <Space size="large" style={{ marginTop: 20 }}>
            <Button 
              type="primary" 
              icon={<CheckCircleOutlined />} 
              size="large"
              loading={submitting}
              onClick={() => handleAttendance('Geldi')}
            >
              Geldi
            </Button>
            <Button 
              danger 
              type="primary" 
              icon={<CloseCircleOutlined />} 
              size="large"
              loading={submitting}
              onClick={() => handleAttendance('Gelmedi')}
            >
              Gelmedi
            </Button>
          </Space>
        </div>
      </Modal>
    </div>
  );
};

export default SessionsPage;
