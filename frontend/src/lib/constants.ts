export const PLANS = [
  {
    id: "free",
    name: "Free",
    price: 0,
    currency: "USD",
    interval: "month",
    features: [
      "Up to 10 reminders",
      "Basic notifications",
      "Email reminders",
      "7-day history",
    ],
    highlighted: false,
  },
  {
    id: "premium",
    name: "Premium",
    price: 3,
    currency: "USD",
    interval: "month",
    features: [
      "Unlimited reminders",
      "Multi-channel notifications",
      "AI-powered suggestions",
      "Priority support",
      "Advanced analytics",
      "Custom categories",
      "90-day history",
    ],
    highlighted: true,
  },
  {
    id: "business",
    name: "Business",
    price: 10,
    currency: "USD",
    interval: "month",
    features: [
      "Everything in Premium",
      "Team collaboration",
      "Unlimited team members",
      "Admin dashboard",
      "API access",
      "Custom integrations",
      "Unlimited history",
      "Dedicated support",
    ],
    highlighted: false,
  },
] as const

export const NOTIFICATION_CHANNELS = [
  { id: "email", label: "Email", icon: "Mail" },
  { id: "telegram", label: "Telegram", icon: "Send" },
  { id: "whatsapp", label: "WhatsApp", icon: "MessageCircle" },
  { id: "sms", label: "SMS", icon: "MessageSquare" },
  { id: "push", label: "Push Notification", icon: "Bell" },
] as const

export const REMINDER_PRIORITIES = [
  { id: "low", label: "Low", color: "text-green-500", bg: "bg-green-500/10" },
  { id: "medium", label: "Medium", color: "text-yellow-500", bg: "bg-yellow-500/10" },
  { id: "high", label: "High", color: "text-orange-500", bg: "bg-orange-500/10" },
  { id: "urgent", label: "Urgent", color: "text-red-500", bg: "bg-red-500/10" },
] as const

export const REPEAT_OPTIONS = [
  { id: "none", label: "Does not repeat" },
  { id: "daily", label: "Daily" },
  { id: "weekdays", label: "Weekdays" },
  { id: "weekly", label: "Weekly" },
  { id: "biweekly", label: "Every 2 weeks" },
  { id: "monthly", label: "Monthly" },
  { id: "yearly", label: "Yearly" },
  { id: "custom", label: "Custom (cron)" },
] as const

export const CATEGORIES = [
  { id: "personal", label: "Personal", color: "#6366f1" },
  { id: "work", label: "Work", color: "#f59e0b" },
  { id: "health", label: "Health", color: "#10b981" },
  { id: "finance", label: "Finance", color: "#3b82f6" },
  { id: "education", label: "Education", color: "#8b5cf6" },
  { id: "social", label: "Social", color: "#ec4899" },
  { id: "shopping", label: "Shopping", color: "#14b8a6" },
  { id: "other", label: "Other", color: "#6b7280" },
] as const

export const ROLES = [
  { id: "user", label: "User" },
  { id: "admin", label: "Admin" },
  { id: "superuser", label: "Superuser" },
] as const

export const REMINDER_STATUSES = [
  { id: "active", label: "Active" },
  { id: "paused", label: "Paused" },
  { id: "completed", label: "Completed" },
  { id: "missed", label: "Missed" },
  { id: "cancelled", label: "Cancelled" },
] as const

export const APP_NAME = "ReminderBot Pro"
export const APP_TAGLINE = "Never Miss What Matters Most"
export const APP_DESCRIPTION = "Smart reminders across all your channels"
