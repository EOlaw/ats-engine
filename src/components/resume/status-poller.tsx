'use client'

import { useEffect } from 'react'
import { useResumeStatus } from '@/lib/hooks/use-resume'
import type { ResumeProcessResponse } from '@/lib/types/api'

const IN_PROGRESS: Set<string> = new Set([
  'pending',
  'parsing',
  'scoring',
  'optimizing',
])

interface StatusPollerProps {
  resumeId: string
  currentStatus: string
  onComplete: (resume: ResumeProcessResponse) => void
}

export function StatusPoller({
  resumeId,
  currentStatus,
  onComplete,
}: StatusPollerProps): null {
  const isPolling = IN_PROGRESS.has(currentStatus)

  const { data } = useResumeStatus(resumeId, isPolling)

  useEffect(() => {
    if (!data) return
    if (!IN_PROGRESS.has(data.status)) {
      // Pipeline finished — fetch full resume via callback
      onComplete({ id: resumeId } as ResumeProcessResponse)
    }
  }, [data, resumeId, onComplete])

  return null
}
