'use client'

import React from 'react'
import Link from 'next/link'
import { FileText, BarChart2, Wand2, Download, Upload } from 'lucide-react'
import { AppShell } from '@/components/layout/shell'
import { StatsCard } from '@/components/dashboard/stats-card'
import { RecentResumes } from '@/components/dashboard/recent-resumes'
import { Button } from '@/components/ui/button'
import { useResumes } from '@/lib/hooks/use-resume'

export default function DashboardPage(): React.ReactElement {
  const { data: resumes = [], isLoading } = useResumes()

  const totalResumes = resumes.length
  const scoredResumes = resumes.filter((r) => r.ats_score !== null)
  const avgScore =
    scoredResumes.length > 0
      ? Math.round(scoredResumes.reduce((acc, r) => acc + (r.ats_score ?? 0), 0) / scoredResumes.length)
      : 0

  const actions = (
    <Link href="/resume/upload">
      <Button variant="primary" size="sm" className="gap-1.5">
        <Upload className="w-3 h-3" />
        Upload Resume
      </Button>
    </Link>
  )

  return (
    <AppShell title="Dashboard" actions={actions}>
      <div className="space-y-5">
        {/* Stats row */}
        <div className="grid grid-cols-4 gap-3">
          <StatsCard
            label="Total Resumes"
            value={totalResumes}
            icon={FileText}
          />
          <StatsCard
            label="Avg ATS Score"
            value={scoredResumes.length > 0 ? `${avgScore}/100` : '—'}
            icon={BarChart2}
            trendUp={avgScore >= 70}
            trend={scoredResumes.length > 0 ? (avgScore >= 70 ? 'Good standing' : 'Needs work') : undefined}
          />
          <StatsCard
            label="Tailored Versions"
            value="—"
            icon={Wand2}
          />
          <StatsCard
            label="Exports Generated"
            value="—"
            icon={Download}
          />
        </div>

        {/* Recent resumes */}
        <RecentResumes resumes={resumes} isLoading={isLoading} />
      </div>
    </AppShell>
  )
}
