import type { UserResponse } from '@/lib/types/api'

const ACCESS_TOKEN_KEY = 'ats_access_token'
const REFRESH_TOKEN_KEY = 'ats_refresh_token'
const TOKEN_EXPIRY_KEY = 'ats_token_expiry'
const USER_KEY = 'ats_user'

export class SessionManager {
  static setTokens(access: string, refresh: string, expiresIn: number): void {
    if (typeof window === 'undefined') return
    const expiryTimestamp = Date.now() + expiresIn * 1000
    localStorage.setItem(ACCESS_TOKEN_KEY, access)
    localStorage.setItem(REFRESH_TOKEN_KEY, refresh)
    localStorage.setItem(TOKEN_EXPIRY_KEY, expiryTimestamp.toString())
    // Write cookie so Next.js middleware can read auth state server-side
    const maxAge = expiresIn
    document.cookie = `ats_access_token=${access}; path=/; max-age=${maxAge}; SameSite=Lax`
  }

  static getAccessToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(ACCESS_TOKEN_KEY)
  }

  static getRefreshToken(): string | null {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }

  static clearTokens(): void {
    if (typeof window === 'undefined') return
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(TOKEN_EXPIRY_KEY)
    localStorage.removeItem(USER_KEY)
    // Expire the middleware cookie immediately
    document.cookie = 'ats_access_token=; path=/; max-age=0; SameSite=Lax'
  }

  static isTokenExpired(): boolean {
    if (typeof window === 'undefined') return true
    const expiry = localStorage.getItem(TOKEN_EXPIRY_KEY)
    if (!expiry) return true
    return Date.now() >= parseInt(expiry, 10)
  }

  static getStoredUser(): UserResponse | null {
    if (typeof window === 'undefined') return null
    const raw = localStorage.getItem(USER_KEY)
    if (!raw) return null
    try {
      return JSON.parse(raw) as UserResponse
    } catch {
      return null
    }
  }

  static setStoredUser(user: UserResponse): void {
    if (typeof window === 'undefined') return
    localStorage.setItem(USER_KEY, JSON.stringify(user))
  }
}
