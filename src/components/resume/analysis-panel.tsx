'use client'

import React, { useState } from 'react'
import { ATSScoreCard } from '@/components/resume/ats-score-card'
import cn from '@/lib/utils/cn'
import type { ResumeProcessResponse, WorkExperience, Education } from '@/lib/types/api'

type TabId = 'score' | 'extracted' | 'optimized' | 'tailored'

interface Tab {
  id: TabId
  label: string
}

const TABS: Tab[] = [
  { id: 'score', label: 'ATS Score' },
  { id: 'extracted', label: 'Extracted Data' },
  { id: 'optimized', label: 'Optimized' },
  { id: 'tailored', label: 'Tailored Versions' },
]

interface AnalysisPanelProps {
  resume: ResumeProcessResponse
  onTailor: () => void
}

function ExtractedDataView({ resume }: { resume: ResumeProcessResponse }): React.ReactElement {
  const data = resume.extracted_data
  if (!data) {
    return <p className="text-xs text-slate-500">No extracted data available yet.</p>
  }
  const pi = data.personal_info

  return (
    <div className="space-y-5">
      {/* Personal Info */}
      <section>
        <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">
          Personal Info
        </p>
        <div className="grid grid-cols-2 gap-x-6 gap-y-1.5 text-xs">
          {pi.full_name && (
            <><span className="text-slate-500">Name</span><span className="text-slate-900">{pi.full_name}</span></>
          )}
          {pi.email && (
            <><span className="text-slate-500">Email</span><span className="text-slate-900">{pi.email}</span></>
          )}
          {pi.phone && (
            <><span className="text-slate-500">Phone</span><span className="text-slate-900">{pi.phone}</span></>
          )}
          {pi.location && (
            <><span className="text-slate-500">Location</span><span className="text-slate-900">{pi.location}</span></>
          )}
          {pi.linkedin_url && (
            <><span className="text-slate-500">LinkedIn</span><a href={pi.linkedin_url} className="text-indigo-600 hover:underline truncate">{pi.linkedin_url}</a></>
          )}
        </div>
        {pi.summary && (
          <p className="mt-2 text-xs text-slate-700 leading-relaxed">{pi.summary}</p>
        )}
      </section>

      {/* Skills */}
      {(data.skills.technical.length > 0 || data.skills.tools.length > 0) && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Skills</p>
          <div className="space-y-2">
            {data.skills.technical.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1">Technical</p>
                <div className="flex flex-wrap gap-1">
                  {data.skills.technical.map((s, i) => (
                    <span key={i} className="px-1.5 py-0.5 bg-indigo-50 text-indigo-700 rounded text-xs">{s}</span>
                  ))}
                </div>
              </div>
            )}
            {data.skills.tools.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1">Tools & Platforms</p>
                <div className="flex flex-wrap gap-1">
                  {data.skills.tools.map((s, i) => (
                    <span key={i} className="px-1.5 py-0.5 bg-slate-100 text-slate-700 rounded text-xs">{s}</span>
                  ))}
                </div>
              </div>
            )}
            {data.skills.soft.length > 0 && (
              <div>
                <p className="text-xs text-slate-500 mb-1">Soft Skills</p>
                <div className="flex flex-wrap gap-1">
                  {data.skills.soft.map((s, i) => (
                    <span key={i} className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded text-xs">{s}</span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </section>
      )}

      {/* Work Experience */}
      {data.work_experience.length > 0 && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Work Experience</p>
          <div className="space-y-3">
            {data.work_experience.map((exp: WorkExperience, i: number) => (
              <div key={i} className="border-l-2 border-indigo-200 pl-3">
                <p className="text-xs font-medium text-slate-900">{exp.title}</p>
                <p className="text-xs text-slate-600">{exp.company} {exp.location ? `— ${exp.location}` : ''}</p>
                <p className="text-xs text-slate-400">
                  {exp.start_date} – {exp.is_current ? 'Present' : exp.end_date}
                </p>
                {exp.bullets.length > 0 && (
                  <ul className="mt-1.5 space-y-0.5">
                    {exp.bullets.map((b, j) => (
                      <li key={j} className="text-xs text-slate-700 flex items-start gap-1.5">
                        <span className="text-slate-400 shrink-0">•</span>{b}
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
      {data.education.length > 0 && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">Education</p>
          <div className="space-y-2">
            {data.education.map((edu: Education, i: number) => (
              <div key={i}>
                <p className="text-xs font-medium text-slate-900">
                  {edu.degree} {edu.field_of_study ? `in ${edu.field_of_study}` : ''}
                </p>
                <p className="text-xs text-slate-600">{edu.institution}</p>
                <p className="text-xs text-slate-400">{edu.start_date} – {edu.end_date}</p>
                {edu.gpa && <p className="text-xs text-slate-500">GPA: {edu.gpa}</p>}
              </div>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

function OptimizedView({ resume }: { resume: ResumeProcessResponse }): React.ReactElement {
  const opt = resume.optimized_content as {
    professional_summary?: string
    work_experience?: Array<{ company?: string; title?: string; optimized_bullets?: string[] }>
    skills_grouping?: Record<string, string[]>
    optimization_notes?: string[]
  } | null

  if (!opt) {
    return (
      <div className="text-center py-8">
        <p className="text-xs text-slate-500">
          Optimized content is not available. Reprocess with <strong>Full Optimization</strong> mode.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-5">
      {opt.professional_summary && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">
            Optimized Summary
          </p>
          <p className="text-xs text-slate-700 leading-relaxed bg-green-50 border border-green-200 rounded p-3">
            {opt.professional_summary}
          </p>
        </section>
      )}

      {opt.work_experience && opt.work_experience.length > 0 && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">
            Optimized Bullets
          </p>
          <div className="space-y-3">
            {opt.work_experience.map((exp, i) => (
              <div key={i} className="border-l-2 border-green-300 pl-3">
                <p className="text-xs font-medium text-slate-900">{exp.title} — {exp.company}</p>
                <ul className="mt-1.5 space-y-0.5">
                  {(exp.optimized_bullets ?? []).map((b, j) => (
                    <li key={j} className="text-xs text-slate-700 flex items-start gap-1.5">
                      <span className="text-green-500 shrink-0">•</span>{b}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </section>
      )}

      {opt.skills_grouping && Object.keys(opt.skills_grouping).length > 0 && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">
            Skills Regrouped
          </p>
          <div className="space-y-2">
            {Object.entries(opt.skills_grouping).map(([cat, items]) => (
              <div key={cat}>
                <p className="text-xs text-slate-500 capitalize mb-1">{cat.replace(/_/g, ' ')}</p>
                <div className="flex flex-wrap gap-1">
                  {(items as string[]).map((s, i) => (
                    <span key={i} className="px-1.5 py-0.5 bg-green-50 text-green-700 rounded text-xs">{s}</span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {opt.optimization_notes && opt.optimization_notes.length > 0 && (
        <section>
          <p className="text-xs font-semibold text-slate-700 uppercase tracking-wide mb-2">
            Changes Made
          </p>
          <ul className="space-y-1">
            {opt.optimization_notes.map((note, i) => (
              <li key={i} className="text-xs text-slate-600 flex items-start gap-1.5">
                <span className="text-indigo-500 shrink-0">→</span>{note}
              </li>
            ))}
          </ul>
        </section>
      )}
    </div>
  )
}

export function AnalysisPanel({ resume, onTailor }: AnalysisPanelProps): React.ReactElement {
  const [activeTab, setActiveTab] = useState<TabId>('score')

  return (
    <div className="bg-white border border-slate-200 rounded">
      {/* Tab bar */}
      <div className="flex border-b border-slate-200">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={cn(
              'px-4 py-2.5 text-xs font-medium transition-colors duration-150 border-b-2 -mb-px',
              activeTab === tab.id
                ? 'border-indigo-600 text-indigo-600'
                : 'border-transparent text-slate-500 hover:text-slate-700'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="p-5">
        {activeTab === 'score' && (
          resume.ats_analysis
            ? <ATSScoreCard analysis={resume.ats_analysis} />
            : <p className="text-xs text-slate-500">ATS analysis not yet available.</p>
        )}
        {activeTab === 'extracted' && <ExtractedDataView resume={resume} />}
        {activeTab === 'optimized' && <OptimizedView resume={resume} />}
        {activeTab === 'tailored' && (
          <div className="text-center py-8 space-y-3">
            <p className="text-xs text-slate-500">
              Tailor this resume to a specific job description to see versions here.
            </p>
            <button
              onClick={onTailor}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-indigo-600 text-white text-xs font-medium rounded hover:bg-indigo-700 transition-colors"
            >
              Tailor to a Job
            </button>
          </div>
        )}
      </div>
    </div>
  )
}
