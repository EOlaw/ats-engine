import { apiClient } from '@/lib/api/client'
import type {
  ResumeUploadResponse,
  ResumeProcessResponse,
  ResumeStatusResponse,
  ATSAnalysis,
  TailoredResumeResponse,
  JobTailoringRequest,
  ProcessingMode,
} from '@/lib/types/api'

export class ResumeAPI {
  static async upload(file: File, mode: ProcessingMode): Promise<ResumeUploadResponse> {
    const formData = new FormData()
    formData.append('file', file)
    return apiClient.postForm<ResumeUploadResponse>(`/upload?mode=${mode}`, formData)
  }

  static async list(skip = 0, limit = 50): Promise<ResumeProcessResponse[]> {
    return apiClient.get<ResumeProcessResponse[]>(`/resumes?skip=${skip}&limit=${limit}`)
  }

  static async getById(id: string): Promise<ResumeProcessResponse> {
    return apiClient.get<ResumeProcessResponse>(`/resumes/${id}`)
  }

  static async getStatus(id: string): Promise<ResumeStatusResponse> {
    return apiClient.get<ResumeStatusResponse>(`/resumes/${id}/status`)
  }

  static async delete(id: string): Promise<void> {
    return apiClient.delete<void>(`/resumes/${id}`)
  }

  static async reprocess(id: string, mode: ProcessingMode): Promise<ResumeProcessResponse> {
    return apiClient.post<ResumeProcessResponse>(
      `/resumes/${id}/reprocess?mode=${mode}`
    )
  }

  static async getAnalysis(id: string): Promise<ATSAnalysis> {
    return apiClient.get<ATSAnalysis>(`/resumes/${id}/analysis`)
  }

  static async tailor(
    id: string,
    req: Omit<JobTailoringRequest, 'resume_id'>
  ): Promise<TailoredResumeResponse> {
    return apiClient.post<TailoredResumeResponse>(`/resumes/${id}/tailor`, {
      resume_id: id,
      ...req,
    })
  }

  static async getTailoring(
    resumeId: string,
    jobId: string
  ): Promise<TailoredResumeResponse> {
    return apiClient.get<TailoredResumeResponse>(
      `/resumes/${resumeId}/tailoring/${jobId}`
    )
  }
}
