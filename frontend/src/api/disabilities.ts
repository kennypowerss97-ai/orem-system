import apiClient from './client';

export interface DisabilityItem {
  id: number;
  name: string;
  description?: string;
  isActive: boolean;
  createdAt?: string;
}

export const getDisabilities = async (): Promise<DisabilityItem[]> => {
  const res = await apiClient.get('/disabilities');
  return res.data;
};

export const createDisability = async (data: { name: string; description?: string }): Promise<any> => {
  const res = await apiClient.post('/disabilities', data);
  return res.data;
};

export const updateDisability = async (id: number, data: { name?: string; description?: string; isActive?: boolean }): Promise<any> => {
  const res = await apiClient.put(`/disabilities/${id}`, data);
  return res.data;
};

export const deleteDisability = async (id: number): Promise<any> => {
  const res = await apiClient.delete(`/disabilities/${id}`);
  return res.data;
};
