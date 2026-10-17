import { apiClient } from './client';
import { Referral, ReferralCreatePayload, ReferralStatusUpdatePayload } from '../types';

export const referralsApi = {
  async getCaseReferrals(caseId: number): Promise<Referral[]> {
    const response = await apiClient.get<Referral[]>(`/referrals/case/${caseId}`);
    return response.data;
  },

  async getReferralById(referralId: number): Promise<Referral> {
    const response = await apiClient.get<Referral>(`/referrals/${referralId}`);
    return response.data;
  },

  async createReferral(caseId: number, payload: ReferralCreatePayload): Promise<Referral> {
    const response = await apiClient.post<Referral>(`/referrals/${caseId}`, payload);
    return response.data;
  },

  async updateReferralStatus(
    referralId: number,
    payload: ReferralStatusUpdatePayload
  ): Promise<Referral> {
    const response = await apiClient.patch<Referral>(`/referrals/${referralId}/status`, payload);
    return response.data;
  },
};
