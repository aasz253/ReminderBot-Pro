import axios, { AxiosError, InternalAxiosRequestConfig } from "axios"
import { getCookie, setCookie, deleteCookie } from "cookies-next"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30000,
})

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getCookie("access_token")
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean }

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      try {
        const refreshToken = getCookie("refresh_token")
        if (!refreshToken) {
          deleteCookie("access_token")
          deleteCookie("refresh_token")
          if (typeof window !== "undefined") {
            window.location.href = "/auth/login"
          }
          return Promise.reject(error)
        }

        const response = await axios.post(`${API_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })

        const { access_token, refresh_token: newRefreshToken } = response.data
        setCookie("access_token", access_token, { maxAge: 60 * 15 })
        setCookie("refresh_token", newRefreshToken, { maxAge: 60 * 60 * 24 * 7 })

        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${access_token}`
        }
        return apiClient(originalRequest)
      } catch {
        deleteCookie("access_token")
        deleteCookie("refresh_token")
        if (typeof window !== "undefined") {
          window.location.href = "/auth/login"
        }
        return Promise.reject(error)
      }
    }

    return Promise.reject(error)
  }
)

export default apiClient
