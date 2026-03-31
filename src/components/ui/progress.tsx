import React from 'react'
import cn from '@/lib/utils/cn'

interface ProgressBarProps {
  value: number
  color?: string
  className?: string
  showLabel?: boolean
}

export function ProgressBar({
  value,
  color = 'bg-indigo-600',
  className,
  showLabel = false,
}: ProgressBarProps): React.ReactElement {
  const clamped = Math.min(100, Math.max(0, value))

  return (
    <div className={cn('flex items-center gap-2', className)}>
      <div className="flex-1 bg-slate-100 rounded-full h-1.5 overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500 ease-out',
            color
          )}
          style={{ width: `${clamped}%` }}
        />
      </div>
      {showLabel && (
        <span className="text-xs text-slate-500 w-8 text-right">
          {Math.round(clamped)}%
        </span>
      )}
    </div>
  )
}
