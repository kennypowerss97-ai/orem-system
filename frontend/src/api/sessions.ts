import apiClient from './client';
import { TherapySession, PaginatedResponse } from '../types';

export const getSessions = async (params?: any): Promise<PaginatedResponse<TherapySession>> => {
  const res = await apiClient.get('/sessions', { params });
  return res.data;
};

export const getSession = async (id: string): Promise<TherapySession> => {
  const res = await apiClient.get(`/sessions/${id}`);
  return res.data;
};

export const markAttendance = async (id: string, data: any): Promise<TherapySession> => {
  const res = await apiClient.post(`/sessions/${id}/attendance`, data);
  return res.data;
};

export const cancelSession = async (id: string, reason: string): Promise<TherapySession> => {
  const res = await apiClient.post(`/sessions/${id}/cancel`, { reason });
  return res.data;
};

export const getTodaySessions = async (): Promise<TherapySession[]> => {
  const res = await apiClient.get('/sessions/today');
  return res.data;
};

export const updateSession = async (id: string, data: any): Promise<any> => {
  const res = await apiClient.put(`/sessions/${id}`, data);
  return res.data;
};

export const deleteSession = async (id: string): Promise<any> => {
  const res = await apiClient.delete(`/sessions/${id}`);
  return res.data;
};
