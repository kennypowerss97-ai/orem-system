import apiClient from './client';
import { IepPlan, ProgressRecord } from '../types';

export const getIepPlans = async (studentId?: string): Promise<IepPlan[]> => {
  const params = studentId ? { student_id: studentId } : {};
  const res = await apiClient.get('/iep/plans', { params });
  return res.data;
};

export const createIepPlan = async (data: any): Promise<any> => {
  const res = await apiClient.post('/iep/plans', data);
  return res.data;
};

export const addProgressRecord = async (data: any): Promise<any> => {
  const res = await apiClient.post('/iep/progress', data);
  return res.data;
};

export const getStudentProgress = async (studentId: string): Promise<any[]> => {
  const res = await apiClient.get('/iep/plans', { params: { student_id: studentId } });
  return res.data;
};
