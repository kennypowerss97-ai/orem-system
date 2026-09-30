import apiClient from './client';
import { EducationProgram } from '../types';

export const getEducationPrograms = async (): Promise<EducationProgram[]> => {
  const res = await apiClient.get('/programs');
  return res.data;
};

export const createEducationProgram = async (data: any): Promise<any> => {
  const res = await apiClient.post('/programs', data);
  return res.data;
};

export const updateEducationProgram = async (id: number, data: any): Promise<any> => {
  const res = await apiClient.put(`/programs/${id}`, data);
  return res.data;
};

export const deleteEducationProgram = async (id: number): Promise<any> => {
  const res = await apiClient.delete(`/programs/${id}`);
  return res.data;
};

export const addProgramModule = async (programId: number, data: any): Promise<any> => {
  const res = await apiClient.post(`/programs/${programId}/modules`, data);
  return res.data;
};

export const updateProgramModule = async (moduleId: number, data: any): Promise<any> => {
  const res = await apiClient.put(`/programs/modules/${moduleId}`, data);
  return res.data;
};

export const deleteProgramModule = async (moduleId: number): Promise<any> => {
  const res = await apiClient.delete(`/programs/modules/${moduleId}`);
  return res.data;
};
