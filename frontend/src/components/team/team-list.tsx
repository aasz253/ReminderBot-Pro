"use client"

import { motion } from "framer-motion"
import { Users, Settings, LogOut } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { getInitials } from "@/lib/utils"
import type { Team } from "@/types"

interface TeamListProps {
  teams: Team[]
  onView: (id: string) => void
  onSettings: (id: string) => void
  onLeave: (id: string) => void
}

export function TeamList({ teams, onView, onSettings, onLeave }: TeamListProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
      {teams.map((team, index) => (
        <motion.div
          key={team.id}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: index * 0.05 }}
        >
          <Card className="h-full group hover:shadow-md transition-all cursor-pointer" onClick={() => onView(team.id)}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="p-2 rounded-lg bg-primary/10">
                  <Users className="h-5 w-5 text-primary" />
                </div>
                <Badge variant="outline">Member</Badge>
              </div>

              <h3 className="font-semibold mb-1">{team.name}</h3>
              {team.description && (
                <p className="text-sm text-muted-foreground mb-4 line-clamp-2">{team.description}</p>
              )}

              <div className="flex items-center justify-between mt-4">
                <div className="flex items-center gap-2">
                  <div className="flex -space-x-2">
                    {[1, 2, 3].map((i) => (
                      <Avatar key={i} className="h-7 w-7 border-2 border-background">
                        <AvatarFallback className="text-[10px]">{getInitials(`User ${i}`)}</AvatarFallback>
                      </Avatar>
                    ))}
                  </div>
                  <span className="text-xs text-muted-foreground">+{team.member_count || 0}</span>
                </div>

                <div className="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button variant="ghost" size="icon" className="h-8 w-8" onClick={(e) => { e.stopPropagation(); onSettings(team.id) }}>
                    <Settings className="h-4 w-4" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-8 w-8 text-red-500" onClick={(e) => { e.stopPropagation(); onLeave(team.id) }}>
                    <LogOut className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
