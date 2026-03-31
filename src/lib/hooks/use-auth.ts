'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { SessionManager } from '@/lib/auth/session'
import { AuthAPI } from '@/lib/api/auth'
import type { UserResponse } from '@/lib/types/api'

interface UseAuthReturn {
  user: UserResponse | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (data: {
    email: string
    password: string
    full_name?: string
  }) => Promise<void>
}

export function useAuth(): UseAuthReturn {
  const [user, setUser] = useState<UserResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const router = useRouter()

  useEffect(() => {
    const storedUser = SessionManager.getStoredUser()
    const token = SessionManager.getAccessToken()
    if (storedUser && token && !SessionManager.isTokenExpired()) {
      setUser(storedUser)
    }
    setIsLoading(false)
  }, [])

  const login = useCallback(
    async (email: string, password: string): Promise<void> => {
      const tokenResponse = await AuthAPI.login(email, password)
      SessionManager.setTokens(
        tokenResponse.access_token,
        tokenResponse.refresh_token,
        tokenResponse.expires_in
      )
      // Fetch user info — store minimal info from token or fetch separately
      // Since no /me endpoint, we store what we know from login
      const partialUser: UserResponse = {
        id: '',
        email,
        full_name: null,
        is_active: true,
        is_verified: true,
        subscription_tier: 'free',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      SessionManager.setStoredUser(partialUser)
      setUser(partialUser)
      router.push('/dashboard')
    },
    [router]
  )

  const logout = useCallback(async (): Promise<void> => {
    try {
      await AuthAPI.logout()
    } catch {
      // Ignore logout errors
    } finally {
      SessionManager.clearTokens()
      setUser(null)
      router.push('/login')
    }
  }, [router])

  const register = useCallback(
    async (data: { email: string; password: string; full_name?: string }): Promise<void> => {
      await AuthAPI.register(data)
      // Auto login after registration
      const tokenResponse = await AuthAPI.login(data.email, data.password)
      SessionManager.setTokens(
        tokenResponse.access_token,
        tokenResponse.refresh_token,
        tokenResponse.expires_in
      )
      const partialUser: UserResponse = {
        id: '',
        email: data.email,
        full_name: data.full_name ?? null,
        is_active: true,
        is_verified: false,
        subscription_tier: 'free',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      SessionManager.setStoredUser(partialUser)
      setUser(partialUser)
      router.push('/dashboard')
    },
    [router]
  )

  return {
    user,
    isLoading,
    isAuthenticated: !!user && !!SessionManager.getAccessToken(),
    login,
    logout,
    register,
  }
}
