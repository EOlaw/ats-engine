import React, { type ButtonHTMLAttributes } from 'react'
import cn from '@/lib/utils/cn'
import { Spinner } from '@/components/ui/spinner'

type ButtonVariant = 'primary' | 'secondary' | 'ghost' | 'danger'
type ButtonSize = 'sm' | 'md'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant
  size?: ButtonSize
  loading?: boolean
  children: React.ReactNode
}

const variantClasses: Record<ButtonVariant, string> = {
  primary:
    'bg-indigo-600 text-white border border-indigo-600 hover:bg-indigo-700 hover:border-indigo-700 focus:ring-2 focus:ring-indigo-500 focus:ring-offset-1',
  secondary:
    'bg-white text-slate-700 border border-slate-300 hover:bg-slate-50 focus:ring-2 focus:ring-slate-400 focus:ring-offset-1',
  ghost:
    'bg-transparent text-slate-600 border border-transparent hover:bg-slate-100 focus:ring-2 focus:ring-slate-400 focus:ring-offset-1',
  danger:
    'bg-red-600 text-white border border-red-600 hover:bg-red-700 hover:border-red-700 focus:ring-2 focus:ring-red-500 focus:ring-offset-1',
}

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'px-2.5 py-1 text-xs',
  md: 'px-3.5 py-1.5 text-xs',
}

export function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps): React.ReactElement {
  return (
    <button
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center gap-1.5 font-medium rounded transition-colors duration-150 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed',
        variantClasses[variant],
        sizeClasses[size],
        className
      )}
      {...props}
    >
      {loading && <Spinner size="sm" />}
      {children}
    </button>
  )
}
