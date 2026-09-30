import apiClient from './client';
import { TeacherBranch } from '../types';

export const getBranches = async (params?: any): Promise<TeacherBranch[]> => {
  const res = await apiClient.get('/branches', { params });
  return res.data;
};

export const createBranch = async (data: Partial<TeacherBranch>): Promise<any> => {
  const res = await apiClient.post('/branches', data);
  return res.data;
};

export const updateBranch = async (id: number, data: Partial<TeacherBranch>): Promise<any> => {
  const res = await apiClient.put(`/branches/${id}`, data);
  return res.data;
};

export const deleteBranch = async (id: number): Promise<any> => {
  const res = await apiClient.delete(`/branches/${id}`);
  return res.data;
};
