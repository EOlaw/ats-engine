'use client'

import React from 'react'
import Link from 'next/link'
import {
  LayoutDashboard,
  FileText,
  Upload,
  CreditCard,
  User,
  LogOut,
} from 'lucide-react'
import cn from '@/lib/utils/cn'
import { useAuth } from '@/lib/hooks/use-auth'

interface NavItem {
  label: string
  href: string
  icon: React.ComponentType<{ className?: string }>
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { label: 'My Resumes', href: '/resume/history', icon: FileText },
  { label: 'Upload', href: '/resume/upload', icon: Upload },
  { label: 'Billing', href: '/billing', icon: CreditCard },
  { label: 'Account', href: '/account', icon: User },
]

interface SidebarProps {
  currentPath: string
}

export function Sidebar({ currentPath }: SidebarProps): React.ReactElement {
  const { user, logout } = useAuth()

  const isActive = (href: string): boolean => {
    if (href === '/dashboard') return currentPath === '/dashboard'
    return currentPath.startsWith(href)
  }

  return (
    <aside className="flex flex-col w-52 min-h-screen bg-slate-900 border-r border-slate-800 shrink-0">
      {/* Logo */}
      <div className="px-4 py-4 border-b border-slate-800">
        <span className="text-sm font-semibold text-white tracking-tight">
          ATS Engine
        </span>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-2 py-3 space-y-0.5">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon
          const active = isActive(item.href)
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'flex items-center gap-2.5 px-3 py-2 rounded text-xs font-medium transition-colors duration-150',
                active
                  ? 'bg-indigo-600 text-white'
                  : 'text-slate-400 hover:text-white hover:bg-slate-800'
              )}
            >
              <Icon className="w-3.5 h-3.5 shrink-0" />
              {item.label}
            </Link>
          )
        })}
      </nav>

      {/* User section */}
      <div className="px-3 py-3 border-t border-slate-800 space-y-2">
        <div className="px-2">
          <p className="text-xs text-slate-500 truncate">
            {user?.email ?? 'Loading...'}
          </p>
          {user?.subscription_tier && (
            <p className="text-xs text-slate-600 capitalize">
              {user.subscription_tier}
            </p>
          )}
        </div>
        <button
          onClick={logout}
          className="flex items-center gap-2 px-3 py-1.5 w-full rounded text-xs font-medium text-slate-400 hover:text-white hover:bg-slate-800 transition-colors duration-150"
        >
          <LogOut className="w-3.5 h-3.5" />
          Sign out
        </button>
      </div>
    </aside>
  )
}
