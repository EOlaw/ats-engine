import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      // ─── Brand / Primary ────────────────────────────────────────────────────
      colors: {
        brand: {
          50:  '#eef2ff',
          100: '#e0e7ff',
          200: '#c7d2fe',
          300: '#a5b4fc',
          400: '#818cf8',
          500: '#6366f1',
          600: '#4f46e5',
          700: '#4338ca',
          800: '#3730a3',
          900: '#312e81',
          950: '#1e1b4b',
        },

        // ─── Semantic Surfaces ───────────────────────────────────────────────
        surface: {
          DEFAULT: '#ffffff',
          muted:   '#f8fafc',
          subtle:  '#f1f5f9',
          raised:  '#ffffff',
          overlay: 'rgba(15, 23, 42, 0.5)',
        },

        // ─── Semantic Borders ────────────────────────────────────────────────
        border: {
          DEFAULT: '#e2e8f0',
          muted:   '#f1f5f9',
          strong:  '#cbd5e1',
        },

        // ─── Success ─────────────────────────────────────────────────────────
        success: {
          50:  '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
        },

        // ─── Warning ─────────────────────────────────────────────────────────
        warning: {
          50:  '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f',
        },

        // ─── Danger ──────────────────────────────────────────────────────────
        danger: {
          50:  '#fff1f2',
          100: '#ffe4e6',
          200: '#fecdd3',
          300: '#fda4af',
          400: '#fb7185',
          500: '#f43f5e',
          600: '#e11d48',
          700: '#be123c',
          800: '#9f1239',
          900: '#881337',
        },

        // ─── Info ─────────────────────────────────────────────────────────────
        info: {
          50:  '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
        },

        // ─── ATS Score Tiers ─────────────────────────────────────────────────
        score: {
          excellent: '#16a34a',
          good:      '#65a30d',
          fair:      '#d97706',
          poor:      '#dc2626',
        },
      },

      // ─── Typography ──────────────────────────────────────────────────────────
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Fira Mono', 'Roboto Mono', 'monospace'],
      },

      fontSize: {
        '2xs': ['0.6875rem', { lineHeight: '1rem' }],
        xs:    ['0.75rem',   { lineHeight: '1.125rem' }],
        sm:    ['0.8125rem', { lineHeight: '1.25rem' }],
        base:  ['0.875rem',  { lineHeight: '1.375rem' }],
        md:    ['0.9375rem', { lineHeight: '1.5rem' }],
        lg:    ['1rem',      { lineHeight: '1.5rem' }],
        xl:    ['1.125rem',  { lineHeight: '1.625rem' }],
        '2xl': ['1.25rem',   { lineHeight: '1.75rem' }],
        '3xl': ['1.5rem',    { lineHeight: '2rem' }],
        '4xl': ['1.875rem',  { lineHeight: '2.25rem' }],
      },

      fontWeight: {
        normal:   '400',
        medium:   '500',
        semibold: '600',
        bold:     '700',
      },

      letterSpacing: {
        tighter: '-0.03em',
        tight:   '-0.015em',
        normal:  '0em',
        wide:    '0.02em',
        wider:   '0.05em',
        widest:  '0.1em',
      },

      // ─── Spacing ─────────────────────────────────────────────────────────────
      spacing: {
        '4.5': '1.125rem',
        '5.5': '1.375rem',
        '6.5': '1.625rem',
        '7.5': '1.875rem',
        '13':  '3.25rem',
        '15':  '3.75rem',
        '18':  '4.5rem',
        '22':  '5.5rem',
        '26':  '6.5rem',
        '30':  '7.5rem',
        '52':  '13rem',
        '56':  '14rem',
        '60':  '15rem',
        '68':  '17rem',
        '72':  '18rem',
        '76':  '19rem',
        '80':  '20rem',
        '88':  '22rem',
        '96':  '24rem',
        '104': '26rem',
        '112': '28rem',
        '120': '30rem',
        '128': '32rem',
      },

      // ─── Layout ───────────────────────────────────────────────────────────────
      maxWidth: {
        '8xl':  '88rem',
        '9xl':  '96rem',
        'prose': '65ch',
      },

      minHeight: {
        screen: '100dvh',
      },

      // ─── Borders ─────────────────────────────────────────────────────────────
      borderRadius: {
        'none': '0',
        'xs':   '0.125rem',
        'sm':   '0.1875rem',
        DEFAULT: '0.25rem',
        'md':   '0.375rem',
        'lg':   '0.5rem',
        'xl':   '0.75rem',
        '2xl':  '1rem',
        '3xl':  '1.5rem',
        'full': '9999px',
      },

      // ─── Shadows ─────────────────────────────────────────────────────────────
      boxShadow: {
        'xs':    '0 1px 2px 0 rgb(0 0 0 / 0.04)',
        'sm':    '0 1px 3px 0 rgb(0 0 0 / 0.07), 0 1px 2px -1px rgb(0 0 0 / 0.05)',
        DEFAULT: '0 2px 6px -1px rgb(0 0 0 / 0.08), 0 2px 4px -2px rgb(0 0 0 / 0.06)',
        'md':    '0 4px 10px -2px rgb(0 0 0 / 0.10), 0 2px 4px -2px rgb(0 0 0 / 0.06)',
        'lg':    '0 8px 20px -4px rgb(0 0 0 / 0.12), 0 4px 8px -4px rgb(0 0 0 / 0.08)',
        'xl':    '0 16px 36px -6px rgb(0 0 0 / 0.14), 0 8px 16px -6px rgb(0 0 0 / 0.10)',
        '2xl':   '0 24px 48px -12px rgb(0 0 0 / 0.20)',
        'inner': 'inset 0 1px 3px 0 rgb(0 0 0 / 0.06)',
        'brand': '0 4px 14px 0 rgb(99 102 241 / 0.30)',
        'none':  'none',
      },

      // ─── Ring ────────────────────────────────────────────────────────────────
      ringWidth: {
        DEFAULT: '2px',
        '1': '1px',
        '3': '3px',
      },

      ringOffsetWidth: {
        DEFAULT: '2px',
      },

      // ─── Animations & Keyframes ──────────────────────────────────────────────
      keyframes: {
        'fade-in': {
          from: { opacity: '0' },
          to:   { opacity: '1' },
        },
        'fade-out': {
          from: { opacity: '1' },
          to:   { opacity: '0' },
        },
        'slide-up': {
          from: { opacity: '0', transform: 'translateY(6px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-down': {
          from: { opacity: '0', transform: 'translateY(-6px)' },
          to:   { opacity: '1', transform: 'translateY(0)' },
        },
        'slide-in-right': {
          from: { opacity: '0', transform: 'translateX(12px)' },
          to:   { opacity: '1', transform: 'translateX(0)' },
        },
        'scale-in': {
          from: { opacity: '0', transform: 'scale(0.95)' },
          to:   { opacity: '1', transform: 'scale(1)' },
        },
        'shimmer': {
          from: { backgroundPosition: '-200% 0' },
          to:   { backgroundPosition: '200% 0' },
        },
        'spin-slow': {
          from: { transform: 'rotate(0deg)' },
          to:   { transform: 'rotate(360deg)' },
        },
        'pulse-soft': {
          '0%, 100%': { opacity: '1' },
          '50%':      { opacity: '0.6' },
        },
        'progress-indeterminate': {
          from: { left: '-40%', width: '40%' },
          to:   { left: '100%', width: '40%' },
        },
        'score-fill': {
          from: { 'stroke-dashoffset': '251.2' },
        },
        'bounce-subtle': {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%':      { transform: 'translateY(-3px)' },
        },
      },

      animation: {
        'fade-in':        'fade-in 150ms ease-out',
        'fade-out':       'fade-out 150ms ease-in',
        'slide-up':       'slide-up 200ms ease-out',
        'slide-down':     'slide-down 200ms ease-out',
        'slide-in-right': 'slide-in-right 200ms ease-out',
        'scale-in':       'scale-in 150ms ease-out',
        'shimmer':        'shimmer 2s linear infinite',
        'spin-slow':      'spin-slow 2s linear infinite',
        'pulse-soft':     'pulse-soft 2s ease-in-out infinite',
        'bounce-subtle':  'bounce-subtle 1.5s ease-in-out infinite',
        'progress':       'progress-indeterminate 1.5s ease-in-out infinite',
      },

      // ─── Transitions ─────────────────────────────────────────────────────────
      transitionTimingFunction: {
        'smooth': 'cubic-bezier(0.4, 0, 0.2, 1)',
        'spring': 'cubic-bezier(0.34, 1.56, 0.64, 1)',
        'bounce': 'cubic-bezier(0.68, -0.55, 0.265, 1.55)',
      },

      transitionDuration: {
        '50':  '50ms',
        '75':  '75ms',
        '100': '100ms',
        '150': '150ms',
        '200': '200ms',
        '250': '250ms',
        '300': '300ms',
        '400': '400ms',
        '500': '500ms',
      },

      // ─── Z-Index ──────────────────────────────────────────────────────────────
      zIndex: {
        'sidebar':  '40',
        'header':   '50',
        'dropdown': '60',
        'modal':    '70',
        'toast':    '80',
        'tooltip':  '90',
      },

      // ─── Backdrop ────────────────────────────────────────────────────────────
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
      },

      // ─── Grid ────────────────────────────────────────────────────────────────
      gridTemplateColumns: {
        'sidebar': '13rem 1fr',
        'sidebar-collapsed': '3.5rem 1fr',
        'dashboard': 'repeat(auto-fill, minmax(260px, 1fr))',
      },
    },
  },
  plugins: [],
}

export default config
