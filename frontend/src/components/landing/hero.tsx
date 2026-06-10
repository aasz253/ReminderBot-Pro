"use client"

import { motion } from "framer-motion"
import { Clock, Bell, Sparkles, ArrowRight, Play } from "lucide-react"
import { Button } from "@/components/ui/button"
import { APP_NAME, APP_TAGLINE } from "@/lib/constants"
import Link from "next/link"

const floatingIcons = [
  { Icon: Bell, delay: 0, x: 100, y: -50 },
  { Icon: Clock, delay: 0.2, x: -80, y: -30 },
  { Icon: Sparkles, delay: 0.4, x: 60, y: 40 },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden py-20 md:py-32">
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[800px] bg-gradient-to-b from-primary/10 to-transparent rounded-full blur-3xl" />

      <div className="container relative">
        <div className="flex flex-col items-center text-center max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
          >
            <div className="inline-flex items-center gap-2 rounded-full border bg-muted/50 px-4 py-1.5 text-sm mb-6">
              <Sparkles className="h-4 w-4 text-primary" />
              <span>AI-Powered Smart Reminders</span>
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight text-balance"
          >
            {APP_TAGLINE}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="mt-6 text-lg md:text-xl text-muted-foreground max-w-2xl text-balance"
          >
            Create reminders using natural language, get notified across email, Telegram, WhatsApp, and more.
            Your smart scheduling assistant powered by AI.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="mt-8 flex flex-col sm:flex-row items-center gap-4"
          >
            <Button size="xl" className="gap-2" asChild>
              <Link href="/auth/register">
                Get Started Free <ArrowRight className="h-5 w-5" />
              </Link>
            </Button>
            <Button size="xl" variant="outline" className="gap-2">
              <Play className="h-5 w-5" /> Watch Demo
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="mt-12 flex items-center gap-8 text-sm text-muted-foreground"
          >
            <div className="flex -space-x-2">
              {[1, 2, 3, 4].map((i) => (
                <div key={i} className="h-8 w-8 rounded-full border-2 border-background bg-gradient-to-br from-primary/80 to-violet-500/80" />
              ))}
            </div>
            <div className="text-left">
              <p className="font-semibold text-foreground">10,000+</p>
              <p>Active users</p>
            </div>
          </motion.div>
        </div>

        {/* Floating icons */}
        <div className="hidden md:block">
          {floatingIcons.map(({ Icon, delay, x, y }) => (
            <motion.div
              key={delay}
              initial={{ opacity: 0, x: 0, y: 0 }}
              animate={{
                opacity: [0, 1, 1, 0],
                x: [0, x, x, 0],
                y: [0, y, y, 0],
              }}
              transition={{
                duration: 4,
                delay,
                repeat: Infinity,
                repeatDelay: 2,
              }}
              className="absolute top-1/2 left-1/2"
            >
              <div className="flex items-center justify-center h-12 w-12 rounded-xl bg-primary/10 border border-primary/20">
                <Icon className="h-6 w-6 text-primary" />
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
