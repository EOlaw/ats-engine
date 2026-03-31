import React from 'react'
import cn from '@/lib/utils/cn'

interface CardProps {
  children: React.ReactNode
  className?: string
}

interface CardHeaderProps {
  children: React.ReactNode
  className?: string
}

interface CardBodyProps {
  children: React.ReactNode
  className?: string
}

interface CardFooterProps {
  children: React.ReactNode
  className?: string
}

export function Card({ children, className }: CardProps): React.ReactElement {
  return (
    <div
      className={cn(
        'bg-white border border-slate-200 rounded overflow-hidden',
        className
      )}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className }: CardHeaderProps): React.ReactElement {
  return (
    <div
      className={cn(
        'px-4 py-3 border-b border-slate-200',
        className
      )}
    >
      {children}
    </div>
  )
}

export function CardBody({ children, className }: CardBodyProps): React.ReactElement {
  return (
    <div className={cn('px-4 py-4', className)}>
      {children}
    </div>
  )
}

export function CardFooter({ children, className }: CardFooterProps): React.ReactElement {
  return (
    <div
      className={cn(
        'px-4 py-3 border-t border-slate-200 bg-slate-50',
        className
      )}
    >
      {children}
    </div>
  )
}
