import React from 'react'
import { CheckCircle, XCircle, AlertTriangle } from 'lucide-react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'
import { ScoreRing } from '@/components/ui/score-ring'
import { Badge } from '@/components/ui/badge'
import type { ATSAnalysis } from '@/lib/types/api'

interface ATSScoreCardProps {
  analysis: ATSAnalysis
}

function getBarColor(value: number): string {
  if (value >= 80) return '#16a34a'
  if (value >= 60) return '#d97706'
  return '#dc2626'
}

export function ATSScoreCard({ analysis }: ATSScoreCardProps): React.ReactElement {
  const breakdownData = Object.entries(analysis.score_breakdown).map(
    ([key, val]) => ({
      name: key.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()),
      value: Math.round(val),
    })
  )

  return (
    <div className="space-y-5">
      {/* Main score */}
      <div className="flex items-center gap-6 p-4 bg-slate-50 border border-slate-200 rounded">
        <ScoreRing score={analysis.score_estimate} label="ATS Score" size="lg" />
        <div className="flex-1 space-y-2">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <p className="text-xs text-slate-500">Quantification</p>
              <p className="text-xs font-medium text-slate-900">
                {Math.round(analysis.quantification_score)}/100
              </p>
            </div>
            <div>
              <p className="text-xs text-slate-500">Action Verbs</p>
              <p className="text-xs font-medium text-slate-900">
                {Math.round(analysis.action_verb_score)}/100
              </p>
            </div>
          </div>
          <p className="text-xs text-slate-600">
            {analysis.strengths.length} strengths identified,{' '}
            {analysis.critical_fixes.length} critical issues
          </p>
        </div>
      </div>

      {/* Score breakdown chart */}
      {breakdownData.length > 0 && (
        <div>
          <p className="text-sm font-medium text-slate-900 mb-2">Score Breakdown</p>
          <ResponsiveContainer width="100%" height={180}>
            <BarChart
              data={breakdownData}
              layout="vertical"
              margin={{ left: 8, right: 16, top: 0, bottom: 0 }}
            >
              <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
              <YAxis
                type="category"
                dataKey="name"
                width={120}
                tick={{ fontSize: 11 }}
              />
              <Tooltip
                formatter={(v: number) => [`${v}`, 'Score']}
                contentStyle={{ fontSize: 11 }}
              />
              <Bar dataKey="value" radius={[0, 3, 3, 0]}>
                {breakdownData.map((entry, index) => (
                  <Cell key={index} fill={getBarColor(entry.value)} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Strengths */}
      {analysis.strengths.length > 0 && (
        <div>
          <p className="text-sm font-medium text-slate-900 mb-2">Strengths</p>
          <ul className="space-y-1">
            {analysis.strengths.map((s, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
                <CheckCircle className="w-3.5 h-3.5 text-green-500 mt-0.5 shrink-0" />
                {s}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Critical fixes */}
      {analysis.critical_fixes.length > 0 && (
        <div>
          <p className="text-sm font-medium text-slate-900 mb-2">Critical Issues</p>
          <ul className="space-y-1">
            {analysis.critical_fixes.map((fix, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
                <XCircle className="w-3.5 h-3.5 text-red-500 mt-0.5 shrink-0" />
                {fix}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Keyword gaps */}
      {analysis.keyword_gaps.length > 0 && (
        <div>
          <p className="text-sm font-medium text-slate-900 mb-2">Keyword Gaps</p>
          <div className="flex flex-wrap gap-1.5">
            {analysis.keyword_gaps.map((kw, i) => (
              <Badge key={i} variant="warning">
                {kw}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Format issues */}
      {analysis.format_issues.length > 0 && (
        <div>
          <p className="text-sm font-medium text-slate-900 mb-2">Format Issues</p>
          <ul className="space-y-1">
            {analysis.format_issues.map((issue, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
                <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                {issue}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {analysis.recommendations.length > 0 && (
        <div>
          <p className="text-sm font-medium text-slate-900 mb-2">Recommendations</p>
          <ol className="space-y-1 list-none">
            {analysis.recommendations.map((rec, i) => (
              <li key={i} className="flex items-start gap-2 text-xs text-slate-700">
                <span className="text-xs font-medium text-indigo-600 shrink-0">
                  {i + 1}.
                </span>
                {rec}
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  )
}
