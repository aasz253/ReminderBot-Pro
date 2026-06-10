"use client"

import { useState, useCallback } from "react"
import { Plus, Trash2, CheckCircle, PauseCircle, Play } from "lucide-react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { ReminderList } from "@/components/reminders/reminder-list"
import { ReminderFilters } from "@/components/reminders/reminder-filters"
import { BulkActions } from "@/components/reminders/bulk-actions"
import { CreateReminderDialog } from "@/components/reminders/create-reminder-dialog"
import { useReminders, useDeleteReminder, useUpdateReminder } from "@/hooks/use-reminders"
import type { ReminderFilters as ReminderFiltersType } from "@/types"

export default function RemindersPage() {
  const [filters, setFilters] = useState<ReminderFiltersType>({})
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set())

  const { data, isLoading } = useReminders(filters)
  const deleteReminder = useDeleteReminder()
  const updateReminder = useUpdateReminder()

  const reminders = data?.data || []

  const handleFilterChange = useCallback((key: string, value: string) => {
    setFilters((prev) => ({ ...prev, [key]: value === "all" ? undefined : value }))
    setSelectedIds(new Set())
  }, [])

  const handleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }, [])

  const handleSelectAll = useCallback(() => {
    setSelectedIds(new Set(reminders.map((r) => r.id)))
  }, [reminders])

  const handleDeselectAll = useCallback(() => {
    setSelectedIds(new Set())
  }, [])

  const handleDelete = useCallback(async (id: string) => {
    try {
      await deleteReminder.mutateAsync(id)
      toast.success("Reminder deleted")
    } catch {
      toast.error("Failed to delete reminder")
    }
  }, [deleteReminder])

  const handleComplete = useCallback(async (id: string) => {
    try {
      await updateReminder.mutateAsync({ id, status: "completed" })
      toast.success("Reminder completed!")
    } catch {
      toast.error("Failed to complete reminder")
    }
  }, [updateReminder])

  const handlePause = useCallback(async (id: string) => {
    try {
      await updateReminder.mutateAsync({ id, status: "paused" })
      toast.success("Reminder paused")
    } catch {
      toast.error("Failed to pause reminder")
    }
  }, [updateReminder])

  const handleBulkAction = useCallback(async (action: string) => {
    try {
      const promises = Array.from(selectedIds).map((id) => {
        if (action === "delete") return deleteReminder.mutateAsync(id)
        if (action === "complete") return updateReminder.mutateAsync({ id, status: "completed" })
        if (action === "pause") return updateReminder.mutateAsync({ id, status: "paused" })
        if (action === "resume") return updateReminder.mutateAsync({ id, status: "active" })
        return Promise.resolve()
      })
      await Promise.all(promises)
      toast.success(`Bulk ${action} completed`)
      setSelectedIds(new Set())
    } catch {
      toast.error(`Bulk ${action} failed`)
    }
  }, [selectedIds, deleteReminder, updateReminder])

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reminders</h1>
          <p className="text-muted-foreground">Manage all your reminders.</p>
        </div>
        <CreateReminderDialog>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> Create Reminder
          </Button>
        </CreateReminderDialog>
      </div>

      <ReminderFilters filters={filters as Record<string, string>} onFilterChange={handleFilterChange} />

      <BulkActions
        selectedCount={selectedIds.size}
        totalCount={reminders.length}
        onSelectAll={handleSelectAll}
        onDeselectAll={handleDeselectAll}
        onBulkComplete={() => handleBulkAction("complete")}
        onBulkDelete={() => handleBulkAction("delete")}
        onBulkPause={() => handleBulkAction("pause")}
        onBulkResume={() => handleBulkAction("resume")}
      />

      <ReminderList
        reminders={reminders}
        isLoading={isLoading}
        selectedIds={selectedIds}
        onSelect={handleSelect}
        onEdit={() => {}}
        onDelete={handleDelete}
        onComplete={handleComplete}
        onPause={handlePause}
      />
    </div>
  )
}
