import React from 'react'
import { CheckCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import cn from '@/lib/utils/cn'

interface PlanCardProps {
  name: string
  price: string
  period?: string
  description: string
  features: string[]
  isCurrent: boolean
  isPopular?: boolean
  onUpgrade?: () => void
}

export function PlanCard({
  name,
  price,
  period = '/mo',
  description,
  features,
  isCurrent,
  isPopular,
  onUpgrade,
}: PlanCardProps): React.ReactElement {
  return (
    <div
      className={cn(
        'bg-white border rounded p-5 flex flex-col gap-4 relative',
        isCurrent
          ? 'border-indigo-400 ring-1 ring-indigo-400'
          : 'border-slate-200'
      )}
    >
      {isPopular && !isCurrent && (
        <span className="absolute -top-2.5 left-4 px-2 py-0.5 bg-indigo-600 text-white text-xs font-medium rounded">
          Popular
        </span>
      )}
      {isCurrent && (
        <span className="absolute -top-2.5 left-4 px-2 py-0.5 bg-green-600 text-white text-xs font-medium rounded">
          Current Plan
        </span>
      )}

      <div>
        <p className="text-xs font-semibold text-slate-900">{name}</p>
        <div className="flex items-baseline gap-0.5 mt-1">
          <span className="text-lg font-bold text-slate-900">{price}</span>
          {price !== 'Free' && (
            <span className="text-xs text-slate-500">{period}</span>
          )}
        </div>
        <p className="text-xs text-slate-500 mt-1">{description}</p>
      </div>

      <ul className="space-y-1.5 flex-1">
        {features.map((feature, i) => (
          <li key={i} className="flex items-start gap-2">
            <CheckCircle className="w-3.5 h-3.5 text-green-500 mt-0.5 shrink-0" />
            <span className="text-xs text-slate-700">{feature}</span>
          </li>
        ))}
      </ul>

      <Button
        variant={isCurrent ? 'secondary' : 'primary'}
        size="sm"
        className="w-full"
        disabled={isCurrent}
        onClick={onUpgrade}
      >
        {isCurrent ? 'Current Plan' : 'Upgrade'}
      </Button>
    </div>
  )
}
