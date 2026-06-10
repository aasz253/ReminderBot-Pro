import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import { format, formatDistanceToNow, isToday, isYesterday, parseISO } from "date-fns"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(date: string | Date, fmt: string = "MMM d, yyyy"): string {
  if (!date) return ""
  const d = typeof date === "string" ? parseISO(date) : date
  return format(d, fmt)
}

export function formatRelativeTime(date: string | Date): string {
  if (!date) return ""
  const d = typeof date === "string" ? parseISO(date) : date
  if (isToday(d)) return `Today at ${format(d, "h:mm a")}`
  if (isYesterday(d)) return `Yesterday at ${format(d, "h:mm a")}`
  return formatDistanceToNow(d, { addSuffix: true })
}

export function getInitials(name: string): string {
  if (!name) return "?"
  return name
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)
}
