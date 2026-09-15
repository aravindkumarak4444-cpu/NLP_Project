import { apiClient } from './client';

export interface DatasetInfo {
  dataset_id: string;
  name: string;
  version: string;
  records_count: number;
  sif_precursor_count: number;
  non_sif_count: number;
  sif_ratio: number;
  source: string;
  status: string;
  created_at: string;
  description?: string;
  columns?: string[];
  sample_records?: any[];
}

export interface ModelMetrics {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
  macro_f1?: number;
  weighted_f1?: number;
}

export interface RegisteredModel {
  model_id: string;
  model_name: string;
  model_type: string;
  version: string;
  dataset_version: string;
  training_date: string;
  metrics: ModelMetrics;
  status: 'ACTIVE' | 'INACTIVE';
  artifact_path: string;
  description: string;
}

export interface ReviewQueueItem {
  report_id: string;
  report_type: string;
  description: string;
  location: string;
  department: string;
  submitted_by: string;
  created_at: string;
  status: string;
  analysis?: {
    sif_precursor: boolean;
    confidence: number;
    hazard_category: string;
    evidence: string[];
    model_source: string;
  };
}

export interface SystemNotification {
  id: string;
  title: string;
  message: string;
  severity: string;
  type: string;
  timestamp: string;
  link?: string;
}

export interface AuditLogItem {
  timestamp: string;
  user_id: string;
  action: string;
  details: Record<string, any>;
}

export const getDatasets = async (): Promise<DatasetInfo[]> => {
  const response = await apiClient.get<DatasetInfo[]>('/datasets');
  return response.data;
};

export const getDatasetDetails = async (datasetId: string): Promise<DatasetInfo> => {
  const response = await apiClient.get<DatasetInfo>(`/datasets/${datasetId}`);
  return response.data;
};

export const getModels = async (): Promise<RegisteredModel[]> => {
  const response = await apiClient.get<RegisteredModel[]>('/models');
  return response.data;
};

export const getActiveModel = async (): Promise<RegisteredModel> => {
  const response = await apiClient.get<RegisteredModel>('/models/active');
  return response.data;
};

export const activateModel = async (modelId: string): Promise<{ message: string }> => {
  const response = await apiClient.post<{ message: string }>(`/models/activate/${modelId}`);
  return response.data;
};

export const trainModel = async (params: { model_type: string }): Promise<any> => {
  const response = await apiClient.post('/models/train', params);
  return response.data;
};

export const getReviewQueue = async (): Promise<ReviewQueueItem[]> => {
  const response = await apiClient.get<ReviewQueueItem[]>('/reviews');
  return response.data;
};

export const submitHumanReview = async (
  reportId: string,
  review: {
    sif_precursor: boolean;
    hazard_category?: string;
    override_reason: string;
    reviewer_notes?: string;
  }
): Promise<any> => {
  const response = await apiClient.post(`/reviews/${reportId}`, review);
  return response.data;
};

export const getNotifications = async (): Promise<SystemNotification[]> => {
  const response = await apiClient.get<SystemNotification[]>('/notifications');
  return response.data;
};

export const getAuditLogs = async (): Promise<AuditLogItem[]> => {
  const response = await apiClient.get<AuditLogItem[]>('/audit-logs');
  return response.data;
};
