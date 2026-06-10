"use client"

import { UserTable } from "@/components/admin/user-table"

const mockUsers = [
  { id: "1", name: "John Doe", email: "john@example.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "2024-01-15", updated_at: "", subscription: { id: "s1", user_id: "1", plan_id: "premium" as const, status: "active" as const, current_period_start: "", current_period_end: "", cancel_at_period_end: false, created_at: "" } },
  { id: "2", name: "Jane Smith", email: "jane@example.com", role: "admin" as const, email_verified: true, two_factor_enabled: true, created_at: "2024-02-20", updated_at: "", subscription: { id: "s2", user_id: "2", plan_id: "business" as const, status: "active" as const, current_period_start: "", current_period_end: "", cancel_at_period_end: false, created_at: "" } },
  { id: "3", name: "Bob Wilson", email: "bob@example.com", role: "user" as const, email_verified: false, two_factor_enabled: false, created_at: "2024-03-10", updated_at: "" },
]

export default function AdminUsersPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Users</h1>
        <p className="text-muted-foreground">Manage platform users.</p>
      </div>
      <UserTable
        users={mockUsers}
        onView={() => {}}
        onSuspend={() => {}}
        onDelete={() => {}}
      />
    </div>
  )
}
