'use client'

import React, { useState } from 'react'
import { useParams } from 'next/navigation'
import { Printer, Download } from 'lucide-react'
import { AppShell } from '@/components/layout/shell'
import { ExportModal } from '@/components/resume/export-modal'
import { Button } from '@/components/ui/button'
import { Spinner } from '@/components/ui/spinner'
import { useResumeById } from '@/lib/hooks/use-resume'
import type { WorkExperience, Education } from '@/lib/types/api'

export default function PreviewPage(): React.ReactElement {
  const params = useParams()
  const id = params.id as string
  const { data: resume, isLoading } = useResumeById(id)
  const [exportOpen, setExportOpen] = useState(false)

  const actions = (
    <div className="flex gap-2">
      <Button
        variant="secondary"
        size="sm"
        onClick={() => window.print()}
        className="gap-1"
      >
        <Printer className="w-3 h-3" />
        Print
      </Button>
      <Button
        variant="primary"
        size="sm"
        onClick={() => setExportOpen(true)}
        className="gap-1"
      >
        <Download className="w-3 h-3" />
        Export
      </Button>
    </div>
  )

  return (
    <AppShell
      title="Resume Preview"
      breadcrumbs={[
        { label: 'My Resumes', href: '/resume/history' },
        { label: 'Preview' },
      ]}
      actions={actions}
    >
      {isLoading ? (
        <div className="flex items-center justify-center py-16">
          <Spinner size="md" />
        </div>
      ) : !resume?.extracted_data ? (
        <p className="text-xs text-slate-500">No extracted data available for preview.</p>
      ) : (
        <div
          id="resume-preview"
          className="max-w-2xl mx-auto bg-white border border-slate-200 rounded p-8 space-y-6 print:border-0 print:shadow-none"
        >
          {/* Header */}
          <div className="border-b border-slate-200 pb-4">
            <h1 className="text-base font-bold text-slate-900">
              {resume.extracted_data.personal_info.full_name ?? 'Candidate'}
            </h1>
            <div className="flex flex-wrap gap-x-4 gap-y-0.5 mt-1">
              {resume.extracted_data.personal_info.email && (
                <span className="text-xs text-slate-600">{resume.extracted_data.personal_info.email}</span>
              )}
              {resume.extracted_data.personal_info.phone && (
                <span className="text-xs text-slate-600">{resume.extracted_data.personal_info.phone}</span>
              )}
              {resume.extracted_data.personal_info.location && (
                <span className="text-xs text-slate-600">{resume.extracted_data.personal_info.location}</span>
              )}
              {resume.extracted_data.personal_info.linkedin_url && (
                <a href={resume.extracted_data.personal_info.linkedin_url} className="text-xs text-indigo-600">
                  LinkedIn
                </a>
              )}
            </div>
          </div>

          {/* Summary */}
          {resume.extracted_data.personal_info.summary && (
            <section>
              <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-1.5">
                Professional Summary
              </h2>
              <p className="text-xs text-slate-700 leading-relaxed">
                {resume.extracted_data.personal_info.summary}
              </p>
            </section>
          )}

          {/* Experience */}
          {resume.extracted_data.work_experience.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-2">
                Work Experience
              </h2>
              <div className="space-y-4">
                {resume.extracted_data.work_experience.map((exp: WorkExperience, i: number) => (
                  <div key={i}>
                    <div className="flex justify-between items-baseline">
                      <p className="text-xs font-medium text-slate-900">{exp.title}</p>
                      <p className="text-xs text-slate-400">
                        {exp.start_date} – {exp.is_current ? 'Present' : exp.end_date}
                      </p>
                    </div>
                    <p className="text-xs text-slate-600">{exp.company}{exp.location ? `, ${exp.location}` : ''}</p>
                    {exp.bullets.length > 0 && (
                      <ul className="mt-1.5 space-y-0.5">
                        {exp.bullets.map((b, j) => (
                          <li key={j} className="text-xs text-slate-700 flex items-start gap-2">
                            <span className="shrink-0 text-slate-400">•</span>{b}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Education */}
          {resume.extracted_data.education.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-2">
                Education
              </h2>
              <div className="space-y-2">
                {resume.extracted_data.education.map((edu: Education, i: number) => (
                  <div key={i} className="flex justify-between items-baseline">
                    <div>
                      <p className="text-xs font-medium text-slate-900">
                        {edu.degree}{edu.field_of_study ? ` in ${edu.field_of_study}` : ''}
                      </p>
                      <p className="text-xs text-slate-600">{edu.institution}</p>
                    </div>
                    <p className="text-xs text-slate-400">{edu.end_date}</p>
                  </div>
                ))}
              </div>
            </section>
          )}

          {/* Skills */}
          {resume.extracted_data.skills.technical.length > 0 && (
            <section>
              <h2 className="text-xs font-semibold text-slate-900 uppercase tracking-wide mb-2">
                Skills
              </h2>
              <div className="flex flex-wrap gap-1">
                {[
                  ...resume.extracted_data.skills.technical,
                  ...resume.extracted_data.skills.tools,
                ].map((s, i) => (
                  <span key={i} className="px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded text-xs">
                    {s}
                  </span>
                ))}
              </div>
            </section>
          )}
        </div>
      )}

      {resume && (
        <ExportModal
          isOpen={exportOpen}
          onClose={() => setExportOpen(false)}
          resumeId={id}
        />
      )}
    </AppShell>
  )
}
