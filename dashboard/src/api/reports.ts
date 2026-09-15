import { apiClient } from './client';
import {
  SafetyReport,
  ReportListResponse,
  ReportCreatePayload,
  AnalysisResponse,
  AIStatusResponse,
} from '../types';

export interface ReportQueryParams {
  page?: number;
  limit?: number;
  status?: string;
  report_type?: string;
  risk_level?: string;
  sif_precursor?: boolean;
  department?: string;
  location?: string;
  search?: string;
}

export const reportsApi = {
  createReport: async (payload: ReportCreatePayload): Promise<SafetyReport> => {
    const res = await apiClient.post<SafetyReport>('/reports', payload);
    return res.data;
  },

  listReports: async (params: ReportQueryParams = {}): Promise<ReportListResponse> => {
    const res = await apiClient.get<ReportListResponse>('/reports', { params });
    return res.data;
  },

  getMyReports: async (params: ReportQueryParams = {}): Promise<ReportListResponse> => {
    const res = await apiClient.get<ReportListResponse>('/reports/my', { params });
    return res.data;
  },

  getReportById: async (id: string): Promise<SafetyReport> => {
    const res = await apiClient.get<SafetyReport>(`/reports/${id}`);
    return res.data;
  },

  analyzeReport: async (id: string): Promise<AnalysisResponse> => {
    const res = await apiClient.post<AnalysisResponse>(`/analysis/${id}`);
    return res.data;
  },

  getAIStatus: async (): Promise<AIStatusResponse> => {
    const res = await apiClient.get<AIStatusResponse>('/analysis/status');
    return res.data;
  },

  addActionItem: async (
    reportId: string,
    description: string,
    assignedTo?: string,
    dueDate?: string
  ): Promise<SafetyReport> => {
    const res = await apiClient.post<SafetyReport>(`/reports/${reportId}/actions`, {
      description,
      assigned_to: assignedTo || null,
      due_date: dueDate || null,
    });
    return res.data;
  },

  updateStatus: async (reportId: string, status: string, reason?: string): Promise<SafetyReport> => {
    const res = await apiClient.patch<SafetyReport>(`/reports/${reportId}/status`, {
      status,
      reason: reason || null,
    });
    return res.data;
  },

  updateActionStatus: async (
    reportId: string,
    actionId: string,
    status: string,
    assignedTo?: string
  ): Promise<SafetyReport> => {
    const res = await apiClient.patch<SafetyReport>(`/reports/${reportId}/actions/${actionId}`, {
      status,
      assigned_to: assignedTo || null,
    });
    return res.data;
  },

  deleteReport: async (reportId: string): Promise<void> => {
    await apiClient.delete(`/reports/${reportId}`);
  },
};

