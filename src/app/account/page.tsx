'use client'

import React, { useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { AppShell } from '@/components/layout/shell'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/lib/hooks/use-auth'

const profileSchema = z.object({
  full_name: z.string().optional(),
})

const passwordSchema = z
  .object({
    current_password: z.string().min(1, 'Required'),
    new_password: z
      .string()
      .min(8, 'At least 8 characters')
      .regex(/[A-Z]/, 'Must contain uppercase')
      .regex(/[a-z]/, 'Must contain lowercase')
      .regex(/[0-9]/, 'Must contain digit'),
    confirm_password: z.string(),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: 'Passwords do not match',
    path: ['confirm_password'],
  })

type ProfileValues = z.infer<typeof profileSchema>
type PasswordValues = z.infer<typeof passwordSchema>

export default function AccountPage(): React.ReactElement {
  const { user, logout } = useAuth()
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  const profileForm = useForm<ProfileValues>({
    resolver: zodResolver(profileSchema),
    defaultValues: { full_name: user?.full_name ?? '' },
  })

  const passwordForm = useForm<PasswordValues>({
    resolver: zodResolver(passwordSchema),
  })

  const onProfileSubmit = async (_values: ProfileValues): Promise<void> => {
    // Profile update endpoint not yet implemented — show info toast
    toast.info('Profile update coming soon')
  }

  const onPasswordSubmit = async (_values: PasswordValues): Promise<void> => {
    toast.info('Password change coming soon')
    passwordForm.reset()
  }

  return (
    <AppShell title="Account Settings">
      <div className="max-w-lg space-y-6">
        {/* Profile section */}
        <div className="bg-white border border-slate-200 rounded p-5 space-y-4">
          <p className="text-xs font-semibold text-slate-900">Profile</p>

          <div className="space-y-1">
            <p className="text-xs text-slate-500">Email</p>
            <p className="text-xs font-medium text-slate-900">{user?.email}</p>
            <p className="text-xs text-slate-400">Email cannot be changed</p>
          </div>

          <div className="space-y-1">
            <p className="text-xs text-slate-500">Plan</p>
            <p className="text-xs font-medium text-slate-900 capitalize">{user?.subscription_tier}</p>
          </div>

          <form onSubmit={profileForm.handleSubmit(onProfileSubmit)} className="space-y-3">
            <Input
              label="Full Name"
              placeholder="Jane Smith"
              error={profileForm.formState.errors.full_name?.message}
              {...profileForm.register('full_name')}
            />
            <Button
              type="submit"
              variant="secondary"
              size="sm"
              loading={profileForm.formState.isSubmitting}
            >
              Update Profile
            </Button>
          </form>
        </div>

        {/* Password section */}
        <div className="bg-white border border-slate-200 rounded p-5 space-y-4">
          <p className="text-xs font-semibold text-slate-900">Change Password</p>
          <form onSubmit={passwordForm.handleSubmit(onPasswordSubmit)} className="space-y-3">
            <Input
              label="Current Password"
              type="password"
              placeholder="••••••••"
              error={passwordForm.formState.errors.current_password?.message}
              {...passwordForm.register('current_password')}
            />
            <Input
              label="New Password"
              type="password"
              placeholder="••••••••"
              hint="8+ chars, uppercase, lowercase, number"
              error={passwordForm.formState.errors.new_password?.message}
              {...passwordForm.register('new_password')}
            />
            <Input
              label="Confirm New Password"
              type="password"
              placeholder="••••••••"
              error={passwordForm.formState.errors.confirm_password?.message}
              {...passwordForm.register('confirm_password')}
            />
            <Button
              type="submit"
              variant="secondary"
              size="sm"
              loading={passwordForm.formState.isSubmitting}
            >
              Change Password
            </Button>
          </form>
        </div>

        {/* Danger zone */}
        <div className="bg-white border border-red-200 rounded p-5 space-y-3">
          <p className="text-xs font-semibold text-red-700">Danger Zone</p>
          <p className="text-xs text-slate-500">
            Deleting your account is permanent and cannot be undone. All resumes and data will be removed.
          </p>
          {showDeleteConfirm ? (
            <div className="flex gap-2">
              <Button
                variant="danger"
                size="sm"
                onClick={() => {
                  toast.error('Account deletion coming soon')
                  setShowDeleteConfirm(false)
                }}
              >
                Yes, Delete My Account
              </Button>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </Button>
            </div>
          ) : (
            <Button
              variant="danger"
              size="sm"
              onClick={() => setShowDeleteConfirm(true)}
            >
              Delete Account
            </Button>
          )}
        </div>
      </div>
    </AppShell>
  )
}
