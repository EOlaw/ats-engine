'use client'

import React, { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, FileText, X, CheckCircle } from 'lucide-react'
import { toast } from 'sonner'
import { ResumeAPI } from '@/lib/api/resume'
import { PROCESSING_MODES } from '@/lib/constants'
import { Button } from '@/components/ui/button'
import cn from '@/lib/utils/cn'
import type { ProcessingMode } from '@/lib/types/api'

interface UploadZoneProps {
  onSuccess: (resumeId: string) => void
}

export function UploadZone({ onSuccess }: UploadZoneProps): React.ReactElement {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [mode, setMode] = useState<ProcessingMode>('extract_and_analyze')
  const [isUploading, setIsUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState<string | null>(null)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0])
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive, fileRejections } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024,
  })

  const handleUpload = async (): Promise<void> => {
    if (!selectedFile) return
    setIsUploading(true)
    setUploadProgress('Uploading file...')
    try {
      const response = await ResumeAPI.upload(selectedFile, mode)
      setUploadProgress('Upload complete!')
      toast.success('Resume uploaded successfully')
      onSuccess(response.resume_id)
    } catch (err: unknown) {
      const msg =
        err instanceof Error ? err.message : 'Upload failed. Please try again.'
      toast.error(msg)
      setUploadProgress(null)
    } finally {
      setIsUploading(false)
    }
  }

  const removeFile = (): void => {
    setSelectedFile(null)
    setUploadProgress(null)
  }

  return (
    <div className="space-y-4">
      {/* Drop zone */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded p-8 text-center cursor-pointer transition-colors duration-150',
          isDragActive
            ? 'border-indigo-400 bg-indigo-50'
            : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50',
          selectedFile && 'border-green-400 bg-green-50'
        )}
      >
        <input {...getInputProps()} />
        {selectedFile ? (
          <div className="flex flex-col items-center gap-2">
            <CheckCircle className="w-8 h-8 text-green-500" />
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-slate-500" />
              <span className="text-xs font-medium text-slate-700">
                {selectedFile.name}
              </span>
              <span className="text-xs text-slate-500">
                ({(selectedFile.size / 1024).toFixed(1)} KB)
              </span>
              <button
                onClick={(e) => {
                  e.stopPropagation()
                  removeFile()
                }}
                className="p-0.5 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-200"
                aria-label="Remove file"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload className="w-8 h-8 text-slate-400" />
            <p className="text-xs font-medium text-slate-700">
              {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume here'}
            </p>
            <p className="text-xs text-slate-500">
              or <span className="text-indigo-600 font-medium">browse files</span>
            </p>
            <p className="text-xs text-slate-400">PDF or DOCX, max 10MB</p>
          </div>
        )}
      </div>

      {/* File rejection errors */}
      {fileRejections.length > 0 && (
        <p className="text-xs text-red-600">
          {fileRejections[0].errors[0].message}
        </p>
      )}

      {/* Processing mode */}
      <div className="space-y-2">
        <p className="text-xs font-medium text-slate-700">Processing Mode</p>
        <div className="space-y-2">
          {PROCESSING_MODES.map((pm) => (
            <label
              key={pm.value}
              className={cn(
                'flex items-start gap-3 p-3 border rounded cursor-pointer transition-colors duration-150',
                mode === pm.value
                  ? 'border-indigo-400 bg-indigo-50'
                  : 'border-slate-200 hover:border-slate-300 hover:bg-slate-50'
              )}
            >
              <input
                type="radio"
                name="mode"
                value={pm.value}
                checked={mode === pm.value}
                onChange={() => setMode(pm.value)}
                className="mt-0.5 accent-indigo-600"
              />
              <div>
                <p className="text-xs font-medium text-slate-900">{pm.label}</p>
                <p className="text-xs text-slate-500">{pm.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Upload status */}
      {uploadProgress && (
        <p className="text-xs text-indigo-600 font-medium">{uploadProgress}</p>
      )}

      {/* Action */}
      <Button
        onClick={handleUpload}
        disabled={!selectedFile || isUploading}
        loading={isUploading}
        variant="primary"
        size="md"
        className="w-full"
      >
        {isUploading ? 'Uploading...' : 'Upload Resume'}
      </Button>
    </div>
  )
}
