'use client'

import React, { useState } from 'react'
import { FileText, Trash2, Eye, Wand2, Download, RotateCcw } from 'lucide-react'
import { toast } from 'sonner'
import { format } from 'date-fns'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { ScoreRing } from '@/components/ui/score-ring'
import { useDeleteResume } from '@/lib/hooks/use-resume'
import { STATUS_LABELS, STATUS_COLORS } from '@/lib/constants'
import cn from '@/lib/utils/cn'
import type { ResumeProcessResponse } from '@/lib/types/api'

interface ResumeCardProps {
  resume: ResumeProcessResponse
  onView: (id: string) => void
  onTailor: (id: string) => void
  onExport: (id: string) => void
}

export function ResumeCard({
  resume,
  onView,
  onTailor,
  onExport,
}: ResumeCardProps): React.ReactElement {
  const [confirming, setConfirming] = useState(false)
  const deleteMutation = useDeleteResume()

  const handleDelete = async (): Promise<void> => {
    if (!confirming) {
      setConfirming(true)
      setTimeout(() => setConfirming(false), 3000)
      return
    }
    try {
      await deleteMutation.mutateAsync(resume.id)
      toast.success('Resume deleted')
    } catch {
      toast.error('Failed to delete resume')
    }
  }

  const statusColor = STATUS_COLORS[resume.status]
  const statusLabel = STATUS_LABELS[resume.status]
  const isProcessing = ['pending', 'parsing', 'scoring', 'optimizing'].includes(resume.status)
  const isError = resume.status === 'error'

  return (
    <div className="bg-white border border-slate-200 rounded p-4 space-y-3 hover:border-slate-300 transition-colors duration-150">
      {/* Top row */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-start gap-2.5 min-w-0">
          <FileText className="w-4 h-4 text-slate-400 mt-0.5 shrink-0" />
          <div className="min-w-0">
            <p className="text-xs font-medium text-slate-900 truncate">
              {resume.original_filename}
            </p>
            <p className="text-xs text-slate-400 mt-0.5">
              {format(new Date(resume.created_at), 'MMM d, yyyy')}
            </p>
          </div>
        </div>

        {/* Score ring */}
        {resume.ats_score !== null && (
          <div className="shrink-0">
            <ScoreRing score={resume.ats_score} label="ATS" size="sm" />
          </div>
        )}
      </div>

      {/* Status + file type */}
      <div className="flex items-center gap-2">
        <span
          className={cn(
            'inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium',
            statusColor
          )}
        >
          {isProcessing && (
            <span className="w-1.5 h-1.5 rounded-full bg-current mr-1 animate-pulse" />
          )}
          {statusLabel}
        </span>
        <Badge variant="neutral">{resume.file_type.toUpperCase()}</Badge>
      </div>

      {/* Error message */}
      {isError && resume.error_message && (
        <p className="text-xs text-red-600 bg-red-50 px-2 py-1 rounded">
          {resume.error_message}
        </p>
      )}

      {/* Actions */}
      <div className="flex items-center gap-1.5 pt-1 border-t border-slate-100">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onView(resume.id)}
          className="gap-1"
        >
          <Eye className="w-3 h-3" />
          View
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onTailor(resume.id)}
          disabled={resume.status !== 'optimized' && resume.status !== 'scored'}
          className="gap-1"
        >
          <Wand2 className="w-3 h-3" />
          Tailor
        </Button>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onExport(resume.id)}
          disabled={resume.status === 'pending' || resume.status === 'parsing' || isError}
          className="gap-1"
        >
          <Download className="w-3 h-3" />
          Export
        </Button>
        <div className="flex-1" />
        <Button
          variant={confirming ? 'danger' : 'ghost'}
          size="sm"
          onClick={handleDelete}
          loading={deleteMutation.isPending}
          className="gap-1"
        >
          {confirming ? (
            <>
              <Trash2 className="w-3 h-3" />
              Confirm
            </>
          ) : (
            <Trash2 className="w-3 h-3" />
          )}
        </Button>
      </div>
    </div>
  )
}
