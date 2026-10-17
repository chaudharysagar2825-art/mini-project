import { apiClient } from './client';
import { CaseTrendsResponse, DashboardSummary } from '../types';

export const dashboardApi = {
  async getDashboardSummary(): Promise<DashboardSummary> {
    const response = await apiClient.get<DashboardSummary>('/dashboards/summary');
    return response.data;
  },

  async getCaseTrends(caseId: number): Promise<CaseTrendsResponse> {
    const response = await apiClient.get<CaseTrendsResponse>(`/dashboards/case/${caseId}/trends`);
    return response.data;
  },
};
