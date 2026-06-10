"use client"

import { Toaster as SonnerToaster } from "sonner"
import { useTheme } from "next-themes"

export function Toaster() {
  const { theme } = useTheme()

  return (
    <SonnerToaster
      position="top-right"
      toastOptions={{
        style: {
          background: theme === "dark" ? "hsl(222.2 84% 4.9%)" : "white",
          color: theme === "dark" ? "hsl(210 40% 98%)" : "hsl(222.2 84% 4.9%)",
          border: `1px solid ${theme === "dark" ? "hsl(217.2 32.6% 17.5%)" : "hsl(214.3 31.8% 91.4%)"}`,
        },
      }}
      richColors
      closeButton
    />
  )
}

export { toast } from "sonner"
