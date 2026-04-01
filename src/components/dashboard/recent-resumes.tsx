'use client'

import React from 'react'
import Link from 'next/link'
import { format } from 'date-fns'
import { FileText, ArrowRight } from 'lucide-react'
import { ScoreRing } from '@/components/ui/score-ring'
import { STATUS_LABELS, STATUS_COLORS } from '@/lib/constants'
import cn from '@/lib/utils/cn'
import type { ResumeProcessResponse } from '@/lib/types/api'

interface RecentResumesProps {
  resumes: ResumeProcessResponse[]
  isLoading: boolean
}

export function RecentResumes({
  resumes,
  isLoading,
}: RecentResumesProps): React.ReactElement {
  if (isLoading) {
    return (
      <div className="bg-white border border-slate-200 rounded">
        <div className="px-4 py-3 border-b border-slate-200">
          <p className="text-xs font-medium text-slate-700">Recent Resumes</p>
        </div>
        <div className="divide-y divide-slate-100">
          {[1, 2, 3].map((i) => (
            <div key={i} className="px-4 py-3 flex items-center gap-3 animate-pulse">
              <div className="w-4 h-4 bg-slate-200 rounded" />
              <div className="flex-1 space-y-1.5">
                <div className="h-2.5 bg-slate-200 rounded w-1/3" />
                <div className="h-2 bg-slate-100 rounded w-1/5" />
              </div>
              <div className="w-8 h-8 bg-slate-100 rounded-full" />
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (resumes.length === 0) {
    return (
      <div className="bg-white border border-slate-200 rounded">
        <div className="px-4 py-3 border-b border-slate-200">
          <p className="text-xs font-medium text-slate-700">Recent Resumes</p>
        </div>
        <div className="px-4 py-8 text-center">
          <FileText className="w-8 h-8 text-slate-300 mx-auto mb-2" />
          <p className="text-xs text-slate-500">No resumes yet.</p>
          <Link
            href="/resume/upload"
            className="inline-flex items-center gap-1 mt-2 text-xs text-indigo-600 hover:text-indigo-700 font-medium"
          >
            Upload your first resume <ArrowRight className="w-3 h-3" />
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded">
      <div className="px-4 py-3 border-b border-slate-200 flex items-center justify-between">
        <p className="text-xs font-medium text-slate-700">Recent Resumes</p>
        <Link
          href="/resume/history"
          className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
        >
          View all
        </Link>
      </div>

      {/* Table header */}
      <div className="grid grid-cols-[1fr_80px_60px_90px_80px] gap-3 px-4 py-2 border-b border-slate-100">
        {['Filename', 'Status', 'Score', 'Uploaded', ''].map((h) => (
          <p key={h} className="text-xs font-medium text-slate-400">{h}</p>
        ))}
      </div>

      {/* Rows */}
      <div className="divide-y divide-slate-50">
        {resumes.slice(0, 5).map((resume) => (
          <div
            key={resume.id}
            className="grid grid-cols-[1fr_80px_60px_90px_80px] gap-3 px-4 py-2.5 items-center hover:bg-slate-50 transition-colors"
          >
            {/* Filename */}
            <div className="flex items-center gap-2 min-w-0">
              <FileText className="w-3.5 h-3.5 text-slate-400 shrink-0" />
              <span className="text-xs text-slate-900 truncate">{resume.original_filename}</span>
            </div>

            {/* Status */}
            <span
              className={cn(
                'inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium w-fit',
                STATUS_COLORS[resume.status]
              )}
            >
              {STATUS_LABELS[resume.status]}
            </span>

            {/* Score */}
            <div>
              {resume.ats_score !== null ? (
                <ScoreRing score={resume.ats_score} size="sm" />
              ) : (
                <span className="text-xs text-slate-400">—</span>
              )}
            </div>

            {/* Date */}
            <span className="text-xs text-slate-500">
              {format(new Date(resume.created_at), 'MMM d, yyyy')}
            </span>

            {/* Action */}
            <Link
              href={`/resume/editor/${resume.id}`}
              className="text-xs text-indigo-600 hover:text-indigo-700 font-medium"
            >
              View
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}
