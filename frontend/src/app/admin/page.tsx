"use client"

import { AdminStats } from "@/components/admin/admin-stats"
import { RevenueChart } from "@/components/admin/revenue-chart"
import { SupportTickets } from "@/components/admin/support-tickets"

const mockStats = {
  total_users: 12543,
  active_subscriptions: 4832,
  mrr: 45280,
  delivery_success_rate: 98.5,
  users_trend: 12,
  subscriptions_trend: 8,
  mrr_trend: 15,
  delivery_trend: 0.5,
}

const mockTickets = [
  { id: "1", user_id: "1", subject: "Payment issue", message: "", status: "open" as const, priority: "high" as const, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), user: { id: "1", name: "John", email: "john@test.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
  { id: "2", user_id: "2", subject: "Feature request", message: "", status: "in_progress" as const, priority: "medium" as const, created_at: new Date().toISOString(), updated_at: new Date().toISOString(), user: { id: "2", name: "Jane", email: "jane@test.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
]

export default function AdminPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Admin Overview</h1>
        <p className="text-muted-foreground">Platform statistics and management.</p>
      </div>

      <AdminStats stats={mockStats} />

      <RevenueChart />

      <div>
        <h2 className="text-xl font-semibold mb-4">Recent Support Tickets</h2>
        <SupportTickets
          tickets={mockTickets}
          onView={() => {}}
          onUpdateStatus={() => {}}
        />
      </div>
    </div>
  )
}
