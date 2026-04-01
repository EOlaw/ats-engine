'use client'

import React, { useState, useCallback } from 'react'
import { useParams } from 'next/navigation'
import { Download, Wand2, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { AppShell } from '@/components/layout/shell'
import { AnalysisPanel } from '@/components/resume/analysis-panel'
import { TailorModal } from '@/components/resume/tailor-modal'
import { ExportModal } from '@/components/resume/export-modal'
import { StatusPoller } from '@/components/resume/status-poller'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'
import { Badge } from '@/components/ui/badge'
import { useResumeById } from '@/lib/hooks/use-resume'
import { STATUS_LABELS, STATUS_COLORS } from '@/lib/constants'
import { ResumeAPI } from '@/lib/api/resume'
import cn from '@/lib/utils/cn'
import type { TailoredResumeResponse } from '@/lib/types/api'

const IN_PROGRESS = new Set(['pending', 'parsing', 'scoring', 'optimizing'])

export default function ResumeEditorPage(): React.ReactElement {
  const params = useParams()
  const id = params.id as string

  const { data: resume, isLoading, refetch } = useResumeById(id)
  const [tailorOpen, setTailorOpen] = useState(false)
  const [exportOpen, setExportOpen] = useState(false)
  const [isReprocessing, setIsReprocessing] = useState(false)

  const handlePollerComplete = useCallback(() => {
    refetch()
  }, [refetch])

  const handleTailorSuccess = (_result: TailoredResumeResponse): void => {
    setTailorOpen(false)
    toast.success('Resume tailored — view in the Tailored Versions tab')
  }

  const handleReprocess = async (): Promise<void> => {
    if (!resume) return
    setIsReprocessing(true)
    try {
      await ResumeAPI.reprocess(id, 'full_optimization')
      toast.success('Reprocessing started')
      refetch()
    } catch {
      toast.error('Failed to start reprocessing')
    } finally {
      setIsReprocessing(false)
    }
  }

  const isProcessing = resume ? IN_PROGRESS.has(resume.status) : false

  const actions = resume ? (
    <div className="flex items-center gap-2">
      <Button
        variant="ghost"
        size="sm"
        onClick={handleReprocess}
        loading={isReprocessing}
        className="gap-1"
      >
        <RotateCcw className="w-3 h-3" />
        Reprocess
      </Button>
      <Button
        variant="secondary"
        size="sm"
        onClick={() => setTailorOpen(true)}
        disabled={isProcessing}
        className="gap-1"
      >
        <Wand2 className="w-3 h-3" />
        Tailor
      </Button>
      <Button
        variant="primary"
        size="sm"
        onClick={() => setExportOpen(true)}
        disabled={isProcessing || resume.status === 'error'}
        className="gap-1"
      >
        <Download className="w-3 h-3" />
        Export
      </Button>
    </div>
  ) : undefined

  return (
    <AppShell
      title={resume?.original_filename ?? 'Resume'}
      breadcrumbs={[{ label: 'My Resumes', href: '/resume/history' }, { label: 'Editor' }]}
      actions={actions}
    >
      {/* Status poller — runs silently while processing */}
      {resume && isProcessing && (
        <StatusPoller
          resumeId={id}
          currentStatus={resume.status}
          onComplete={handlePollerComplete}
        />
      )}

      {isLoading && (
        <div className="flex items-center justify-center py-16">
          <Spinner size="md" />
        </div>
      )}

      {!isLoading && resume && (
        <>
          {/* Status bar while processing */}
          {isProcessing && (
            <div className="mb-4 flex items-center gap-2 px-3 py-2 bg-indigo-50 border border-indigo-200 rounded text-xs text-indigo-700">
              <Spinner size="sm" />
              <span>
                Processing resume — {STATUS_LABELS[resume.status]}...
                This may take 30–60 seconds.
              </span>
            </div>
          )}

          {resume.status === 'error' && (
            <div className="mb-4 px-3 py-2 bg-red-50 border border-red-200 rounded text-xs text-red-700">
              Processing failed: {resume.error_message ?? 'Unknown error'}
            </div>
          )}

          <AnalysisPanel
            resume={resume}
            onTailor={() => setTailorOpen(true)}
          />
        </>
      )}

      {/* Modals */}
      {resume && (
        <>
          <TailorModal
            isOpen={tailorOpen}
            onClose={() => setTailorOpen(false)}
            resumeId={id}
            onSuccess={handleTailorSuccess}
          />
          <ExportModal
            isOpen={exportOpen}
            onClose={() => setExportOpen(false)}
            resumeId={id}
          />
        </>
      )}
    </AppShell>
  )
}
