import apiClient from './client';
import { TherapyModule } from '../types';

export const getModules = async (): Promise<TherapyModule[]> => {
  const res = await apiClient.get('/modules');
  return Array.isArray(res.data) ? res.data : (res.data?.data || []);
};

export const createModule = async (data: any): Promise<TherapyModule> => {
  const res = await apiClient.post('/modules', data);
  return res.data;
};
