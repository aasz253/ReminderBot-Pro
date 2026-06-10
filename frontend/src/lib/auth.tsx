"use client"

import React, { createContext, useContext, useState, useEffect, useCallback } from "react"
import { deleteCookie, getCookie, setCookie } from "cookies-next"
import apiClient from "@/lib/api-client"
import type { User } from "@/types"

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    try {
      const token = getCookie("access_token")
      if (!token) {
        setIsLoading(false)
        return
      }
      const response = await apiClient.get("/auth/me")
      setUser(response.data.data || response.data)
    } catch {
      deleteCookie("access_token")
      deleteCookie("refresh_token")
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = async (email: string, password: string) => {
    const response = await apiClient.post("/auth/login", { email, password })
    const { access_token, refresh_token, user: userData } = response.data.data || response.data
    setCookie("access_token", access_token, { maxAge: 60 * 15 })
    setCookie("refresh_token", refresh_token, { maxAge: 60 * 60 * 24 * 7 })
    setUser(userData)
  }

  const register = async (name: string, email: string, password: string) => {
    const response = await apiClient.post("/auth/register", { name, email, password })
    const { access_token, refresh_token, user: userData } = response.data.data || response.data
    setCookie("access_token", access_token, { maxAge: 60 * 15 })
    setCookie("refresh_token", refresh_token, { maxAge: 60 * 60 * 24 * 7 })
    setUser(userData)
  }

  const logout = () => {
    deleteCookie("access_token")
    deleteCookie("refresh_token")
    setUser(null)
    if (typeof window !== "undefined") {
      window.location.href = "/"
    }
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

export function protectPage(user: User | null, requiredRole?: string): boolean {
  if (!user) return false
  if (requiredRole && user.role !== requiredRole && user.role !== "superuser") return false
  return true
}

export function hasPermission(user: User | null, permission: string): boolean {
  if (!user) return false
  if (user.role === "superuser") return true
  const permissions: Record<string, string[]> = {
    admin: ["manage_users", "manage_subscriptions", "view_analytics"],
    user: ["create_reminders", "view_own_reminders", "manage_profile"],
  }
  return permissions[user.role]?.includes(permission) ?? false
}
