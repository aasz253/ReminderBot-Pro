import { useQuery, useMutation, useQueryClient } from "react-query"
import apiClient from "@/lib/api-client"
import type { Subscription, ApiResponse } from "@/types"

export function useSubscription() {
  return useQuery<ApiResponse<Subscription>>(
    ["subscription"],
    async () => {
      const response = await apiClient.get("/subscriptions/current")
      return response.data
    }
  )
}

export function usePlans() {
  return useQuery<ApiResponse<any[]>>(
    ["plans"],
    async () => {
      const response = await apiClient.get("/subscriptions/plans")
      return response.data
    }
  )
}

export function useCreateSubscription() {
  const queryClient = useQueryClient()
  return useMutation(
    async (data: { plan_id: string; payment_method: string; payment_details?: any }) => {
      const response = await apiClient.post("/subscriptions", data)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["subscription"])
        queryClient.invalidateQueries(["plans"])
      },
    }
  )
}

export function useCancelSubscription() {
  const queryClient = useQueryClient()
  return useMutation(
    async () => {
      const response = await apiClient.post("/subscriptions/cancel")
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["subscription"])
      },
    }
  )
}
