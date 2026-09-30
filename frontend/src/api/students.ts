import apiClient from './client';
import { Student, PaginatedResponse } from '../types';

export const getStudents = async (params?: any): Promise<PaginatedResponse<Student>> => {
  const res = await apiClient.get('/students', { params });
  return res.data;
};

export const getStudent = async (id: string): Promise<Student> => {
  const res = await apiClient.get(`/students/${id}`);
  return res.data;
};

export const createStudent = async (data: any): Promise<Student> => {
  const res = await apiClient.post('/students', data);
  return res.data;
};

export const updateStudent = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.put(`/students/${id}`, data);
  return res.data;
};

export const deleteStudent = async (id: string): Promise<void> => {
  await apiClient.delete(`/students/${id}`);
};

export const addGuardian = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.post(`/students/${id}/guardian`, data);
  return res.data;
};

export const addRamReport = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.post(`/students/${id}/ram-report`, data);
  return res.data;
};

export const addAllocatedModule = async (id: string, data: any): Promise<Student> => {
  const res = await apiClient.post(`/students/${id}/modules`, data);
  return res.data;
};

export const getStudentSchedule = async (id: string): Promise<any> => {
  const res = await apiClient.get(`/students/${id}/schedule`);
  return res.data;
};
