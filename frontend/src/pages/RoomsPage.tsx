import React, { useState, useEffect } from 'react';
import { Table, Button, Tag, Modal, Form, Input, InputNumber, Select, message, Space } from 'antd';
import { PlusOutlined } from '@ant-design/icons';
import { getRooms, createRoom } from '../api/rooms';
import { getModules } from '../api/modules';

const { Option } = Select;

interface Module {
  id: string;
  name: string;
}

interface Room {
  id: string;
  name: string;
  code: string;
  capacity: number;
  supportedModules: string[];
  status: string;
}

const RoomsPage: React.FC = () => {
  const [form] = Form.useForm();
  
  const [data, setData] = useState<Room[]>([]);
  const [loading, setLoading] = useState(false);
  
  const [isModalVisible, setIsModalVisible] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [modules, setModules] = useState<Module[]>([]);

  useEffect(() => {
    fetchRooms();
    fetchModules();
  }, []);

  const fetchRooms = async () => {
    setLoading(true);
    try {
      const response = await getRooms();
      setData(Array.isArray(response) ? response : (response as any)?.data || []);
    } catch (error) {
      message.error('Odalar yüklenirken bir hata oluştu.');
    } finally {
      setLoading(false);
    }
  };

  const fetchModules = async () => {
    try {
      const response = await getModules();
      setModules(Array.isArray(response) ? response : (response as any)?.data || []);
    } catch (error) {
      console.error('Modüller yüklenemedi', error);
    }
  };

  const showModal = () => {
    setIsModalVisible(true);
  };

  const handleCancel = () => {
    setIsModalVisible(false);
    form.resetFields();
  };

  const handleAdd = async (values: any) => {
    setSubmitting(true);
    try {
      await createRoom(values);
      message.success('Oda başarıyla eklendi.');
      setIsModalVisible(false);
      form.resetFields();
      fetchRooms();
    } catch (error) {
      message.error('Oda eklenirken bir hata oluştu.');
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    {
      title: 'Oda Adı',
      dataIndex: 'name',
      key: 'name',
    },
    {
      title: 'Kodu',
      dataIndex: 'code',
      key: 'code',
    },
    {
      title: 'Kapasite',
      dataIndex: 'capacity',
      key: 'capacity',
    },
    {
      title: 'Desteklediği Modüller',
      key: 'supportedModules',
      render: (text: string, record: Room) => (
        <>
          {record.supportedModules?.map(moduleId => {
            const moduleName = modules.find(m => m.id === moduleId)?.name || moduleId;
            return <Tag color="cyan" key={moduleId}>{moduleName}</Tag>;
          })}
        </>
      ),
    },
    {
      title: 'Durum',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'Aktif' ? 'green' : 'red'}>
          {status}
        </Tag>
      ),
    },
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Odalar</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={showModal}>
          Yeni Oda
        </Button>
      </div>

      <Table 
        columns={columns} 
        dataSource={data} 
        rowKey="id" 
        loading={loading}
        pagination={false}
      />

      <Modal 
        title="Yeni Oda Ekle" 
        open={isModalVisible} 
        onCancel={handleCancel}
        footer={null}
      >
        <Form layout="vertical" form={form} onFinish={handleAdd}>
          <Form.Item name="name" label="Oda Adı" rules={[{ required: true, message: 'Lütfen oda adı giriniz' }]}>
            <Input />
          </Form.Item>
          
          <Form.Item name="code" label="Kod" rules={[{ required: true, message: 'Lütfen kod giriniz' }]}>
            <Input />
          </Form.Item>
          
          <Form.Item name="capacity" label="Kapasite" rules={[{ required: true }]}>
            <InputNumber min={1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item name="supportedModules" label="Desteklediği Modüller">
            <Select mode="multiple" placeholder="Modül seçiniz">
              {modules.map(m => (
                <Option key={m.id} value={m.id}>{m.name}</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item>
            <Space style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <Button onClick={handleCancel}>İptal</Button>
              <Button type="primary" htmlType="submit" loading={submitting}>
                Kaydet
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default RoomsPage;
