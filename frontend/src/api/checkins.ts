import { apiClient } from './client';
import { CheckIn, CheckInCreatePayload } from '../types';

export const checkinsApi = {
  async submitCheckIn(caseId: number, payload: CheckInCreatePayload): Promise<CheckIn> {
    const response = await apiClient.post<CheckIn>(`/checkins/${caseId}`, payload);
    return response.data;
  },

  async getCaseCheckIns(caseId: number): Promise<CheckIn[]> {
    const response = await apiClient.get<CheckIn[]>(`/checkins/case/${caseId}`);
    return response.data;
  },

  async getCheckInById(checkinId: number): Promise<CheckIn> {
    const response = await apiClient.get<CheckIn>(`/checkins/${checkinId}`);
    return response.data;
  },
};
