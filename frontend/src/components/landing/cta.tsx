"use client"

import { motion } from "framer-motion"
import { ArrowRight, Sparkles } from "lucide-react"
import { Button } from "@/components/ui/button"
import Link from "next/link"

export function CTA() {
  return (
    <section className="py-20 md:py-28">
      <div className="container">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500 via-violet-500 to-purple-600 p-8 md:p-16 text-center text-white"
        >
          <div className="absolute inset-0 bg-grid-white/10" />
          <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-white/10 rounded-full blur-3xl" />

          <div className="relative">
            <div className="inline-flex items-center gap-2 rounded-full bg-white/20 px-4 py-1.5 text-sm mb-6">
              <Sparkles className="h-4 w-4" />
              <span>Start your free trial</span>
            </div>

            <h2 className="text-3xl md:text-5xl font-bold tracking-tight mb-4">
              Ready to Get Started?
            </h2>
            <p className="text-lg text-white/80 max-w-xl mx-auto mb-8">
              Join thousands of happy users and never miss what matters most. No credit card required.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button size="xl" variant="secondary" className="gap-2 bg-white text-indigo-600 hover:bg-white/90" asChild>
                <Link href="/auth/register">
                  Get Started Free <ArrowRight className="h-5 w-5" />
                </Link>
              </Button>
              <Button size="xl" variant="outline" className="gap-2 border-white/30 text-white hover:bg-white/10" asChild>
                <Link href="#features">Learn More</Link>
              </Button>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  )
}
