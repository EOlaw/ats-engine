'use client'

import React from 'react'
import { usePathname } from 'next/navigation'
import { Sidebar } from '@/components/layout/sidebar'
import { Header } from '@/components/layout/header'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface AppShellProps {
  title: string
  breadcrumbs?: BreadcrumbItem[]
  actions?: React.ReactNode
  children: React.ReactNode
}

export function AppShell({
  title,
  breadcrumbs,
  actions,
  children,
}: AppShellProps): React.ReactElement {
  const pathname = usePathname()

  return (
    <div className="flex min-h-screen bg-slate-50">
      <Sidebar currentPath={pathname} />
      <div className="flex flex-col flex-1 min-w-0">
        <Header
          title={title}
          breadcrumbs={breadcrumbs}
          actions={actions}
        />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}
