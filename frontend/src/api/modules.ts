import apiClient from './client';
import { TherapyModule } from '../types';

export const DEFAULT_MODULES = [
  { id: '1', name: 'Dil ve Konuşma Güçlüğü', code: 'DIL_KONUSMA', color: '#1890ff' },
  { id: '2', name: 'Bedensel Engelli (Fizyoterapi)', code: 'BEDENSEL_FIZYOTERAPI', color: '#52c41a' },
  { id: '3', name: 'Özel Öğrenme Güçlüğü (Disleksi)', code: 'OZEL_OGRENME', color: '#fa8c16' },
  { id: '4', name: 'Otizm Spektrum Bozukluğu', code: 'OTIZM', color: '#722ed1' },
  { id: '5', name: 'Zihinsel Engelliler Eğitimi', code: 'ZIHINSEL', color: '#eb2f96' },
  { id: '6', name: 'İşitme Engelliler Eğitimi', code: 'ISITME', color: '#13c2c2' },
  { id: '7', name: 'Görme Engelliler Eğitimi', code: 'GORME', color: '#faad14' }
];

export const getModules = async (): Promise<TherapyModule[]> => {
  try {
    const res = await apiClient.get('/modules');
    const list = Array.isArray(res.data) ? res.data : (res.data?.data || []);
    if (list && list.length > 0) {
      return list;
    }
  } catch (error) {
    console.warn('Backend modülleri alınamadı, yerel MEB modülleri kullanılıyor:', error);
  }
  return DEFAULT_MODULES as any;
};

export const createModule = async (data: any): Promise<TherapyModule> => {
  const res = await apiClient.post('/modules', data);
  return res.data;
};

