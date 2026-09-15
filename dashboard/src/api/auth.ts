import { apiClient } from './client';
import { TokenResponse, User, UserRegisterPayload } from '../types';

export const authApi = {
  login: async (email: string, password: string): Promise<TokenResponse> => {
    const res = await apiClient.post<TokenResponse>('/auth/login', { email, password });
    return res.data;
  },

  register: async (payload: UserRegisterPayload): Promise<User> => {
    const res = await apiClient.post<User>('/auth/register', payload);
    return res.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const res = await apiClient.get<User>('/auth/me');
    return res.data;
  },

  getUsers: async (): Promise<User[]> => {
    const res = await apiClient.get<User[]>('/auth/users');
    return res.data;
  },
};

