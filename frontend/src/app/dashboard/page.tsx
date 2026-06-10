"use client"

import { Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { StatsCards } from "@/components/dashboard/stats-cards"
import { ReminderChart } from "@/components/dashboard/reminder-chart"
import { ProductivityScore } from "@/components/dashboard/productivity-score"
import { UpcomingReminders } from "@/components/dashboard/upcoming-reminders"
import { CategoryBreakdown } from "@/components/dashboard/category-breakdown"
import { CreateReminderDialog } from "@/components/reminders/create-reminder-dialog"

export default function DashboardPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">Overview of your reminders and productivity.</p>
        </div>
        <CreateReminderDialog>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> Create Reminder
          </Button>
        </CreateReminderDialog>
      </div>

      <StatsCards stats={null} />

      <div className="grid gap-6 lg:grid-cols-2">
        <ReminderChart />
        <ProductivityScore />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <UpcomingReminders />
        <CategoryBreakdown />
      </div>
    </div>
  )
}
