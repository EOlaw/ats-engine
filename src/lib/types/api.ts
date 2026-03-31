// Enums
export type ResumeStatus =
  | 'pending'
  | 'parsing'
  | 'parsed'
  | 'scoring'
  | 'scored'
  | 'optimizing'
  | 'optimized'
  | 'error'

export type FileType = 'pdf' | 'docx'

export type SubscriptionTier = 'free' | 'pro' | 'enterprise'

export type ProcessingMode =
  | 'extract_only'
  | 'extract_and_analyze'
  | 'full_optimization'

export type TemplateEnum =
  | 'modern_clean'
  | 'executive_classic'
  | 'tech_minimal'
  | 'creative_bold'
  | 'ats_optimized'
  | 'academic'

export type ExportFormat = 'pdf' | 'docx'

// Auth
export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface UserResponse {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  is_verified: boolean
  subscription_tier: SubscriptionTier
  created_at: string
  updated_at: string
}

// Resume Upload
export interface ResumeUploadResponse {
  resume_id: string
  status: ResumeStatus
  original_filename: string
  message: string
}

export interface ResumeStatusResponse {
  resume_id: string
  status: ResumeStatus
  ats_score: number | null
  error_message: string | null
  updated_at: string
}

// Extracted data structures
export interface PersonalInfo {
  full_name: string | null
  email: string | null
  phone: string | null
  location: string | null
  linkedin_url: string | null
  github_url: string | null
  portfolio_url: string | null
  summary: string | null
}

export interface WorkExperience {
  company: string | null
  title: string | null
  location: string | null
  start_date: string | null
  end_date: string | null
  is_current: boolean
  bullets: string[]
  technologies: string[]
}

export interface Education {
  institution: string | null
  degree: string | null
  field_of_study: string | null
  start_date: string | null
  end_date: string | null
  gpa: string | null
  honors: string[]
}

export interface ExtractedResume {
  personal_info: PersonalInfo
  skills: {
    technical: string[]
    soft: string[]
    languages: string[]
    tools: string[]
    certifications_mentioned: string[]
  }
  work_experience: WorkExperience[]
  education: Education[]
  certifications: unknown[]
  projects: unknown[]
  extraction_confidence: number
  raw_sections_found: string[]
}

export interface ATSAnalysis {
  score_estimate: number
  score_breakdown: Record<string, number>
  strengths: string[]
  weaknesses: string[]
  critical_fixes: string[]
  keyword_gaps: string[]
  format_issues: string[]
  quantification_score: number
  action_verb_score: number
  recommendations: string[]
}

export interface ResumeProcessResponse {
  id: string
  user_id: string
  original_filename: string
  file_type: FileType
  status: ResumeStatus
  ats_score: number | null
  extracted_data: ExtractedResume | null
  ats_analysis: ATSAnalysis | null
  optimized_content: unknown | null
  error_message: string | null
  created_at: string
  updated_at: string
}

// Tailoring
export interface JobTailoringRequest {
  resume_id: string
  job_title: string
  job_description: string
}

export interface TailoredResumeResponse {
  job_id: string
  resume_id: string
  job_title: string
  match_score: number | null
  tailored_data: unknown | null
  created_at: string
  updated_at: string
}

// Export
export interface ExportRequest {
  resume_id: string
  template_name: TemplateEnum
  format: ExportFormat
  job_id?: string
  use_optimized: boolean
}

export interface ExportResponse {
  export_id: string
  resume_id: string
  template_name: string
  format: ExportFormat
  download_url: string
  file_path: string
  created_at: string
}

// Error
export interface APIError {
  detail: string
  error_code?: string
}
