import { useQuery, useMutation, useQueryClient } from "react-query"
import apiClient from "@/lib/api-client"
import type {
  Reminder,
  PaginatedResponse,
  CreateReminderInput,
  UpdateReminderInput,
  ReminderFilters,
  ApiResponse,
} from "@/types"

export function useReminders(filters: ReminderFilters = {}) {
  const params = new URLSearchParams()
  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== "") {
      params.set(key, String(value))
    }
  })

  return useQuery<PaginatedResponse<Reminder>>(
    ["reminders", filters],
    async () => {
      const response = await apiClient.get(`/reminders?${params.toString()}`)
      return response.data
    },
    { keepPreviousData: true }
  )
}

export function useReminder(id: string) {
  return useQuery<ApiResponse<Reminder>>(
    ["reminder", id],
    async () => {
      const response = await apiClient.get(`/reminders/${id}`)
      return response.data
    },
    { enabled: !!id }
  )
}

export function useCreateReminder() {
  const queryClient = useQueryClient()
  return useMutation(
    async (data: CreateReminderInput) => {
      const response = await apiClient.post("/reminders", data)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["reminders"])
        queryClient.invalidateQueries(["dashboard"])
      },
    }
  )
}

export function useUpdateReminder() {
  const queryClient = useQueryClient()
  return useMutation(
    async (data: UpdateReminderInput) => {
      const { id, ...rest } = data
      const response = await apiClient.patch(`/reminders/${id}`, rest)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["reminders"])
        queryClient.invalidateQueries(["dashboard"])
      },
    }
  )
}

export function useDeleteReminder() {
  const queryClient = useQueryClient()
  return useMutation(
    async (id: string) => {
      const response = await apiClient.delete(`/reminders/${id}`)
      return response.data
    },
    {
      onSuccess: () => {
        queryClient.invalidateQueries(["reminders"])
        queryClient.invalidateQueries(["dashboard"])
      },
    }
  )
}

export function useParseNaturalLanguage() {
  return useMutation(
    async (text: string) => {
      const response = await apiClient.post("/reminders/parse", { text })
      return response.data
    }
  )
}
