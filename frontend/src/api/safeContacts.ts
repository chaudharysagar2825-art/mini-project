import { apiClient } from './client';
import { SafeContact, SafeContactCreatePayload } from '../types';

export const safeContactsApi = {
  async getSafeContacts(caseId: number): Promise<SafeContact[]> {
    const response = await apiClient.get<SafeContact[]>(`/safe-contacts/${caseId}`);
    return response.data;
  },

  async createSafeContact(
    caseId: number,
    payload: SafeContactCreatePayload
  ): Promise<SafeContact> {
    const response = await apiClient.post<SafeContact>(`/safe-contacts/${caseId}`, payload);
    return response.data;
  },

  async deactivateSafeContact(caseId: number, contactId: number): Promise<SafeContact> {
    const response = await apiClient.delete<SafeContact>(
      `/safe-contacts/${caseId}/${contactId}`
    );
    return response.data;
  },
};
