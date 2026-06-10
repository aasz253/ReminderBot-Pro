"use client"

import { SupportTickets } from "@/components/admin/support-tickets"

const mockTickets = [
  { id: "1", user_id: "1", subject: "Payment not processed", message: "", status: "open" as const, priority: "urgent" as const, created_at: "2024-03-15", updated_at: "", user: { id: "1", name: "John Doe", email: "john@test.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
  { id: "2", user_id: "2", subject: "How to create team reminders", message: "", status: "in_progress" as const, priority: "low" as const, created_at: "2024-03-14", updated_at: "", user: { id: "2", name: "Jane Smith", email: "jane@test.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
  { id: "3", user_id: "3", subject: "Notification delay issue", message: "", status: "resolved" as const, priority: "high" as const, created_at: "2024-03-13", updated_at: "", user: { id: "3", name: "Bob Wilson", email: "bob@test.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
]

export default function AdminSupportPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Support Tickets</h1>
        <p className="text-muted-foreground">Manage customer support requests.</p>
      </div>

      <SupportTickets
        tickets={mockTickets}
        onView={() => {}}
        onUpdateStatus={() => {}}
      />
    </div>
  )
}
