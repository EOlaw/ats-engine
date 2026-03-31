import { apiClient } from '@/lib/api/client'
import type { TokenResponse, UserResponse } from '@/lib/types/api'

export class AuthAPI {
  static async register(data: {
    email: string
    password: string
    full_name?: string
  }): Promise<UserResponse> {
    return apiClient.post<UserResponse>('/auth/register', data)
  }

  static async login(email: string, password: string): Promise<TokenResponse> {
    return apiClient.post<TokenResponse>('/auth/login', { email, password })
  }

  static async refresh(refreshToken: string): Promise<TokenResponse> {
    return apiClient.post<TokenResponse>('/auth/refresh', {
      refresh_token: refreshToken,
    })
  }

  static async logout(): Promise<void> {
    return apiClient.post<void>('/auth/logout')
  }
}
