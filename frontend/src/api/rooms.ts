import apiClient from './client';
import { Room } from '../types';

export const getRooms = async (): Promise<Room[]> => {
  const res = await apiClient.get('/rooms');
  return res.data?.data || res.data;
};

export const createRoom = async (data: any): Promise<Room> => {
  const res = await apiClient.post('/rooms', data);
  return res.data;
};

export const updateRoom = async (id: string, data: any): Promise<Room> => {
  const res = await apiClient.put(`/rooms/${id}`, data);
  return res.data;
};
