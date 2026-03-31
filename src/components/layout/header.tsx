import React from 'react'
import cn from '@/lib/utils/cn'

interface BreadcrumbItem {
  label: string
  href?: string
}

interface HeaderProps {
  title: string
  breadcrumbs?: BreadcrumbItem[]
  actions?: React.ReactNode
  className?: string
}

export function Header({
  title,
  breadcrumbs,
  actions,
  className,
}: HeaderProps): React.ReactElement {
  return (
    <header
      className={cn(
        'flex items-center justify-between px-6 py-3 bg-white border-b border-slate-200 shrink-0',
        className
      )}
    >
      <div className="flex flex-col gap-0.5">
        {breadcrumbs && breadcrumbs.length > 0 && (
          <nav className="flex items-center gap-1" aria-label="Breadcrumb">
            {breadcrumbs.map((item, index) => (
              <React.Fragment key={index}>
                {index > 0 && (
                  <span className="text-xs text-slate-400">/</span>
                )}
                {item.href ? (
                  <a
                    href={item.href}
                    className="text-xs text-slate-500 hover:text-slate-700 transition-colors"
                  >
                    {item.label}
                  </a>
                ) : (
                  <span className="text-xs text-slate-500">{item.label}</span>
                )}
              </React.Fragment>
            ))}
          </nav>
        )}
        <h1 className="text-sm font-medium text-slate-900">{title}</h1>
      </div>
      {actions && (
        <div className="flex items-center gap-2">{actions}</div>
      )}
    </header>
  )
}
