"use client"

import { motion } from "framer-motion"
import { Bell, CheckCircle, XCircle, TrendingUp, CalendarClock } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

interface StatsCardProps {
  title: string
  value: string | number
  icon: React.ElementType
  trend?: number
  trendLabel?: string
  variant?: "default" | "success" | "warning" | "destructive"
}

function StatsCard({ title, value, icon: Icon, trend, trendLabel, variant = "default" }: StatsCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between pb-2">
          <CardTitle className="text-sm font-medium text-muted-foreground">{title}</CardTitle>
          <div className={cn(
            "p-2 rounded-lg",
            variant === "success" && "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400",
            variant === "warning" && "bg-yellow-500/10 text-yellow-600 dark:text-yellow-400",
            variant === "destructive" && "bg-red-500/10 text-red-600 dark:text-red-400",
            variant === "default" && "bg-primary/10 text-primary"
          )}>
            <Icon className="h-4 w-4" />
          </div>
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{value}</div>
          {trend !== undefined && (
            <p className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
              <TrendingUp className={cn("h-3 w-3", trend >= 0 ? "text-emerald-500" : "text-red-500")} />
              <span className={trend >= 0 ? "text-emerald-500" : "text-red-500"}>
                {trend >= 0 ? "+" : ""}{trend}%
              </span>
              {trendLabel && <span>{trendLabel}</span>}
            </p>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

export function StatsCards({ stats }: { stats: any }) {
  const cards = [
    {
      title: "Active Reminders",
      value: stats?.active_reminders ?? 0,
      icon: Bell,
      trend: 12,
      trendLabel: "vs last week",
      variant: "default" as const,
    },
    {
      title: "Completed Today",
      value: stats?.completed_today ?? 0,
      icon: CheckCircle,
      trend: 8,
      trendLabel: "completion rate",
      variant: "success" as const,
    },
    {
      title: "Missed",
      value: stats?.missed_today ?? 0,
      icon: XCircle,
      trend: -5,
      trendLabel: "vs yesterday",
      variant: "destructive" as const,
    },
    {
      title: "Upcoming",
      value: stats?.upcoming_count ?? 0,
      icon: CalendarClock,
      trend: 3,
      trendLabel: "in next 24h",
      variant: "warning" as const,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <StatsCard key={card.title} {...card} />
      ))}
    </div>
  )
}
