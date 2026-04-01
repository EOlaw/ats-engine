'use client'

import React, { useState } from 'react'
import { toast } from 'sonner'
import { Download } from 'lucide-react'
import { Modal } from '@/components/ui/modal'
import { Button } from '@/components/ui/button'
import { useCreateExport, useDownloadExport } from '@/lib/hooks/use-export'
import { TEMPLATE_OPTIONS } from '@/lib/constants'
import cn from '@/lib/utils/cn'
import type { TemplateEnum, ExportFormat } from '@/lib/types/api'

interface ExportModalProps {
  isOpen: boolean
  onClose: () => void
  resumeId: string
  jobId?: string
}

export function ExportModal({
  isOpen,
  onClose,
  resumeId,
  jobId,
}: ExportModalProps): React.ReactElement {
  const [template, setTemplate] = useState<TemplateEnum>('ats_optimized')
  const [format, setFormat] = useState<ExportFormat>('pdf')
  const [useOptimized, setUseOptimized] = useState(true)

  const createExport = useCreateExport()
  const { download, isDownloading } = useDownloadExport()

  const handleExport = async (): Promise<void> => {
    try {
      const result = await createExport.mutateAsync({
        resume_id: resumeId,
        template_name: template,
        format,
        job_id: jobId,
        use_optimized: useOptimized,
      })
      toast.success('Export generated — downloading...')
      await download(result.export_id, `resume.${format}`)
      onClose()
    } catch {
      toast.error('Export failed. Please try again.')
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Export Resume">
      <div className="space-y-5">
        {/* Template selection */}
        <div>
          <p className="text-xs font-medium text-slate-700 mb-2">Template</p>
          <div className="grid grid-cols-2 gap-2">
            {TEMPLATE_OPTIONS.map((opt) => (
              <button
                key={opt.value}
                onClick={() => setTemplate(opt.value)}
                className={cn(
                  'text-left p-2.5 border rounded transition-colors duration-150',
                  template === opt.value
                    ? 'border-indigo-400 bg-indigo-50'
                    : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
                )}
              >
                <p className="text-xs font-medium text-slate-900">{opt.label}</p>
                <p className="text-xs text-slate-500 mt-0.5 leading-snug">{opt.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Format toggle */}
        <div>
          <p className="text-xs font-medium text-slate-700 mb-2">Format</p>
          <div className="flex gap-2">
            {(['pdf', 'docx'] as ExportFormat[]).map((f) => (
              <button
                key={f}
                onClick={() => setFormat(f)}
                className={cn(
                  'flex-1 py-1.5 text-xs font-medium rounded border transition-colors duration-150',
                  format === f
                    ? 'border-indigo-400 bg-indigo-600 text-white'
                    : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                )}
              >
                {f.toUpperCase()}
              </button>
            ))}
          </div>
        </div>

        {/* Use optimized */}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={useOptimized}
            onChange={(e) => setUseOptimized(e.target.checked)}
            className="accent-indigo-600 w-3.5 h-3.5"
          />
          <span className="text-xs text-slate-700">
            Use AI-optimized content (if available)
          </span>
        </label>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-1">
          <Button variant="secondary" size="sm" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            size="sm"
            onClick={handleExport}
            loading={createExport.isPending || isDownloading}
            className="gap-1.5"
          >
            <Download className="w-3 h-3" />
            {createExport.isPending ? 'Generating...' : isDownloading ? 'Downloading...' : 'Export & Download'}
          </Button>
        </div>
      </div>
    </Modal>
  )
}
