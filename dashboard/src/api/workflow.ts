import { apiClient } from './client';
import {
  NotificationItem,
  ReviewItem,
  FeedbackItem,
  AuditLogItem,
  AssignedAction,
  User,
  SIFRiskLevel,
} from '../types';

export interface SubmitReviewPayload {
  report_id: string;
  decision: 'ACCEPT' | 'REJECT' | 'CORRECT';
  corrected_sif?: boolean;
  corrected_risk?: SIFRiskLevel;
  corrected_hazard?: string;
  corrected_unsafe_act?: string;
  corrected_unsafe_condition?: string;
  correction_reason?: string;
  assigned_to?: string;
  action_description?: string;
  due_date?: string;
}

export const workflowApi = {
  getNotifications: async (): Promise<NotificationItem[]> => {
    const response = await apiClient.get('/notifications');
    return response.data;
  },

  markNotificationRead: async (notificationId: string): Promise<void> => {
    await apiClient.patch(`/notifications/${notificationId}/read`);
  },

  submitReview: async (payload: SubmitReviewPayload): Promise<ReviewItem> => {
    const response = await apiClient.post('/reviews', payload);
    return response.data;
  },

  listReviews: async (): Promise<ReviewItem[]> => {
    const response = await apiClient.get('/reviews');
    return response.data;
  },

  getFeedbackDataset: async (statusFilter?: string): Promise<FeedbackItem[]> => {
    const response = await apiClient.get('/feedback', { params: { status_filter: statusFilter } });
    return response.data;
  },

  updateFeedbackStatus: async (feedbackId: string, status: string): Promise<void> => {
    await apiClient.patch(`/feedback/${feedbackId}/status`, { status });
  },

  getAuditLogs: async (): Promise<AuditLogItem[]> => {
    const response = await apiClient.get('/audit-logs');
    return response.data;
  },

  getUsers: async (): Promise<User[]> => {
    const response = await apiClient.get('/users');
    return response.data;
  },

  getMyActions: async (): Promise<AssignedAction[]> => {
    const response = await apiClient.get('/actions/my');
    return response.data;
  },

  updateActionStatus: async (reportId: string, actionId: string, status: string): Promise<AssignedAction> => {
    const response = await apiClient.patch(`/actions/${reportId}/${actionId}`, { status });
    return response.data;
  },
};
