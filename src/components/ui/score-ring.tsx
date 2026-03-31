import React from 'react'
import cn from '@/lib/utils/cn'

interface ScoreRingProps {
  score: number
  label?: string
  size?: 'sm' | 'md' | 'lg'
  className?: string
}

function getScoreColor(score: number): string {
  if (score >= 80) return '#16a34a'
  if (score >= 60) return '#d97706'
  return '#dc2626'
}

const sizeDimensions = {
  sm: { dim: 56, strokeWidth: 4 },
  md: { dim: 80, strokeWidth: 6 },
  lg: { dim: 110, strokeWidth: 7 },
}

export function ScoreRing({
  score,
  label,
  size = 'md',
  className,
}: ScoreRingProps): React.ReactElement {
  const { dim, strokeWidth } = sizeDimensions[size]
  const radius = (dim - strokeWidth * 2) / 2
  const circumference = 2 * Math.PI * radius
  const clamped = Math.min(100, Math.max(0, score))
  const offset = circumference - (clamped / 100) * circumference
  const color = getScoreColor(clamped)
  const center = dim / 2

  return (
    <div className={cn('inline-flex flex-col items-center gap-1', className)}>
      <div className="relative" style={{ width: dim, height: dim }}>
        <svg
          width={dim}
          height={dim}
          viewBox={`0 0 ${dim} ${dim}`}
          className="-rotate-90"
          aria-hidden="true"
        >
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#e2e8f0"
            strokeWidth={strokeWidth}
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke={color}
            strokeWidth={strokeWidth}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
            className="transition-all duration-700 ease-out"
          />
        </svg>
        <div
          className="absolute inset-0 flex items-center justify-center"
          aria-label={`Score: ${Math.round(clamped)}`}
        >
          <span
            className="text-sm font-semibold tabular-nums"
            style={{ color }}
          >
            {Math.round(clamped)}
          </span>
        </div>
      </div>
      {label && (
        <span className="text-xs text-slate-500">{label}</span>
      )}
    </div>
  )
}
