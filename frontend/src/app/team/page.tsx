"use client"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { Plus, Users } from "lucide-react"
import { Button } from "@/components/ui/button"
import { TeamList } from "@/components/team/team-list"
import { CreateTeamDialog } from "@/components/team/create-team-dialog"

const mockTeams = [
  { id: "1", name: "Engineering", description: "Engineering team reminders", member_count: 5, owner_id: "me", created_at: "2026-01-15T08:00:00Z" },
  { id: "2", name: "Marketing", description: "Marketing campaigns and deadlines", member_count: 3, owner_id: "me", created_at: "2026-02-10T12:00:00Z" },
]

export default function TeamPage() {
  const router = useRouter()

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Teams</h1>
          <p className="text-muted-foreground">Collaborate with your team on reminders.</p>
        </div>
        <CreateTeamDialog>
          <Button className="gap-2">
            <Plus className="h-4 w-4" /> Create Team
          </Button>
        </CreateTeamDialog>
      </div>

      {mockTeams.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <div className="p-4 rounded-full bg-muted mb-4">
            <Users className="h-8 w-8 text-muted-foreground" />
          </div>
          <h3 className="text-lg font-medium mb-1">No teams yet</h3>
          <p className="text-sm text-muted-foreground mb-4">Create a team to collaborate.</p>
          <CreateTeamDialog>
            <Button>Create Your First Team</Button>
          </CreateTeamDialog>
        </div>
      ) : (
        <TeamList
          teams={mockTeams}
          onView={(id) => router.push(`/team/${id}`)}
          onSettings={(id) => router.push(`/team/${id}`)}
          onLeave={(id) => {}}
        />
      )}
    </div>
  )
}
