import { useQuery } from "react-query"
import apiClient from "@/lib/api-client"
import type { Analytics, ProductivityScore, ReminderTrend, CategoryBreakdown, ApiResponse } from "@/types"

export function useDashboardStats() {
  return useQuery<ApiResponse<{
    analytics: Analytics
    productivity: ProductivityScore
    upcoming_reminders: any[]
    trends: ReminderTrend[]
    category_breakdown: CategoryBreakdown[]
  }>>(
    ["dashboard", "stats"],
    async () => {
      const response = await apiClient.get("/dashboard/stats")
      return response.data
    },
    { refetchInterval: 60000 }
  )
}

export function useReminderTrends(period: "daily" | "weekly" | "monthly" = "weekly") {
  return useQuery<ApiResponse<ReminderTrend[]>>(
    ["dashboard", "trends", period],
    async () => {
      const response = await apiClient.get(`/dashboard/trends?period=${period}`)
      return response.data
    }
  )
}

export function useProductivityScore() {
  return useQuery<ApiResponse<ProductivityScore>>(
    ["dashboard", "productivity"],
    async () => {
      const response = await apiClient.get("/dashboard/productivity")
      return response.data
    },
    { refetchInterval: 300000 }
  )
}

export function useCategoryBreakdown() {
  return useQuery<ApiResponse<CategoryBreakdown[]>>(
    ["dashboard", "categories"],
    async () => {
      const response = await apiClient.get("/dashboard/category-breakdown")
      return response.data
    }
  )
}
