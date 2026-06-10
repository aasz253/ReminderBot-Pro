"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Users, CreditCard, TrendingUp, CheckCircle, DollarSign } from "lucide-react"
import { cn } from "@/lib/utils"

interface AdminStatsProps {
  stats: {
    total_users: number
    active_subscriptions: number
    mrr: number
    delivery_success_rate: number
    users_trend: number
    subscriptions_trend: number
    mrr_trend: number
    delivery_trend: number
  }
}

export function AdminStats({ stats }: AdminStatsProps) {
  const items = [
    {
      title: "Total Users",
      value: stats.total_users.toLocaleString(),
      icon: Users,
      trend: stats.users_trend,
      variant: "default" as const,
    },
    {
      title: "Active Subscriptions",
      value: stats.active_subscriptions.toLocaleString(),
      icon: CreditCard,
      trend: stats.subscriptions_trend,
      variant: "success" as const,
    },
    {
      title: "Monthly Revenue (MRR)",
      value: `$${stats.mrr.toLocaleString()}`,
      icon: DollarSign,
      trend: stats.mrr_trend,
      variant: "default" as const,
    },
    {
      title: "Delivery Success Rate",
      value: `${stats.delivery_success_rate}%`,
      icon: CheckCircle,
      trend: stats.delivery_trend,
      variant: "success" as const,
    },
  ]

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      {items.map((item, i) => (
        <motion.div
          key={item.title}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: i * 0.05 }}
        >
          <Card>
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">{item.title}</CardTitle>
              <div className={cn(
                "p-2 rounded-lg",
                item.variant === "success" && "bg-emerald-500/10 text-emerald-600",
                item.variant === "default" && "bg-primary/10 text-primary"
              )}>
                <item.icon className="h-4 w-4" />
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{item.value}</div>
              <p className="flex items-center gap-1 text-xs text-muted-foreground mt-1">
                <TrendingUp className={cn("h-3 w-3", item.trend >= 0 ? "text-emerald-500" : "text-red-500")} />
                <span className={item.trend >= 0 ? "text-emerald-500" : "text-red-500"}>
                  {item.trend >= 0 ? "+" : ""}{item.trend}%
                </span>
              </p>
            </CardContent>
          </Card>
        </motion.div>
      ))}
    </div>
  )
}
