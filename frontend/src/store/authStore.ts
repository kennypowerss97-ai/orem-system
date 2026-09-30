import { create } from 'zustand';
import { User } from '../types';
import * as authApi from '../api/auth';

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  login: (credentials: any) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  login: async (credentials) => {
    const { user, token } = await authApi.login(credentials);
    localStorage.setItem('token', token);
    set({ user, token, isAuthenticated: true });
  },
  logout: () => {
    localStorage.removeItem('token');
    set({ user: null, token: null, isAuthenticated: false });
  },
  checkAuth: async () => {
    if (typeof window !== 'undefined') {
      const params = new URLSearchParams(window.location.search);
      const queryToken = params.get('token') || params.get('access_token') || params.get('auth');
      if (queryToken) {
        localStorage.setItem('token', queryToken);
        set({ token: queryToken, isAuthenticated: true });
      }
    }
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const user = await authApi.getMe();
        set({ user, token, isAuthenticated: true });
      } catch (error) {
        console.warn('Auth check failed:', error);
        localStorage.removeItem('token');
        set({ user: null, token: null, isAuthenticated: false });
      }
    }
  },
}));
