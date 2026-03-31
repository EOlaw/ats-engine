'use client'

import {
  useQuery,
  useMutation,
  useQueryClient,
  type UseQueryResult,
  type UseMutationResult,
} from '@tanstack/react-query'
import { ResumeAPI } from '@/lib/api/resume'
import type {
  ResumeProcessResponse,
  ResumeStatusResponse,
  ProcessingMode,
  TailoredResumeResponse,
} from '@/lib/types/api'

const IN_PROGRESS_STATUSES = new Set([
  'pending',
  'parsing',
  'scoring',
  'optimizing',
])

export function useResumes(): UseQueryResult<ResumeProcessResponse[], Error> {
  return useQuery({
    queryKey: ['resumes'],
    queryFn: () => ResumeAPI.list(),
  })
}

export function useResumeById(
  id: string
): UseQueryResult<ResumeProcessResponse, Error> {
  return useQuery({
    queryKey: ['resume', id],
    queryFn: () => ResumeAPI.getById(id),
    enabled: !!id,
  })
}

export function useResumeStatus(
  id: string,
  enabled: boolean
): UseQueryResult<ResumeStatusResponse, Error> {
  return useQuery({
    queryKey: ['resume-status', id],
    queryFn: () => ResumeAPI.getStatus(id),
    enabled: !!id && enabled,
    refetchInterval: (query) => {
      const data = query.state.data
      if (!data) return 3000
      return IN_PROGRESS_STATUSES.has(data.status) ? 3000 : false
    },
  })
}

export function useUploadResume(): UseMutationResult<
  ResumeProcessResponse & { resume_id: string },
  Error,
  { file: File; mode: ProcessingMode }
> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async ({ file, mode }: { file: File; mode: ProcessingMode }) => {
      const upload = await ResumeAPI.upload(file, mode)
      return { ...upload, id: upload.resume_id } as unknown as ResumeProcessResponse & {
        resume_id: string
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
  })
}

export function useDeleteResume(): UseMutationResult<void, Error, string> {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => ResumeAPI.delete(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['resumes'] })
    },
  })
}

export function useTailorResume(): UseMutationResult<
  TailoredResumeResponse,
  Error,
  { id: string; job_title: string; job_description: string }
> {
  return useMutation({
    mutationFn: ({
      id,
      job_title,
      job_description,
    }: {
      id: string
      job_title: string
      job_description: string
    }) => ResumeAPI.tailor(id, { job_title, job_description }),
  })
}
