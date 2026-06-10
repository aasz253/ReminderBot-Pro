"use client"

import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { getInitials } from "@/lib/utils"
import type { TeamMember } from "@/types"

interface TeamMembersProps {
  members: TeamMember[]
  currentUserId: string
  onRemove: (userId: string) => void
  onChangeRole: (userId: string, role: string) => void
}

export function TeamMembers({ members, currentUserId, onRemove, onChangeRole }: TeamMembersProps) {
  return (
    <div className="space-y-2">
      {members.map((member) => (
        <div key={member.user_id} className="flex items-center gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors">
          <Avatar className="h-9 w-9">
            <AvatarImage src={member.user?.avatar_url} />
            <AvatarFallback>{getInitials(member.user?.name || "User")}</AvatarFallback>
          </Avatar>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium truncate">{member.user?.name || "Unknown"}</p>
            <p className="text-xs text-muted-foreground truncate">{member.user?.email}</p>
          </div>
          <Badge variant={member.role === "owner" ? "default" : "outline"}>{member.role}</Badge>
          <div className="w-2 h-2 rounded-full bg-emerald-500" title="Online" />
          {currentUserId !== member.user_id && (
            <div className="flex gap-1">
              <Button variant="ghost" size="sm" className="h-8 text-xs" onClick={() => onChangeRole(member.user_id, member.role === "admin" ? "member" : "admin")}>
                {member.role === "admin" ? "Demote" : "Promote"}
              </Button>
              <Button variant="ghost" size="sm" className="h-8 text-xs text-red-500" onClick={() => onRemove(member.user_id)}>
                Remove
              </Button>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
