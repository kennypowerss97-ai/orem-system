import apiClient from './client';
import { Therapist, PaginatedResponse } from '../types';

export const getTherapists = async (params?: any): Promise<PaginatedResponse<Therapist>> => {
  const res = await apiClient.get('/therapists', { params });
  return res.data;
};

export const getTherapist = async (id: string): Promise<Therapist> => {
  const res = await apiClient.get(`/therapists/${id}`);
  return res.data;
};

export const createTherapist = async (data: any): Promise<Therapist> => {
  const res = await apiClient.post('/therapists', data);
  return res.data;
};

export const updateTherapist = async (id: string, data: any): Promise<Therapist> => {
  const res = await apiClient.put(`/therapists/${id}`, data);
  return res.data;
};

export const deleteTherapist = async (id: string): Promise<void> => {
  await apiClient.delete(`/therapists/${id}`);
};

export const addSpecialization = async (id: string, data: any): Promise<Therapist> => {
  const res = await apiClient.post(`/therapists/${id}/specializations`, data);
  return res.data;
};

export const addAvailability = async (id: string, data: any): Promise<Therapist> => {
  const res = await apiClient.post(`/therapists/${id}/availability`, data);
  return res.data;
};

export const getTherapistSchedule = async (id: string): Promise<any> => {
  const res = await apiClient.get(`/therapists/${id}/schedule`);
  return res.data;
};

export const getTherapistWorkload = async (id: string): Promise<any> => {
  const res = await apiClient.get(`/therapists/${id}/workload`);
  return res.data;
};
