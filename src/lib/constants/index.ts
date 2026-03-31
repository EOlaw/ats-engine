import type { ProcessingMode, ResumeStatus, TemplateEnum, ExportFormat } from '@/lib/types/api'

export const API_BASE = '/api/v1'

export const PROCESSING_MODES: Array<{ label: string; value: ProcessingMode; description: string }> = [
  {
    label: 'Extract Only',
    value: 'extract_only',
    description: 'Parse and extract resume data without analysis',
  },
  {
    label: 'Extract & Analyze',
    value: 'extract_and_analyze',
    description: 'Extract data and compute ATS score with feedback',
  },
  {
    label: 'Full Optimization',
    value: 'full_optimization',
    description: 'Extract, analyze, and generate optimized content',
  },
]

export const TEMPLATE_OPTIONS: Array<{ label: string; value: TemplateEnum; description: string }> = [
  {
    label: 'Modern Clean',
    value: 'modern_clean',
    description: 'Clean, contemporary layout with a modern aesthetic',
  },
  {
    label: 'Executive Classic',
    value: 'executive_classic',
    description: 'Traditional professional format for senior roles',
  },
  {
    label: 'Tech Minimal',
    value: 'tech_minimal',
    description: 'Minimal design optimized for technical roles',
  },
  {
    label: 'Creative Bold',
    value: 'creative_bold',
    description: 'Bold layout for creative and design roles',
  },
  {
    label: 'ATS Optimized',
    value: 'ats_optimized',
    description: 'Maximum ATS compatibility, plain formatting',
  },
  {
    label: 'Academic',
    value: 'academic',
    description: 'CV-style layout for academic and research roles',
  },
]

export const EXPORT_FORMATS: Array<{ label: string; value: ExportFormat }> = [
  { label: 'PDF', value: 'pdf' },
  { label: 'DOCX', value: 'docx' },
]

export const STATUS_LABELS: Record<ResumeStatus, string> = {
  pending: 'Pending',
  parsing: 'Parsing',
  parsed: 'Parsed',
  scoring: 'Scoring',
  scored: 'Scored',
  optimizing: 'Optimizing',
  optimized: 'Optimized',
  error: 'Error',
}

export const STATUS_COLORS: Record<ResumeStatus, string> = {
  pending: 'text-slate-500 bg-slate-100',
  parsing: 'text-blue-600 bg-blue-50',
  parsed: 'text-blue-600 bg-blue-50',
  scoring: 'text-indigo-600 bg-indigo-50',
  scored: 'text-indigo-600 bg-indigo-50',
  optimizing: 'text-purple-600 bg-purple-50',
  optimized: 'text-green-600 bg-green-50',
  error: 'text-red-600 bg-red-50',
}
