'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { SessionManager } from '@/lib/auth/session'
import { Spinner } from '@/components/ui/spinner'

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}): React.ReactElement {
  const router = useRouter()

  useEffect(() => {
    const token = SessionManager.getAccessToken()
    if (!token || SessionManager.isTokenExpired()) {
      router.replace('/login')
    }
  }, [router])

  const token = SessionManager.getAccessToken()
  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50">
        <Spinner size="md" />
      </div>
    )
  }

  return <>{children}</>
}
