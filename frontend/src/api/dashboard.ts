import apiClient from './client';
import { DashboardStats, Alert } from '../types';

export const getStats = async (): Promise<DashboardStats> => {
  const res = await apiClient.get('/dashboard/stats');
  return res.data;
};

export const getToday = async (): Promise<any> => {
  const res = await apiClient.get('/dashboard/today');
  return res.data;
};

export const getAlerts = async (): Promise<Alert[]> => {
  const res = await apiClient.get('/dashboard/alerts');
  return res.data;
};
