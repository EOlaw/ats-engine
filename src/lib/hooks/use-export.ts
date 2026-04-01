'use client'

import { useState } from 'react'
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

interface UseDownloadExportReturn {
  download: (exportId: string, filename: string) => Promise<void>
  isDownloading: boolean
}

export function useDownloadExport(): UseDownloadExportReturn {
  const [isDownloading, setIsDownloading] = useState(false)

  const download = async (exportId: string, filename: string): Promise<void> => {
    setIsDownloading(true)
    try {
      const blob = await ExportAPI.downloadExport(exportId)
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } finally {
      setIsDownloading(false)
    }
  }

  return { download, isDownloading }
}
