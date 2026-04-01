'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import { Upload, FileText } from 'lucide-react'
import Link from 'next/link'
import { AppShell } from '@/components/layout/shell'
import { ResumeCard } from '@/components/resume/resume-card'
import { TailorModal } from '@/components/resume/tailor-modal'
import { ExportModal } from '@/components/resume/export-modal'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'
import { useResumes } from '@/lib/hooks/use-resume'

export default function HistoryPage(): React.ReactElement {
  const router = useRouter()
  const { data: resumes = [], isLoading } = useResumes()
  const [tailorId, setTailorId] = useState<string | null>(null)
  const [exportId, setExportId] = useState<string | null>(null)

  const actions = (
    <Link href="/resume/upload">
      <Button variant="primary" size="sm" className="gap-1.5">
        <Upload className="w-3 h-3" />
        Upload New
      </Button>
    </Link>
  )

  return (
    <AppShell title="My Resumes" actions={actions}>
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Spinner size="md" />
        </div>
      ) : resumes.length === 0 ? (
        <div className="text-center py-16">
          <FileText className="w-10 h-10 text-slate-300 mx-auto mb-3" />
          <p className="text-xs font-medium text-slate-600">No resumes uploaded yet</p>
          <p className="text-xs text-slate-400 mt-1">Upload your first resume to get started</p>
          <Link href="/resume/upload">
            <Button variant="primary" size="sm" className="mt-4 gap-1.5">
              <Upload className="w-3 h-3" />
              Upload Resume
            </Button>
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-3">
          {resumes.map((resume) => (
            <ResumeCard
              key={resume.id}
              resume={resume}
              onView={(id) => router.push(`/resume/editor/${id}`)}
              onTailor={(id) => setTailorId(id)}
              onExport={(id) => setExportId(id)}
            />
          ))}
        </div>
      )}

      {/* Modals */}
      {tailorId && (
        <TailorModal
          isOpen={!!tailorId}
          onClose={() => setTailorId(null)}
          resumeId={tailorId}
          onSuccess={() => setTailorId(null)}
        />
      )}
      {exportId && (
        <ExportModal
          isOpen={!!exportId}
          onClose={() => setExportId(null)}
          resumeId={exportId}
        />
      )}
    </AppShell>
  )
}
