'use client'

import React from 'react'
import { AppShell } from '@/components/layout/shell'
import { PlanCard } from '@/components/billing/plan-card'
import { useAuth } from '@/lib/hooks/use-auth'
import { toast } from 'sonner'

const PLANS = [
  {
    name: 'Free',
    tier: 'free' as const,
    price: 'Free',
    description: 'Get started with basic resume analysis',
    features: [
      '3 resume uploads/month',
      'PDF & DOCX parsing',
      'ATS score analysis',
      'Basic extraction',
      'DOCX export',
    ],
  },
  {
    name: 'Pro',
    tier: 'pro' as const,
    price: '$19',
    description: 'For active job seekers',
    features: [
      'Unlimited resume uploads',
      'Full AI optimization pipeline',
      'Job tailoring (unlimited)',
      'All 6 ATS-safe templates',
      'PDF & DOCX export',
      'Priority processing',
    ],
    isPopular: true,
  },
  {
    name: 'Enterprise',
    tier: 'enterprise' as const,
    price: '$49',
    description: 'For teams and staffing agencies',
    features: [
      'Everything in Pro',
      'Team management',
      'Bulk upload & processing',
      'API access',
      'Custom templates',
      'Dedicated support',
    ],
  },
]

export default function BillingPage(): React.ReactElement {
  const { user } = useAuth()
  const currentTier = user?.subscription_tier ?? 'free'

  const handleUpgrade = (tier: string): void => {
    toast.info(`Upgrade to ${tier} — payment integration coming soon.`)
  }

  return (
    <AppShell title="Billing & Plans">
      <div className="max-w-3xl space-y-5">
        <div>
          <p className="text-xs text-slate-500">
            Current plan: <span className="font-medium text-slate-900 capitalize">{currentTier}</span>
          </p>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {PLANS.map((plan) => (
            <PlanCard
              key={plan.tier}
              name={plan.name}
              price={plan.price}
              description={plan.description}
              features={plan.features}
              isCurrent={currentTier === plan.tier}
              isPopular={plan.isPopular}
              onUpgrade={() => handleUpgrade(plan.name)}
            />
          ))}
        </div>

        <div className="bg-slate-50 border border-slate-200 rounded p-4">
          <p className="text-xs font-medium text-slate-700">Need a custom plan?</p>
          <p className="text-xs text-slate-500 mt-0.5">
            Contact us for volume pricing, white-label solutions, or enterprise integrations.
          </p>
        </div>
      </div>
    </AppShell>
  )
}
