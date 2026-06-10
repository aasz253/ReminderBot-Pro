"use client"

import { useState, Suspense } from "react"
import { useSearchParams, useRouter } from "next/navigation"
import { Clock, CheckCircle } from "lucide-react"
import { toast } from "sonner"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Separator } from "@/components/ui/separator"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { PaymentMethods } from "@/components/payments/payment-methods"
import { MpesaForm } from "@/components/payments/mpesa-form"
import { PLANS } from "@/lib/constants"

function CheckoutContent() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const planId = searchParams.get("plan") || "premium"
  const plan = PLANS.find((p) => p.id === planId) || PLANS[1]

  const [paymentMethod, setPaymentMethod] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)

  async function handleProcessPayment() {
    if (!paymentMethod) {
      toast.error("Please select a payment method")
      return
    }
    setIsProcessing(true)
    try {
      await new Promise(resolve => setTimeout(resolve, 2000))
      toast.success("Payment successful! Welcome to " + plan.name)
      router.push("/dashboard")
    } catch {
      toast.error("Payment failed. Please try again.")
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-3xl mx-auto space-y-8">
        <div className="text-center">
          <Link href="/" className="inline-flex items-center gap-2 font-bold text-xl mb-4">
            <Clock className="h-6 w-6 text-primary" />
            <span>ReminderBot Pro</span>
          </Link>
          <h1 className="text-3xl font-bold tracking-tight">Checkout</h1>
          <p className="text-muted-foreground">Complete your subscription purchase.</p>
        </div>

        <div className="grid gap-8 lg:grid-cols-5">
          <div className="lg:col-span-3 space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Payment Method</CardTitle>
                <CardDescription>Choose how to pay</CardDescription>
              </CardHeader>
              <CardContent>
                <PaymentMethods selected={paymentMethod} onSelect={setPaymentMethod} />
              </CardContent>
            </Card>

            {paymentMethod === "mpesa" && (
              <MpesaForm amount={plan.price} />
            )}

            {paymentMethod && paymentMethod !== "mpesa" && (
              <Card>
                <CardHeader>
                  <CardTitle>Card Details</CardTitle>
                  <CardDescription>Enter your payment details</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <Label>Card Number</Label>
                    <Input placeholder="4242 4242 4242 4242" />
                  </div>
                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label>Expiry</Label>
                      <Input placeholder="MM/YY" />
                    </div>
                    <div className="space-y-2">
                      <Label>CVC</Label>
                      <Input placeholder="123" />
                    </div>
                  </div>
                  <Button className="w-full" onClick={handleProcessPayment} disabled={isProcessing}>
                    {isProcessing ? "Processing..." : `Pay $${plan.price}`}
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Order Summary</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="flex items-center justify-between">
                  <span className="font-medium">{plan.name} Plan</span>
                  <span>${plan.price}/{plan.interval}</span>
                </div>
                <Separator />
                <div className="space-y-2">
                  {plan.features.slice(0, 5).map((feature) => (
                    <div key={feature} className="flex items-center gap-2 text-sm text-muted-foreground">
                      <CheckCircle className="h-3.5 w-3.5 text-primary" />
                      {feature}
                    </div>
                  ))}
                  {plan.features.length > 5 && (
                    <p className="text-xs text-muted-foreground pl-5">+{plan.features.length - 5} more features</p>
                  )}
                </div>
                <Separator />
                <div className="flex items-center justify-between font-bold">
                  <span>Total</span>
                  <span>${plan.price}/{plan.interval}</span>
                </div>
                {paymentMethod && paymentMethod !== "mpesa" && (
                  <Button className="w-full" onClick={handleProcessPayment} disabled={isProcessing}>
                    {isProcessing ? "Processing..." : `Pay $${plan.price}`}
                  </Button>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function CheckoutPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Loading...</div>}>
      <CheckoutContent />
    </Suspense>
  )
}
