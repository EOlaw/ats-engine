import axios from 'axios'
import { apiClient } from '@/lib/api/client'
import { SessionManager } from '@/lib/auth/session'
import type { ExportRequest, ExportResponse } from '@/lib/types/api'

export class ExportAPI {
  static async createExport(req: ExportRequest): Promise<ExportResponse> {
    return apiClient.post<ExportResponse>('/export', req)
  }

  static async downloadExport(exportId: string): Promise<Blob> {
    const token = SessionManager.getAccessToken()
    const response = await axios.get(`/api/v1/exports/${exportId}/download`, {
      responseType: 'blob',
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
    return response.data as Blob
  }
}
