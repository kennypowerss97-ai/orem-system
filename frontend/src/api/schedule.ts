import apiClient from './client';

export const generateSchedule = async (startDate: string, endDate: string): Promise<any> => {
  const res = await apiClient.post('/schedule/generate', { startDate, endDate });
  return res.data;
};

export const addStudentToSchedule = async (studentId: string, data: any): Promise<any> => {
  const res = await apiClient.post(`/schedule/student/${studentId}`, data);
  return res.data;
};

export const getWeeklySchedule = async (params: any): Promise<any> => {
  const res = await apiClient.get('/schedule/weekly', { params });
  return res.data;
};

export const moveSession = async (sessionId: string, newTime: any): Promise<any> => {
  const res = await apiClient.put(`/schedule/sessions/${sessionId}/move`, newTime);
  return res.data;
};

export const getConflicts = async (): Promise<any> => {
  const res = await apiClient.get('/schedule/conflicts');
  return res.data;
};
