import { apiClient } from './client';
import { Assessment } from '../types';

export const assessmentsApi = {
  async getCaseAssessments(caseId: number, limit = 50): Promise<Assessment[]> {
    const response = await apiClient.get<Assessment[]>(`/assessments/case/${caseId}?limit=${limit}`);
    return response.data;
  },

  async getAssessmentById(assessmentId: number): Promise<Assessment> {
    const response = await apiClient.get<Assessment>(`/assessments/${assessmentId}`);
    return response.data;
  },
};
