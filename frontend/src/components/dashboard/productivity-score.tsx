"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function ProductivityScore({ score = 85, trend = "up", dailyStreak = 7 }: { score?: number; trend?: string; dailyStreak?: number }) {
  const radius = 60
  const circumference = 2 * Math.PI * radius
  const offset = circumference - (score / 100) * circumference

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3, delay: 0.2 }}
    >
      <Card className="h-full">
        <CardHeader>
          <CardTitle className="text-lg">Productivity Score</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-col items-center">
          <div className="relative flex items-center justify-center">
            <svg width="150" height="150" className="transform -rotate-90">
              <circle
                cx="75"
                cy="75"
                r={radius}
                fill="none"
                stroke="hsl(var(--muted))"
                strokeWidth="10"
              />
              <motion.circle
                cx="75"
                cy="75"
                r={radius}
                fill="none"
                stroke="url(#gradient)"
                strokeWidth="10"
                strokeLinecap="round"
                strokeDasharray={circumference}
                initial={{ strokeDashoffset: circumference }}
                animate={{ strokeDashoffset: offset }}
                transition={{ duration: 1.5, ease: "easeOut" }}
              />
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#6366f1" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
            <div className="absolute flex flex-col items-center">
              <span className="text-3xl font-bold">{score}%</span>
              <span className="text-xs text-muted-foreground capitalize">{trend}</span>
            </div>
          </div>
          <div className="mt-4 text-center">
            <p className="text-sm text-muted-foreground">
              {dailyStreak} day streak
            </p>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  )
}
