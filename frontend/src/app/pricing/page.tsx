"use client"

import { motion } from "framer-motion"
import { Check } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { PLANS } from "@/lib/constants"
import { Navbar } from "@/components/layout/navbar"
import { Footer } from "@/components/layout/footer"

export default function PricingPage() {
  return (
    <>
      <Navbar />
      <main className="py-20">
        <div className="container">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <Badge className="mb-4">Pricing</Badge>
            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
              Simple, Transparent Pricing
            </h1>
            <p className="text-lg text-muted-foreground">
              Choose the perfect plan for your needs. Upgrade or downgrade anytime.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {PLANS.map((plan, index) => (
              <motion.div
                key={plan.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                className="relative"
              >
                {plan.highlighted && (
                  <div className="absolute -inset-0.5 bg-gradient-to-r from-indigo-500 to-violet-500 rounded-2xl blur opacity-30" />
                )}
                <Card className={cn("relative h-full", plan.highlighted && "border-primary shadow-xl")}>
                  <CardHeader>
                    {plan.highlighted && (
                      <div className="inline-flex items-center rounded-full bg-primary/10 px-3 py-1 text-xs font-medium text-primary mb-2 w-fit">
                        Most Popular
                      </div>
                    )}
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    <CardDescription>
                      <span className="text-4xl font-bold text-foreground">${plan.price}</span>
                      <span className="text-muted-foreground">/{plan.interval}</span>
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-3">
                      {plan.features.map((feature) => (
                        <li key={feature} className="flex items-start gap-2 text-sm">
                          <Check className="h-4 w-4 text-primary mt-0.5 shrink-0" />
                          <span>{feature}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                  <CardFooter>
                    <Button
                      className={cn("w-full", plan.highlighted && "bg-gradient-to-r from-indigo-500 to-violet-500")}
                      variant={plan.highlighted ? "default" : "outline"}
                      size="lg"
                      asChild
                    >
                      <Link href={plan.price === 0 ? "/auth/register" : `/checkout?plan=${plan.id}`}>
                        {plan.price === 0 ? "Get Started Free" : "Subscribe Now"}
                      </Link>
                    </Button>
                  </CardFooter>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="mt-16 text-center">
            <h3 className="text-xl font-semibold mb-4">All plans include</h3>
            <div className="grid sm:grid-cols-3 gap-6 max-w-3xl mx-auto text-sm text-muted-foreground">
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="font-medium text-foreground mb-1">SSL Security</p>
                <p>Enterprise-grade encryption</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="font-medium text-foreground mb-1">24/7 Support</p>
                <p>We're here to help anytime</p>
              </div>
              <div className="p-4 rounded-lg bg-muted/50">
                <p className="font-medium text-foreground mb-1">14-Day Guarantee</p>
                <p>Money-back guarantee</p>
              </div>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  )
}
