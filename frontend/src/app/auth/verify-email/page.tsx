"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { useSearchParams } from "next/navigation"
import { Clock, CheckCircle, XCircle, Loader2 } from "lucide-react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export default function VerifyEmailPage() {
  const [status, setStatus] = useState<"loading" | "success" | "error">("loading")
  const searchParams = useSearchParams()
  const token = searchParams.get("token")

  useEffect(() => {
    if (token) {
      setTimeout(() => setStatus("success"), 1500)
    } else {
      setStatus("error")
    }
  }, [token])

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-6">
          <Link href="/" className="inline-flex items-center gap-2 font-bold text-xl">
            <Clock className="h-6 w-6 text-primary" />
            <span>ReminderBot Pro</span>
          </Link>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Email Verification</CardTitle>
            <CardDescription>
              {status === "loading" && "Verifying your email..."}
              {status === "success" && "Your email has been verified"}
              {status === "error" && "Verification failed"}
            </CardDescription>
          </CardHeader>
          <CardContent className="text-center space-y-4">
            {status === "loading" && (
              <Loader2 className="h-12 w-12 animate-spin text-primary mx-auto" />
            )}
            {status === "success" && (
              <>
                <CheckCircle className="h-12 w-12 text-emerald-500 mx-auto" />
                <p className="text-sm text-muted-foreground">
                  Your email has been successfully verified. You can now access all features.
                </p>
                <Button asChild className="w-full">
                  <Link href="/dashboard">Go to Dashboard</Link>
                </Button>
              </>
            )}
            {status === "error" && (
              <>
                <XCircle className="h-12 w-12 text-red-500 mx-auto" />
                <p className="text-sm text-muted-foreground">
                  Invalid or expired verification link. Please request a new one.
                </p>
                <Button variant="outline" className="w-full">
                  Resend Verification Email
                </Button>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
