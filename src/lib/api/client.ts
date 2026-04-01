import axios, {
  type AxiosInstance,
  type AxiosRequestConfig,
  type InternalAxiosRequestConfig,
  type AxiosResponse,
} from 'axios'
import { SessionManager } from '@/lib/auth/session'
import type { TokenResponse } from '@/lib/types/api'

let isRefreshing = false
let failedQueue: Array<{
  resolve: (value: string) => void
  reject: (reason: unknown) => void
}> = []

function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token as string)
    }
  })
  failedQueue = []
}

export class APIClient {
  private axiosInstance: AxiosInstance

  constructor(baseURL: string) {
    this.axiosInstance = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    this.axiosInstance.interceptors.request.use(
      (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
        const token = SessionManager.getAccessToken()
        if (token && config.headers) {
          config.headers['Authorization'] = `Bearer ${token}`
        }
        // For FormData, delete Content-Type so the browser sets multipart/form-data
        // with the correct boundary automatically. Must happen here (after merging)
        // because the instance default `application/json` wins over per-request `undefined`.
        if (config.data instanceof FormData) {
          delete config.headers['Content-Type']
        }
        return config
      },
      (error) => Promise.reject(error)
    )

    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => response,
      async (error) => {
        const originalRequest = error.config as InternalAxiosRequestConfig & {
          _retry?: boolean
        }

        if (error.response?.status === 401 && !originalRequest._retry) {
          if (isRefreshing) {
            return new Promise((resolve, reject) => {
              failedQueue.push({ resolve, reject })
            })
              .then((token) => {
                if (originalRequest.headers) {
                  originalRequest.headers['Authorization'] = `Bearer ${token}`
                }
                return this.axiosInstance(originalRequest)
              })
              .catch((err) => Promise.reject(err))
          }

          originalRequest._retry = true
          isRefreshing = true

          const refreshToken = SessionManager.getRefreshToken()
          if (!refreshToken) {
            SessionManager.clearTokens()
            if (typeof window !== 'undefined') {
              window.location.href = '/login'
            }
            return Promise.reject(error)
          }

          try {
            const response = await axios.post<TokenResponse>(
              '/api/v1/auth/refresh',
              { refresh_token: refreshToken }
            )
            const { access_token, refresh_token, expires_in } = response.data
            SessionManager.setTokens(access_token, refresh_token, expires_in)
            processQueue(null, access_token)
            if (originalRequest.headers) {
              originalRequest.headers['Authorization'] = `Bearer ${access_token}`
            }
            return this.axiosInstance(originalRequest)
          } catch (refreshError) {
            processQueue(refreshError, null)
            SessionManager.clearTokens()
            if (typeof window !== 'undefined') {
              window.location.href = '/login'
            }
            return Promise.reject(refreshError)
          } finally {
            isRefreshing = false
          }
        }

        // Extract a readable message from the error response.
        // Custom app exceptions use { message, error_code } shape.
        // FastAPI Pydantic validation errors use { detail: [...] } shape.
        const data = error.response?.data
        if (data) {
          if (typeof data.message === 'string') {
            return Promise.reject(new Error(data.message))
          }
          const detail = data.detail
          if (detail) {
            const message =
              typeof detail === 'string'
                ? detail
                : Array.isArray(detail)
                ? detail.map((e: { msg: string }) => e.msg).join(', ')
                : 'Request failed'
            return Promise.reject(new Error(message))
          }
        }

        return Promise.reject(error)
      }
    )
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.get<T>(url, config)
    return response.data
  }

  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, data, config)
    return response.data
  }

  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.put<T>(url, data, config)
    return response.data
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.delete<T>(url, config)
    return response.data
  }

  async postForm<T>(url: string, formData: FormData, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.axiosInstance.post<T>(url, formData, config)
    return response.data
  }
}

export const apiClient = new APIClient('/api/v1')
