"use client"

import { Smartphone, CreditCard, Landmark, Wallet } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { cn } from "@/lib/utils"

const methods = [
  { id: "mpesa", label: "M-Pesa", description: "Pay via M-Pesa STK Push", icon: Smartphone, color: "text-green-600" },
  { id: "airtel_money", label: "Airtel Money", description: "Pay via Airtel Money", icon: Smartphone, color: "text-red-600" },
  { id: "paypal", label: "PayPal", description: "Pay with your PayPal account", icon: Wallet, color: "text-blue-600" },
  { id: "stripe", label: "Stripe", description: "Credit/Debit card via Stripe", icon: CreditCard, color: "text-indigo-600" },
]

interface PaymentMethodsProps {
  selected: string
  onSelect: (method: string) => void
}

export function PaymentMethods({ selected, onSelect }: PaymentMethodsProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2">
      {methods.map((method) => {
        const Icon = method.icon
        return (
          <Card
            key={method.id}
            className={cn(
              "cursor-pointer transition-all hover:shadow-md",
              selected === method.id && "ring-2 ring-primary border-primary"
            )}
            onClick={() => onSelect(method.id)}
          >
            <CardHeader className="pb-2">
              <div className="flex items-center gap-2">
                <Icon className={cn("h-5 w-5", method.color)} />
                <CardTitle className="text-sm">{method.label}</CardTitle>
              </div>
            </CardHeader>
            <CardContent>
              <CardDescription>{method.description}</CardDescription>
            </CardContent>
          </Card>
        )
      })}
    </div>
  )
}
