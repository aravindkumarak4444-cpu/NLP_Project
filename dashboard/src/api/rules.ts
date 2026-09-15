import { apiClient } from './client';
import { RuleResponse } from '../types';

export const rulesApi = {
  getRules: async (): Promise<RuleResponse[]> => {
    const res = await apiClient.get<RuleResponse[]>('/rules');
    return res.data;
  },
};
