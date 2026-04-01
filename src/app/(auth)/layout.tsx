import React from 'react'

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode
}): React.ReactElement {
  return (
    <div className="min-h-screen bg-slate-50 flex items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <span className="text-sm font-semibold text-slate-900 tracking-tight">ATS Engine</span>
        </div>
        {children}
      </div>
    </div>
  )
}
