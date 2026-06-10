"use client"

import { motion } from "framer-motion"
import { Clock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { formatRelativeTime, cn } from "@/lib/utils"
import { REMINDER_PRIORITIES } from "@/lib/constants"

const upcomingData = [
  { id: 1, title: "Team standup meeting", due_date: new Date(Date.now() + 3600000).toISOString(), priority: "high", category: "work" },
  { id: 2, title: "Buy groceries", due_date: new Date(Date.now() + 7200000).toISOString(), priority: "medium", category: "shopping" },
  { id: 3, title: "Gym session", due_date: new Date(Date.now() + 10800000).toISOString(), priority: "low", category: "health" },
  { id: 4, title: "Doctor appointment", due_date: new Date(Date.now() + 86400000).toISOString(), priority: "urgent", category: "health" },
  { id: 5, title: "Submit report", due_date: new Date(Date.now() + 172800000).toISOString(), priority: "high", category: "work" },
]

export function UpcomingReminders() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.3 }}
    >
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Upcoming Reminders</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {upcomingData.map((reminder, index) => {
              const priority = REMINDER_PRIORITIES.find(p => p.id === reminder.priority)
              return (
                <motion.div
                  key={reminder.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="flex items-start gap-3 p-3 rounded-lg hover:bg-muted/50 transition-colors group cursor-pointer"
                >
                  <div className={cn("p-1.5 rounded-full mt-0.5", priority?.bg)}>
                    <Clock className={cn("h-3.5 w-3.5", priority?.color)} />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium truncate">{reminder.title}</p>
                    <p className="text-xs text-muted-foreground">
                      {formatRelativeTime(reminder.due_date)}
                    </p>
                  </div>
                  <Badge variant="outline" className="shrink-0 text-xs">
                    {priority?.label}
                  </Badge>
                </motion.div>
              )
            })}
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
