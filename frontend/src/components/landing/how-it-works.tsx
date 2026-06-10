"use client"

import { motion } from "framer-motion"
import { MessageSquare, Settings, Bell } from "lucide-react"

const steps = [
  {
    icon: MessageSquare,
    title: "Create a Reminder",
    description: "Type naturally like 'Meeting tomorrow at 2pm' or 'Buy groceries every Saturday'. Our AI understands you.",
    gradient: "from-indigo-500 to-violet-500",
  },
  {
    icon: Settings,
    title: "Set Channels & Schedule",
    description: "Choose where to get notified - email, Telegram, WhatsApp. Set repeat patterns with smart defaults.",
    gradient: "from-violet-500 to-purple-500",
  },
  {
    icon: Bell,
    title: "Get Notified Everywhere",
    description: "Receive timely notifications across all your chosen channels. Never miss what matters most.",
    gradient: "from-purple-500 to-pink-500",
  },
]

export function HowItWorks() {
  return (
    <section id="how-it-works" className="py-20 md:py-28 bg-muted/30">
      <div className="container">
        <div className="text-center max-w-2xl mx-auto mb-16">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            How It Works
          </h2>
          <p className="text-lg text-muted-foreground">
            Get started in minutes. Three simple steps to never miss a thing.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 relative">
          {/* Connecting line */}
          <div className="hidden md:block absolute top-24 left-[20%] right-[20%] h-0.5 bg-gradient-to-r from-indigo-500/20 via-violet-500/20 to-pink-500/20" />

          {steps.map((step, index) => (
            <motion.div
              key={step.title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: index * 0.2 }}
              viewport={{ once: true }}
              className="relative flex flex-col items-center text-center"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/20 to-violet-500/20 rounded-full blur-xl" />
                <div className={`relative flex items-center justify-center h-16 w-16 rounded-full bg-gradient-to-br ${step.gradient} shadow-lg mb-6`}>
                  <step.icon className="h-7 w-7 text-white" />
                </div>
                <div className="absolute -top-2 -right-2 h-7 w-7 rounded-full bg-background border-2 border-primary flex items-center justify-center text-sm font-bold text-primary">
                  {index + 1}
                </div>
              </div>
              <h3 className="text-xl font-semibold mb-3">{step.title}</h3>
              <p className="text-sm text-muted-foreground max-w-xs">{step.description}</p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  )
}
