import { apiClient } from './client';
import { Alert, AlertActionPayload } from '../types';

export const alertsApi = {
  async getAlertsQueue(): Promise<Alert[]> {
    const response = await apiClient.get<Alert[]>('/alerts');
    return response.data;
  },

  async getCaseAlerts(caseId: number): Promise<Alert[]> {
    const response = await apiClient.get<Alert[]>(`/alerts/case/${caseId}`);
    return response.data;
  },

  async getAlertById(alertId: number): Promise<Alert> {
    const response = await apiClient.get<Alert>(`/alerts/${alertId}`);
    return response.data;
  },

  async actionAlert(alertId: number, payload: AlertActionPayload): Promise<Alert> {
    const response = await apiClient.patch<Alert>(`/alerts/${alertId}/action`, payload);
    return response.data;
  },
};
