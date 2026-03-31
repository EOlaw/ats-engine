'use client'

import { useMutation, type UseMutationResult } from '@tanstack/react-query'
import { ExportAPI } from '@/lib/api/export'
import type { ExportRequest, ExportResponse } from '@/lib/types/api'

export function useCreateExport(): UseMutationResult<
  ExportResponse,
  Error,
  ExportRequest
> {
  return useMutation({
    mutationFn: (req: ExportRequest) => ExportAPI.createExport(req),
  })
}

export function useDownloadExport(): UseMutationResult<void, Error, { exportId: string; filename: string }> {
  return useMutation({
    mutationFn: async ({
      exportId,
      filename,
    }: {
      exportId: string
      filename: string
    }): Promise<void> => {
      const blob = await ExportAPI.downloadExport(exportId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    },
  })
}
