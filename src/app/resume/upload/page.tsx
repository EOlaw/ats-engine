'use client'

import React from 'react'
import { useRouter } from 'next/navigation'
import { AppShell } from '@/components/layout/shell'
import { UploadZone } from '@/components/resume/upload-zone'

export default function UploadPage(): React.ReactElement {
  const router = useRouter()

  const handleSuccess = (resumeId: string): void => {
    router.push(`/resume/editor/${resumeId}`)
  }

  return (
    <AppShell
      title="Upload Resume"
      breadcrumbs={[{ label: 'My Resumes', href: '/resume/history' }, { label: 'Upload' }]}
    >
      <div className="max-w-xl">
        <p className="text-xs text-slate-500 mb-4">
          Upload a PDF or DOCX resume. The AI pipeline will extract, score, and optimize your content.
        </p>
        <UploadZone onSuccess={handleSuccess} />
      </div>
    </AppShell>
  )
}
