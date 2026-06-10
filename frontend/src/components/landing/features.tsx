"use client"

import { motion } from "framer-motion"
import {
  Brain,
  Bell,
  MessageCircle,
  Users,
  Smartphone,
  Puzzle,
} from "lucide-react"
import { Card, CardContent } from "@/components/ui/card"

const features = [
  {
    icon: Brain,
    title: "Smart Scheduling",
    description: "AI-powered scheduling that learns your patterns and suggests optimal reminder times.",
    gradient: "from-blue-500 to-cyan-500",
  },
  {
    icon: Bell,
    title: "Multi-Channel Notifications",
    description: "Get reminders via Email, Telegram, WhatsApp, SMS, and push notifications.",
    gradient: "from-violet-500 to-purple-500",
  },
  {
    icon: MessageCircle,
    title: "AI-Powered Suggestions",
    description: "Natural language processing understands your reminders in plain English.",
    gradient: "from-emerald-500 to-teal-500",
  },
  {
    icon: Users,
    title: "Team Collaboration",
    description: "Share reminders and tasks with your team. Perfect for project management.",
    gradient: "from-orange-500 to-red-500",
  },
  {
    icon: Smartphone,
    title: "Cross-Platform",
    description: "Access your reminders anywhere - web, mobile, and popular messaging apps.",
    gradient: "from-pink-500 to-rose-500",
  },
  {
    icon: Puzzle,
    title: "Premium Integrations",
    description: "Connect with your favorite tools: Slack, Discord, Google Calendar, and more.",
    gradient: "from-indigo-500 to-blue-500",
  },
]

export function Features() {
  return (
    <section id="features" className="py-20 md:py-28">
      <div className="container">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            Everything you need to stay on track
          </h2>
          <p className="text-lg text-muted-foreground">
            Powerful features that make reminder management effortless and intelligent.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.1 }}
              viewport={{ once: true }}
            >
              <Card className="group h-full hover:shadow-lg transition-all duration-300">
                <CardContent className="p-6">
                  <div className={`inline-flex p-3 rounded-xl bg-gradient-to-br ${feature.gradient} mb-4`}>
                    <feature.icon className="h-6 w-6 text-white" />
                  </div>
                  <h3 className="font-semibold text-lg mb-2">{feature.title}</h3>
                  <p className="text-sm text-muted-foreground">{feature.description}</p>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
