"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
} from "recharts"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs"

const data = [
  { name: "Mon", created: 8, completed: 6, missed: 1 },
  { name: "Tue", created: 12, completed: 10, missed: 2 },
  { name: "Wed", created: 6, completed: 5, missed: 0 },
  { name: "Thu", created: 15, completed: 12, missed: 3 },
  { name: "Fri", created: 10, completed: 8, missed: 1 },
  { name: "Sat", created: 4, completed: 3, missed: 0 },
  { name: "Sun", created: 7, completed: 6, missed: 1 },
]

const monthlyData = [
  { name: "Week 1", created: 45, completed: 38, missed: 5 },
  { name: "Week 2", created: 52, completed: 44, missed: 4 },
  { name: "Week 3", created: 48, completed: 42, missed: 3 },
  { name: "Week 4", created: 55, completed: 50, missed: 2 },
]

export function ReminderChart() {
  const [period, setPeriod] = useState("weekly")
  const chartData = period === "weekly" ? data : monthlyData

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle className="text-lg">Reminder Trends</CardTitle>
          <Tabs value={period} onValueChange={setPeriod}>
            <TabsList>
              <TabsTrigger value="weekly">Weekly</TabsTrigger>
              <TabsTrigger value="monthly">Monthly</TabsTrigger>
            </TabsList>
          </Tabs>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="completed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="missed" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--background))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "8px",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="completed"
                  stroke="#6366f1"
                  fillOpacity={1}
                  fill="url(#completed)"
                  strokeWidth={2}
                />
                <Area
                  type="monotone"
                  dataKey="missed"
                  stroke="#ef4444"
                  fillOpacity={1}
                  fill="url(#missed)"
                  strokeWidth={2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
