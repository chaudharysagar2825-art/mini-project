import { apiClient } from './client';
import { AuditLog } from '../types';

export const auditApi = {
  async getMyAuditLogs(): Promise<AuditLog[]> {
    const response = await apiClient.get<AuditLog[]>('/audit');
    return response.data;
  },

  async getResourceAuditLogs(resourceType: string, resourceId: string): Promise<AuditLog[]> {
    const response = await apiClient.get<AuditLog[]>(
      `/audit/resource?resource_type=${resourceType}&resource_id=${resourceId}`
    );
    return response.data;
  },
};
