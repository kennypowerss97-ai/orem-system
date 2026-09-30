import apiClient from './client';
import { User } from '../types';

export const login = async (credentials: { username: string; password: string }): Promise<{ user: User; token: string }> => {
  const res = await apiClient.post('/auth/login', credentials);
  return {
    user: res.data.user,
    token: res.data.access_token,
  };
};

export const register = async (userData: any): Promise<void> => {
  await apiClient.post('/auth/register', userData);
};

export const getMe = async (): Promise<User> => {
  const res = await apiClient.get('/auth/me');
  return res.data;
};
