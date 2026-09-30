import apiClient from './client';

export const getStudentProgress = async (studentId: string): Promise<any> => {
  const res = await apiClient.get(`/reports/progress/${studentId}`);
  return res.data;
};

export const getMonthlyAttendance = async (month?: string): Promise<any> => {
  const res = await apiClient.get('/reports/attendance/monthly', { params: month ? { month } : {} });
  return res.data;
};

export const getTherapistWorkload = async (): Promise<any> => {
  const res = await apiClient.get('/reports/therapist-workload');
  return res.data;
};

export const getCapacity = async (): Promise<any> => {
  const res = await apiClient.get('/reports/capacity');
  return res.data;
};
