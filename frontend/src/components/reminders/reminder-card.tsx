"use client"

import { motion } from "framer-motion"
import { Bell, Mail, Send, MessageCircle, MessageSquare, Edit2, Trash2, CheckCircle, PauseCircle, Repeat } from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { cn, formatRelativeTime } from "@/lib/utils"
import { REMINDER_PRIORITIES, NOTIFICATION_CHANNELS, CATEGORIES } from "@/lib/constants"
import type { Reminder } from "@/types"

const channelIcons: Record<string, React.ElementType> = {
  email: Mail,
  telegram: Send,
  whatsapp: MessageCircle,
  sms: MessageSquare,
  push: Bell,
}

interface ReminderCardProps {
  reminder: Reminder
  onEdit?: (id: string) => void
  onDelete?: (id: string) => void
  onComplete?: (id: string) => void
  onPause?: (id: string) => void
  selected?: boolean
  onSelect?: (id: string) => void
}

export function ReminderCard({ reminder, onEdit, onDelete, onComplete, onPause, selected, onSelect }: ReminderCardProps) {
  const priority = REMINDER_PRIORITIES.find(p => p.id === reminder.priority)
  const category = CATEGORIES.find(c => c.id === reminder.category)

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      layout
    >
      <Card className={cn(
        "group hover:shadow-md transition-all duration-200 cursor-pointer",
        selected && "ring-2 ring-primary",
        reminder.status === "completed" && "opacity-60"
      )}
        onClick={() => onSelect?.(reminder.id)}
      >
        <CardContent className="p-4">
          <div className="flex items-start gap-3">
            <div className={cn(
              "mt-1 h-2 w-2 rounded-full shrink-0",
              priority?.color?.replace("text", "bg")
            )} />

            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1">
                <h3 className={cn(
                  "text-sm font-medium truncate",
                  reminder.status === "completed" && "line-through"
                )}>
                  {reminder.title}
                </h3>
                {reminder.repeat_type !== "none" && (
                  <Repeat className="h-3 w-3 text-muted-foreground shrink-0" />
                )}
              </div>

              {reminder.description && (
                <p className="text-xs text-muted-foreground truncate mb-2">
                  {reminder.description}
                </p>
              )}

              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span>{formatRelativeTime(reminder.due_date)}</span>
                <span>•</span>
                <Badge variant="outline" className="text-[10px] px-1.5 py-0">
                  {priority?.label}
                </Badge>
                {category && (
                  <Badge
                    variant="outline"
                    className="text-[10px] px-1.5 py-0"
                    style={{ borderColor: category.color, color: category.color }}
                  >
                    {category.label}
                  </Badge>
                )}
              </div>

              <div className="flex items-center gap-1.5 mt-2">
                {reminder.notification_channels?.map((channel) => {
                  const Icon = channelIcons[channel]
                  if (!Icon) return null
                  return (
                    <div key={channel} className="p-1 rounded-md bg-muted/50" title={channel}>
                      <Icon className="h-3 w-3 text-muted-foreground" />
                    </div>
                  )
                })}
              </div>
            </div>

            <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
              {reminder.status === "active" && (
                <>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onComplete?.(reminder.id) }}>
                    <CheckCircle className="h-4 w-4 text-emerald-500" />
                  </Button>
                  <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onPause?.(reminder.id) }}>
                    <PauseCircle className="h-4 w-4 text-yellow-500" />
                  </Button>
                </>
              )}
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onEdit?.(reminder.id) }}>
                <Edit2 className="h-4 w-4 text-muted-foreground" />
              </Button>
              <Button variant="ghost" size="icon" className="h-7 w-7" onClick={(e) => { e.stopPropagation(); onDelete?.(reminder.id) }}>
                <Trash2 className="h-4 w-4 text-red-500" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
