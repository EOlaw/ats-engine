'use client'

import React from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Wand2, CheckCircle } from 'lucide-react'
import { Modal } from '@/components/ui/modal'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useTailorResume } from '@/lib/hooks/use-resume'
import type { TailoredResumeResponse } from '@/lib/types/api'

const schema = z.object({
  job_title: z.string().min(2, 'Job title is required').max(200),
  job_description: z.string().min(50, 'Job description must be at least 50 characters').max(20000),
})

type FormValues = z.infer<typeof schema>

interface TailorModalProps {
  isOpen: boolean
  onClose: () => void
  resumeId: string
  onSuccess: (result: TailoredResumeResponse) => void
}

export function TailorModal({
  isOpen,
  onClose,
  resumeId,
  onSuccess,
}: TailorModalProps): React.ReactElement {
  const mutation = useTailorResume()

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (values: FormValues): Promise<void> => {
    try {
      const result = await mutation.mutateAsync({
        id: resumeId,
        job_title: values.job_title,
        job_description: values.job_description,
      })
      toast.success('Resume tailored successfully')
      onSuccess(result)
      reset()
    } catch {
      toast.error('Tailoring failed. Please try again.')
    }
  }

  const handleClose = (): void => {
    if (!mutation.isPending) {
      reset()
      mutation.reset()
      onClose()
    }
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Tailor Resume to Job">
      {mutation.isSuccess && mutation.data ? (
        <div className="space-y-4">
          <div className="flex items-center gap-2 p-3 bg-green-50 border border-green-200 rounded">
            <CheckCircle className="w-4 h-4 text-green-600 shrink-0" />
            <div>
              <p className="text-xs font-medium text-green-800">Tailoring complete</p>
              {mutation.data.match_score !== null && (
                <p className="text-xs text-green-700">
                  Match score: <strong>{Math.round(mutation.data.match_score)}%</strong>
                </p>
              )}
            </div>
          </div>
          <div className="flex justify-end gap-2">
            <Button variant="secondary" size="sm" onClick={handleClose}>
              Close
            </Button>
            <Button
              variant="primary"
              size="sm"
              onClick={() => {
                onSuccess(mutation.data!)
                handleClose()
              }}
            >
              View Tailored Resume
            </Button>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <Input
            label="Job Title"
            placeholder="e.g. Senior Data Analyst"
            error={errors.job_title?.message}
            {...register('job_title')}
          />

          <div className="space-y-1">
            <label className="block text-xs font-medium text-slate-700">
              Job Description
            </label>
            <textarea
              rows={10}
              placeholder="Paste the full job description here..."
              className="w-full px-3 py-2 border border-slate-300 rounded text-xs text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 resize-none"
              {...register('job_description')}
            />
            {errors.job_description && (
              <p className="text-xs text-red-600">{errors.job_description.message}</p>
            )}
          </div>

          <div className="flex justify-end gap-2 pt-1">
            <Button
              type="button"
              variant="secondary"
              size="sm"
              onClick={handleClose}
              disabled={mutation.isPending}
            >
              Cancel
            </Button>
            <Button
              type="submit"
              variant="primary"
              size="sm"
              loading={mutation.isPending}
              className="gap-1.5"
            >
              <Wand2 className="w-3 h-3" />
              {mutation.isPending ? 'Tailoring...' : 'Tailor Resume'}
            </Button>
          </div>
        </form>
      )}
    </Modal>
  )
}
