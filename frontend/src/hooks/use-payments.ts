import { useQuery, useMutation } from "react-query"
import apiClient from "@/lib/api-client"
import type { Payment, PaginatedResponse, ApiResponse, MpesaPaymentInput } from "@/types"

export function usePaymentHistory(page = 1, limit = 10) {
  return useQuery<PaginatedResponse<Payment>>(
    ["payments", page, limit],
    async () => {
      const response = await apiClient.get(`/payments?page=${page}&limit=${limit}`)
      return response.data
    }
  )
}

export function useProcessPayment() {
  return useMutation(
    async (data: {
      plan_id: string
      payment_method: string
      payment_method_id?: string
    }) => {
      const response = await apiClient.post("/payments/process", data)
      return response.data
    }
  )
}

export function useMpesaPayment() {
  return useMutation(
    async (data: MpesaPaymentInput) => {
      const response = await apiClient.post("/payments/mpesa", data)
      return response.data
    }
  )
}
