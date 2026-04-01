'use client'

import React, { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { SessionManager } from '@/lib/auth/session'
import { Spinner } from '@/components/ui/spinner'
import { Button } from '@/components/ui/button'

export default function HomePage(): React.ReactElement {
  const router = useRouter()

  useEffect(() => {
    const token = SessionManager.getAccessToken()
    if (token && !SessionManager.isTokenExpired()) {
      router.replace('/dashboard')
    }
  }, [router])

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center px-4">
      <div className="max-w-md w-full text-center space-y-6">
        <div>
          <h1 className="text-base font-semibold text-white tracking-tight">ATS Engine</h1>
          <p className="text-xs text-slate-400 mt-1">
            Enterprise-grade ATS resume intelligence platform
          </p>
        </div>

        <div className="space-y-2">
          <p className="text-xs text-slate-500">
            Upload resumes, score ATS compatibility, optimize content, and export enterprise-ready documents.
          </p>
        </div>

        <div className="flex flex-col gap-2">
          <Link href="/register">
            <Button variant="primary" size="md" className="w-full">
              Get Started — It&apos;s Free
            </Button>
          </Link>
          <Link href="/login">
            <Button variant="ghost" size="md" className="w-full text-slate-400 hover:text-white">
              Sign In
            </Button>
          </Link>
        </div>

        <div className="grid grid-cols-3 gap-3 pt-2">
          {[
            ['Parse', 'PDF & DOCX extraction'],
            ['Score', 'ATS compatibility analysis'],
            ['Optimize', 'AI-powered rewriting'],
          ].map(([title, desc]) => (
            <div key={title} className="text-center">
              <p className="text-xs font-medium text-white">{title}</p>
              <p className="text-xs text-slate-500 mt-0.5">{desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
