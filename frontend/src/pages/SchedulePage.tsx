import React, { useState, useEffect, useRef } from 'react';
import { Button, Select, Space, Card, Modal, Descriptions, Tag, message, Spin, Grid, Segmented, Row, Col, Form, DatePicker, TimePicker, Popconfirm, Tooltip } from 'antd';
import { ReloadOutlined, ThunderboltOutlined, EditOutlined, DeleteOutlined, CheckCircleOutlined, CloseCircleOutlined, CalendarOutlined } from '@ant-design/icons';
import FullCalendar from '@fullcalendar/react';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import trLocale from '@fullcalendar/core/locales/tr';
import dayjs from 'dayjs';
import { getWeeklySchedule, generateSchedule, moveSession } from '../api/schedule';
import { getTherapists } from '../api/therapists';
import { getRooms } from '../api/rooms';
import { getModules } from '../api/modules';
import { updateSession, deleteSession } from '../api/sessions';

const { useBreakpoint } = Grid;

const SchedulePage: React.FC = () => {
  const screens = useBreakpoint();
  const isMobile = screens.md === false;
  const calendarRef = useRef<FullCalendar>(null);

  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [savingSession, setSavingSession] = useState(false);

  const [therapists, setTherapists] = useState<any[]>([]);
  const [rooms, setRooms] = useState<any[]>([]);
  const [modules, setModules] = useState<any[]>([]);

  const [selectedTherapist, setSelectedTherapist] = useState<string | undefined>(undefined);
  const [selectedRoom, setSelectedRoom] = useState<number | undefined>(undefined);
  
  // Seans Detay & Düzenleme Modalı
  const [selectedEvent, setSelectedEvent] = useState<any | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm] = Form.useForm();

  const [calendarView, setCalendarView] = useState<string>(isMobile ? 'timeGridDay' : 'timeGridWeek');

  useEffect(() => {
    if (isMobile) {
      setCalendarView('timeGridDay');
      calendarRef.current?.getApi().changeView('timeGridDay');
    }
  }, [isMobile]);

  const fetchFilters = async () => {
    try {
      const [tRes, rRes, mRes] = await Promise.all([getTherapists(), getRooms(), getModules()]);
      setTherapists(tRes.data || []);
      setRooms(Array.isArray(rRes) ? rRes : (rRes as any)?.data || []);
      setModules(Array.isArray(mRes) ? mRes : (mRes as any)?.data || []);
    } catch (e) {
      console.error(e);
    }
  };

  const fetchSchedule = async () => {
    setLoading(true);
    try {
      const params: any = {};
      if (selectedTherapist) params.therapist_id = selectedTherapist;
      if (selectedRoom) params.room_id = selectedRoom;
      const res = await getWeeklySchedule(params);
      setEvents(res || []);
    } catch (err) {
      message.error('Ders programı yüklenirken hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFilters();
  }, []);

  useEffect(() => {
    fetchSchedule();
  }, [selectedTherapist, selectedRoom]);

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const res = await generateSchedule('', '');
      message.success(res.message || 'Otomatik ders programı başarıyla oluşturuldu!');
      await fetchSchedule();
    } catch (e) {
      message.error('Program oluşturulurken hata meydana geldi.');
    } finally {
      setGenerating(false);
    }
  };

  const handleEventClick = (info: any) => {
    const props = info.event.extendedProps;
    const evData = {
      id: info.event.id,
      title: info.event.title,
      start: info.event.startStr,
      end: info.event.endStr,
      date: props?.date || (info.event.startStr ? info.event.startStr.split('T')[0] : ''),
      startTime: props?.startTime || (info.event.start ? dayjs(info.event.start).format('HH:mm') : '09:00'),
      endTime: props?.endTime || (info.event.end ? dayjs(info.event.end).format('HH:mm') : '09:45'),
      studentName: props?.studentName,
      studentId: props?.studentId,
      therapistName: props?.therapistName,
      therapistId: props?.therapistId,
      roomName: props?.roomName,
      roomId: props?.roomId,
      moduleName: props?.moduleName,
      moduleId: props?.moduleId,
      status: props?.status || 'planned'
    };
    setSelectedEvent(evData);
    setIsEditing(false);
  };

  // Sürükle - Bırak ile Seans Taşıma
  const handleEventDrop = async (info: any) => {
    try {
      await moveSession(info.event.id, {
        start: info.event.startStr,
        end: info.event.endStr
      });
      message.success('Seans yeni gün/saate başarıyla taşındı! 📅');
      fetchSchedule();
    } catch (e) {
      message.error('Seans taşınırken hata oluştu.');
      info.revert();
    }
  };

  const handleStartEdit = () => {
    if (!selectedEvent) return;
    setIsEditing(true);
    editForm.setFieldsValue({
      date: selectedEvent.date ? dayjs(selectedEvent.date) : dayjs(),
      startTime: selectedEvent.startTime ? dayjs(selectedEvent.startTime, 'HH:mm') : dayjs('09:00', 'HH:mm'),
      endTime: selectedEvent.endTime ? dayjs(selectedEvent.endTime, 'HH:mm') : dayjs('09:45', 'HH:mm'),
      therapistId: selectedEvent.therapistId,
      roomId: selectedEvent.roomId ? Number(selectedEvent.roomId) : undefined,
      moduleId: selectedEvent.moduleId ? Number(selectedEvent.moduleId) : undefined,
      status: selectedEvent.status || 'scheduled'
    });
  };

  const handleSaveEdit = async () => {
    if (!selectedEvent) return;
    try {
      const values = await editForm.validateFields();
      setSavingSession(true);

      const payload = {
        date: values.date.format('YYYY-MM-DD'),
        startTime: values.startTime.format('HH:mm'),
        endTime: values.endTime.format('HH:mm'),
        therapistId: values.therapistId,
        roomId: values.roomId,
        moduleId: values.moduleId,
        status: values.status
      };

      await updateSession(selectedEvent.id, payload);
      message.success('Seans başarıyla güncellendi! 🎉');
      setSelectedEvent(null);
      setIsEditing(false);
      fetchSchedule();
    } catch (e) {
      message.error('Seans güncellenirken hata oluştu.');
    } finally {
      setSavingSession(false);
    }
  };

  const handleDeleteSession = async () => {
    if (!selectedEvent) return;
    try {
      await deleteSession(selectedEvent.id);
      message.success('Seans programdan kaldırıldı.');
      setSelectedEvent(null);
      setIsEditing(false);
      fetchSchedule();
    } catch (e) {
      message.error('Seans silinirken hata oluştu.');
    }
  };

  const handleQuickStatus = async (status: string) => {
    if (!selectedEvent) return;
    try {
      await updateSession(selectedEvent.id, { status });
      message.success(`Seans durumu "${status.toUpperCase()}" olarak kaydedildi.`);
      setSelectedEvent(null);
      fetchSchedule();
    } catch (e) {
      message.error('Durum güncellenirken hata oluştu.');
    }
  };

  const handleViewChange = (view: string) => {
    setCalendarView(view);
    calendarRef.current?.getApi().changeView(view);
  };

  return (
    <div>
      {/* Üst Başlık ve Aksiyonlar */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 12, marginBottom: 12 }}>
          <div>
            <h2 style={{ margin: 0, fontSize: isMobile ? '1.25rem' : '1.4rem' }}>Haftalık Ders ve Terapi Programı</h2>
            <span style={{ color: '#888', fontSize: isMobile ? '12px' : '14px' }}>
              MEB Mevzuatına Uygun Otomatik & Manuel Ders Programı Yönetimi
            </span>
          </div>
          
          <Space wrap>
            <Button icon={<ReloadOutlined />} onClick={fetchSchedule}>
              Yenile
            </Button>
            <Button
              type="primary"
              icon={<ThunderboltOutlined />}
              loading={generating}
              onClick={handleGenerate}
              style={{ backgroundColor: '#52c41a', borderColor: '#52c41a' }}
            >
              {isMobile ? 'Yapay Zeka Dağıt' : 'Otomatik Program Oluştur (Yapay Zeka)'}
            </Button>
          </Space>
        </div>

        {/* Filtre ve Görünüm Seçici Çubuğu */}
        <Row gutter={[8, 8]} align="middle">
          <Col xs={24} sm={12} md={7}>
            <Select
              allowClear
              placeholder="Öğretmen Filtrele"
              style={{ width: '100%' }}
              value={selectedTherapist}
              onChange={setSelectedTherapist}
              options={therapists.map(t => ({ value: t.id, label: `${t.firstName} ${t.lastName}` }))}
            />
          </Col>
          <Col xs={24} sm={12} md={7}>
            <Select
              allowClear
              placeholder="Oda Filtrele"
              style={{ width: '100%' }}
              value={selectedRoom}
              onChange={setSelectedRoom}
              options={rooms.map(r => ({ value: Number(r.id), label: r.name }))}
            />
          </Col>
          <Col xs={24} md={10} style={{ display: 'flex', justifyContent: isMobile ? 'stretch' : 'flex-end' }}>
            <Segmented
              style={{ width: isMobile ? '100%' : 'auto', textAlign: 'center' }}
              value={calendarView}
              onChange={(val) => handleViewChange(String(val))}
              options={[
                { label: 'Günlük', value: 'timeGridDay' },
                { label: isMobile ? '3 Gün' : 'Haftalık', value: isMobile ? 'timeGridThreeDay' : 'timeGridWeek' },
                { label: 'Aylık', value: 'dayGridMonth' },
              ]}
            />
          </Col>
        </Row>
      </div>

      <Card styles={{ body: { padding: isMobile ? 8 : 16 } }}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '80px 0' }}>
            <Spin size="large" tip="Ders programı yükleniyor..." />
          </div>
        ) : (
          <div style={{ height: isMobile ? '70vh' : '76vh' }}>
            <FullCalendar
              ref={calendarRef}
              plugins={[dayGridPlugin, timeGridPlugin, interactionPlugin]}
              initialView={isMobile ? 'timeGridDay' : 'timeGridWeek'}
              views={{
                timeGridThreeDay: {
                  type: 'timeGrid',
                  duration: { days: 3 },
                  buttonText: '3 Gün'
                }
              }}
              locales={[trLocale]}
              locale="tr"
              firstDay={1}
              slotMinTime="08:30:00"
              slotMaxTime="18:30:00"
              slotDuration="00:15:00"
              slotLabelInterval="01:00:00"
              businessHours={{ daysOfWeek: [1, 2, 3, 4, 5], startTime: '09:00', endTime: '17:00' }}
              events={events}
              eventClick={handleEventClick}
              editable={true}
              eventDrop={handleEventDrop}
              headerToolbar={{
                left: isMobile ? 'prev,next' : 'prev,next today',
                center: 'title',
                right: isMobile ? 'today' : 'timeGridWeek,timeGridDay'
              }}
              allDaySlot={false}
              height="100%"
              nowIndicator={true}
              eventTimeFormat={{
                hour: '2-digit',
                minute: '2-digit',
                meridiem: false,
                hour12: false
              }}
            />
          </div>
        )}
      </Card>

      {/* Seans Detayı ve Düzenleme Modalı */}
      <Modal
        title={isEditing ? "Seansı Düzenle" : "Seans Detayı ve Yönetimi"}
        open={!!selectedEvent}
        onCancel={() => { setSelectedEvent(null); setIsEditing(false); }}
        width="95%"
        style={{ maxWidth: 540 }}
        footer={null}
        destroyOnClose={true}
      >
        {selectedEvent && !isEditing && (
          <div>
            <Descriptions bordered column={1} size="small" style={{ marginBottom: 16 }}>
              <Descriptions.Item label="Öğrenci">
                <strong>{selectedEvent.studentName}</strong>
              </Descriptions.Item>
              <Descriptions.Item label="Eğitim / Modül">
                {selectedEvent.moduleName}
              </Descriptions.Item>
              <Descriptions.Item label="Öğretmen / Terapist">
                {selectedEvent.therapistName}
              </Descriptions.Item>
              <Descriptions.Item label="Oda / Salon">
                {selectedEvent.roomName}
              </Descriptions.Item>
              <Descriptions.Item label="Tarih & Saat">
                {dayjs(selectedEvent.date).format('DD MMMM YYYY dddd')} ({selectedEvent.startTime} - {selectedEvent.endTime})
              </Descriptions.Item>
              <Descriptions.Item label="Durum">
                <Tag color={
                  selectedEvent.status === 'completed' ? 'green' :
                  selectedEvent.status === 'student_absent' ? 'red' :
                  selectedEvent.status === 'cancelled' ? 'default' : 'blue'
                }>
                  {selectedEvent.status ? selectedEvent.status.toUpperCase() : 'PLANLANDI'}
                </Tag>
              </Descriptions.Item>
            </Descriptions>

            <div style={{ backgroundColor: '#f0f5ff', padding: 10, borderRadius: 6, marginBottom: 16, fontSize: '13px' }}>
              💡 <strong>İpucu:</strong> Seansları takvim üzerinde sürükleyip bırakarak başka gün ve saatlere anında taşıyabilirsiniz.
            </div>

            <Row gutter={[8, 8]} justify="end">
              <Col>
                <Button icon={<CheckCircleOutlined />} onClick={() => handleQuickStatus('completed')}>
                  Tamamlandı
                </Button>
              </Col>
              <Col>
                <Button danger icon={<CloseCircleOutlined />} onClick={() => handleQuickStatus('student_absent')}>
                  Devamsız
                </Button>
              </Col>
              <Col>
                <Button type="primary" icon={<EditOutlined />} onClick={handleStartEdit}>
                  Düzenle
                </Button>
              </Col>
              <Col>
                <Popconfirm
                  title="Bu seansı ders programından silmek istediğinize emin misiniz?"
                  onConfirm={handleDeleteSession}
                  okText="Evet, Sil"
                  cancelText="Vazgeç"
                >
                  <Button danger icon={<DeleteOutlined />}>
                    Sil
                  </Button>
                </Popconfirm>
              </Col>
            </Row>
          </div>
        )}

        {selectedEvent && isEditing && (
          <Form form={editForm} layout="vertical" onFinish={handleSaveEdit}>
            <Row gutter={[12, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="date" label="Tarih" rules={[{ required: true, message: 'Tarih seçiniz' }]}>
                  <DatePicker style={{ width: '100%' }} format="DD.MM.YYYY" />
                </Form.Item>
              </Col>
              <Col xs={12} sm={6}>
                <Form.Item name="startTime" label="Başlangıç" rules={[{ required: true, message: 'Saat seçiniz' }]}>
                  <TimePicker format="HH:mm" minuteStep={15} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
              <Col xs={12} sm={6}>
                <Form.Item name="endTime" label="Bitiş" rules={[{ required: true, message: 'Saat seçiniz' }]}>
                  <TimePicker format="HH:mm" minuteStep={15} style={{ width: '100%' }} />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={[12, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="therapistId" label="Öğretmen / Terapist" rules={[{ required: true, message: 'Öğretmen seçiniz' }]}>
                  <Select
                    placeholder="Öğretmen seçiniz"
                    options={therapists.map(t => ({ value: t.id, label: `${t.firstName} ${t.lastName}` }))}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="roomId" label="Oda / Salon" rules={[{ required: true, message: 'Oda seçiniz' }]}>
                  <Select
                    placeholder="Oda seçiniz"
                    options={rooms.map(r => ({ value: Number(r.id), label: r.name }))}
                  />
                </Form.Item>
              </Col>
            </Row>

            <Row gutter={[12, 12]}>
              <Col xs={24} sm={12}>
                <Form.Item name="moduleId" label="Eğitim Modülü" rules={[{ required: true, message: 'Modül seçiniz' }]}>
                  <Select
                    placeholder="Modül seçiniz"
                    options={modules.map(m => ({ value: Number(m.id), label: m.name }))}
                  />
                </Form.Item>
              </Col>
              <Col xs={24} sm={12}>
                <Form.Item name="status" label="Seans Durumu">
                  <Select
                    options={[
                      { value: 'scheduled', label: 'Planlandı' },
                      { value: 'completed', label: 'Tamamlandı' },
                      { value: 'student_absent', label: 'Öğrenci Devamsız' },
                      { value: 'cancelled', label: 'İptal Edildi' }
                    ]}
                  />
                </Form.Item>
              </Col>
            </Row>

            <div style={{ textAlign: 'right', marginTop: 16 }}>
              <Space>
                <Button onClick={() => setIsEditing(false)}>Vazgeç</Button>
                <Button type="primary" htmlType="submit" loading={savingSession}>
                  Değişiklikleri Kaydet
                </Button>
              </Space>
            </div>
          </Form>
        )}
      </Modal>
    </div>
  );
};

export default SchedulePage;
