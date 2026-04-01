import React from 'react'
import type { LucideIcon } from 'lucide-react'
import cn from '@/lib/utils/cn'

interface StatsCardProps {
  label: string
  value: string | number
  icon: LucideIcon
  trend?: string
  trendUp?: boolean
  className?: string
}

export function StatsCard({
  label,
  value,
  icon: Icon,
  trend,
  trendUp,
  className,
}: StatsCardProps): React.ReactElement {
  return (
    <div
      className={cn(
        'bg-white border border-slate-200 rounded p-4 flex items-start gap-3',
        className
      )}
    >
      <div className="p-2 bg-indigo-50 rounded shrink-0">
        <Icon className="w-3.5 h-3.5 text-indigo-600" />
      </div>
      <div className="min-w-0">
        <p className="text-xs text-slate-500 truncate">{label}</p>
        <p className="text-sm font-semibold text-slate-900 mt-0.5">{value}</p>
        {trend && (
          <p
            className={cn(
              'text-xs mt-0.5',
              trendUp ? 'text-green-600' : 'text-slate-400'
            )}
          >
            {trend}
          </p>
        )}
      </div>
    </div>
  )
}
