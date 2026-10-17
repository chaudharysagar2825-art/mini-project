import { apiClient } from './client';
import { Consent, ConsentCreatePayload } from '../types';

export const consentApi = {
  async getConsent(caseId: number): Promise<Consent | null> {
    try {
      const response = await apiClient.get<Consent>(`/consent/${caseId}`);
      return response.data;
    } catch (err: unknown) {
      // 404 means no consent record has been submitted yet
      if (err && typeof err === 'object' && 'statusCode' in err && (err as { statusCode: number }).statusCode === 404) {
        return null;
      }
      throw err;
    }
  },

  async createConsent(caseId: number, payload: ConsentCreatePayload): Promise<Consent> {
    const response = await apiClient.post<Consent>(`/consent/${caseId}`, payload);
    return response.data;
  },

  async updateConsentStatus(caseId: number, statusValue: string): Promise<Consent> {
    const response = await apiClient.patch<Consent>(
      `/consent/${caseId}/status?status_value=${statusValue}`
    );
    return response.data;
  },
};
