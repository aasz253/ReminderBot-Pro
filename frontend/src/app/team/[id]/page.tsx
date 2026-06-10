"use client"

import { useParams, useRouter } from "next/navigation"
import { ArrowLeft, UserPlus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { TeamMembers } from "@/components/team/team-members"
import { InviteMemberDialog } from "@/components/team/invite-member-dialog"
import { ReminderList } from "@/components/reminders/reminder-list"

const mockMembers = [
  { id: "1", team_id: "1", user_id: "me", role: "owner" as const, joined_at: "", user: { id: "me", name: "You", email: "you@example.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
  { id: "2", team_id: "1", user_id: "2", role: "admin" as const, joined_at: "", user: { id: "2", name: "Alice", email: "alice@example.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
  { id: "3", team_id: "1", user_id: "3", role: "member" as const, joined_at: "", user: { id: "3", name: "Bob", email: "bob@example.com", role: "user" as const, email_verified: true, two_factor_enabled: false, created_at: "", updated_at: "" } },
]

export default function TeamDetailPage() {
  const params = useParams()
  const router = useRouter()

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => router.push("/team")}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Engineering</h1>
          <p className="text-muted-foreground">Engineering team reminders</p>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">Team Members (3)</CardTitle>
          <InviteMemberDialog>
            <Button size="sm" className="gap-2">
              <UserPlus className="h-4 w-4" /> Invite
            </Button>
          </InviteMemberDialog>
        </CardHeader>
        <CardContent>
          <TeamMembers
            members={mockMembers}
            currentUserId="me"
            onRemove={() => {}}
            onChangeRole={() => {}}
          />
        </CardContent>
      </Card>

      <Separator />

      <div>
        <h2 className="text-xl font-semibold mb-4">Team Reminders</h2>
        <ReminderList
          reminders={[]}
          isLoading={false}
          selectedIds={new Set()}
          onSelect={() => {}}
          onEdit={() => {}}
          onDelete={() => {}}
          onComplete={() => {}}
          onPause={() => {}}
        />
      </div>
    </div>
  )
}
