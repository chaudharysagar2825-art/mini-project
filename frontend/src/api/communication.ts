import { apiClient } from './client';
import { CommunicationStatus } from '../types';

export const communicationApi = {
  async getStatus(): Promise<CommunicationStatus> {
    const response = await apiClient.get<CommunicationStatus>('/communication/providers/status');
    return response.data;
  },

  async sendReminder(
    caseId: number,
    phoneNumber: string
  ): Promise<{ status: string; message_id: string; is_mock: boolean; provider: string }> {
    const response = await apiClient.post('/communication/sms/reminder', {
      case_id: caseId,
      phone_number: phoneNumber,
    });
    return response.data;
  },

  async simulateInboundSMS(
    senderPhone: string,
    message: string
  ): Promise<{
    status: string;
    checkin_id?: number;
    case_id?: number;
    message?: string;
  }> {
    const response = await apiClient.post('/communication/sms/inbound', {
      sender_phone: senderPhone,
      message,
    });
    return response.data;
  },

  async analyzeVoiceText(text: string): Promise<{
    user_id: number;
    result: {
      sentiment?: string;
      crisis_signals?: { signal_count: number; matched_signals: string[] };
      distress_indicator?: string;
      [key: string]: unknown;
    };
  }> {
    const response = await apiClient.post('/voice/analyze', { text });
    return response.data;
  },
};
