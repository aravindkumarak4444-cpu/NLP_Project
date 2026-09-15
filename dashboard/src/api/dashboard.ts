import { apiClient } from './client';
import { DashboardSummaryResponse, PatternAnalysisResult, TrendPoint } from '../types';

export const dashboardApi = {
  getSummary: async (): Promise<DashboardSummaryResponse> => {
    const res = await apiClient.get<DashboardSummaryResponse>('/dashboard/summary');
    return res.data;
  },

  getTrends: async (): Promise<{ sif_trends: TrendPoint[] }> => {
    const res = await apiClient.get<{ sif_trends: TrendPoint[] }>('/dashboard/trends');
    return res.data;
  },

  getPatterns: async (): Promise<PatternAnalysisResult> => {
    const res = await apiClient.get<PatternAnalysisResult>('/dashboard/patterns');
    return res.data;
  },
};
