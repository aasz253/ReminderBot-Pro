"use client"

import { AnimatePresence } from "framer-motion"
import { ReminderCard } from "@/components/reminders/reminder-card"
import { Skeleton } from "@/components/ui/skeleton"
import { Bell } from "lucide-react"
import type { Reminder } from "@/types"

interface ReminderListProps {
  reminders?: Reminder[]
  isLoading: boolean
  selectedIds: Set<string>
  onSelect: (id: string) => void
  onEdit: (id: string) => void
  onDelete: (id: string) => void
  onComplete: (id: string) => void
  onPause: (id: string) => void
}

export function ReminderList({
  reminders,
  isLoading,
  selectedIds,
  onSelect,
  onEdit,
  onDelete,
  onComplete,
  onPause,
}: ReminderListProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="p-4 rounded-lg border">
            <div className="flex items-start gap-3">
              <Skeleton className="h-2 w-2 rounded-full mt-2" />
              <div className="flex-1 space-y-2">
                <Skeleton className="h-4 w-3/4" />
                <Skeleton className="h-3 w-1/2" />
                <div className="flex gap-2">
                  <Skeleton className="h-5 w-16 rounded-full" />
                  <Skeleton className="h-5 w-20 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  if (!reminders || reminders.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="p-4 rounded-full bg-muted mb-4">
          <Bell className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-1">No reminders yet</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Create your first reminder to get started.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-2">
      <AnimatePresence>
        {reminders.map((reminder) => (
          <ReminderCard
            key={reminder.id}
            reminder={reminder}
            selected={selectedIds.has(reminder.id)}
            onSelect={onSelect}
            onEdit={onEdit}
            onDelete={onDelete}
            onComplete={onComplete}
            onPause={onPause}
          />
        ))}
      </AnimatePresence>
    </div>
  )
}
