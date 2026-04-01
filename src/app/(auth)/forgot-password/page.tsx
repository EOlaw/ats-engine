'use client'

import React, { useState } from 'react'
import Link from 'next/link'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Mail } from 'lucide-react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'

const schema = z.object({
  email: z.string().email('Enter a valid email'),
})

type FormValues = z.infer<typeof schema>

export default function ForgotPasswordPage(): React.ReactElement {
  const [submitted, setSubmitted] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (_values: FormValues): Promise<void> => {
    // Simulate API call — endpoint not yet implemented in backend
    await new Promise((r) => setTimeout(r, 800))
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="bg-white border border-slate-200 rounded p-6 shadow-sm text-center space-y-3">
        <div className="flex justify-center">
          <div className="p-3 bg-indigo-50 rounded-full">
            <Mail className="w-5 h-5 text-indigo-600" />
          </div>
        </div>
        <p className="text-xs font-medium text-slate-900">Check your email</p>
        <p className="text-xs text-slate-500">
          If an account exists for that email, you&apos;ll receive a password reset link shortly.
        </p>
        <Link href="/login" className="block text-xs text-indigo-600 hover:text-indigo-700 font-medium mt-2">
          Back to sign in
        </Link>
      </div>
    )
  }

  return (
    <div className="bg-white border border-slate-200 rounded p-6 shadow-sm space-y-5">
      <div>
        <h2 className="text-xs font-semibold text-slate-900">Reset your password</h2>
        <p className="text-xs text-slate-500 mt-0.5">Enter your email to receive a reset link</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-3">
        <Input
          label="Email"
          type="email"
          placeholder="you@example.com"
          error={errors.email?.message}
          {...register('email')}
        />
        <Button
          type="submit"
          variant="primary"
          size="md"
          loading={isSubmitting}
          className="w-full"
        >
          Send Reset Link
        </Button>
      </form>

      <p className="text-xs text-center text-slate-500">
        <Link href="/login" className="text-indigo-600 hover:text-indigo-700 font-medium">
          Back to sign in
        </Link>
      </p>
    </div>
  )
}
