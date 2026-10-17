import { apiClient } from './client';
import { Case } from '../types';

export const casesApi = {
  async getMyCases(): Promise<Case[]> {
    const response = await apiClient.get<Case[]>('/cases/my');
    return response.data;
  },

  async listAllCases(): Promise<Case[]> {
    const response = await apiClient.get<Case[]>('/cases');
    return response.data;
  },

  async getCaseById(caseId: number): Promise<Case> {
    const response = await apiClient.get<Case>(`/cases/${caseId}`);
    return response.data;
  },

  async generateCase(): Promise<Case> {
    const response = await apiClient.post<Case>('/cases/generate');
    return response.data;
  },

  async createCase(caseCode: string): Promise<Case> {
    const response = await apiClient.post<Case>('/cases', { case_code: caseCode });
    return response.data;
  },

  async updateCaseStatus(caseId: number, status: string): Promise<Case> {
    const response = await apiClient.patch<Case>(`/cases/${caseId}/status?status_value=${status}`);
    return response.data;
  },
};
