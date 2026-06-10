export interface User {
  id: string
  email: string
  name: string
  avatar_url?: string
  role: "user" | "admin" | "superuser"
  email_verified: boolean
  two_factor_enabled: boolean
  created_at: string
  updated_at: string
  subscription?: Subscription
}

export interface Subscription {
  id: string
  user_id: string
  plan_id: "free" | "premium" | "business"
  status: "active" | "cancelled" | "expired" | "trialing"
  current_period_start: string
  current_period_end: string
  cancel_at_period_end: boolean
  stripe_subscription_id?: string
  mpesa_reference?: string
  created_at: string
}

export interface Reminder {
  id: string
  user_id: string
  title: string
  description?: string
  due_date: string
  completed_at?: string
  priority: "low" | "medium" | "high" | "urgent"
  category: string
  status: "active" | "paused" | "completed" | "missed" | "cancelled"
  notification_channels: string[]
  repeat_type: "none" | "daily" | "weekdays" | "weekly" | "biweekly" | "monthly" | "yearly" | "custom"
  repeat_cron?: string
  repeat_end_date?: string
  team_id?: string
  created_at: string
  updated_at: string
  category_color?: string
}

export interface Category {
  id: string
  name: string
  color: string
  icon?: string
  user_id?: string
  is_default: boolean
}

export interface Notification {
  id: string
  reminder_id: string
  channel: string
  status: "pending" | "sent" | "failed" | "read"
  sent_at?: string
  error_message?: string
}

export interface Team {
  id: string
  name: string
  description?: string
  owner_id: string
  created_at: string
  member_count?: number
  members?: TeamMember[]
}

export interface TeamMember {
  id: string
  team_id: string
  user_id: string
  role: "owner" | "admin" | "member"
  user?: User
  joined_at: string
}

export interface TeamReminder extends Reminder {
  assigned_to?: string
  assigned_user?: User
}

export interface Payment {
  id: string
  user_id: string
  amount: number
  currency: string
  status: "pending" | "completed" | "failed" | "refunded"
  payment_method: "stripe" | "mpesa" | "airtel_money" | "paypal"
  plan_id: string
  reference: string
  created_at: string
}

export interface Transaction {
  id: string
  user_id: string
  type: "payment" | "refund" | "payout"
  amount: number
  currency: string
  status: string
  description: string
  created_at: string
}

export interface Analytics {
  total_reminders: number
  active_reminders: number
  completed_today: number
  missed_today: number
  upcoming_count: number
  completion_rate: number
}

export interface ProductivityScore {
  score: number
  trend: "up" | "down" | "stable"
  daily_streak: number
  weekly_completion_rate: number
}

export interface ReminderTrend {
  date: string
  created: number
  completed: number
  missed: number
}

export interface CategoryBreakdown {
  category: string
  count: number
  color: string
  percentage: number
}

export interface ApiResponse<T> {
  success: boolean
  data: T
  message?: string
  error?: string
}

export interface PaginatedResponse<T> {
  success: boolean
  data: T[]
  pagination: {
    page: number
    limit: number
    total: number
    total_pages: number
    has_next: boolean
    has_prev: boolean
  }
}

export interface CreateReminderInput {
  title: string
  description?: string
  due_date: string
  priority: "low" | "medium" | "high" | "urgent"
  category: string
  notification_channels: string[]
  repeat_type?: "none" | "daily" | "weekdays" | "weekly" | "biweekly" | "monthly" | "yearly" | "custom"
  repeat_cron?: string
  repeat_end_date?: string
  team_id?: string
}

export interface UpdateReminderInput extends Partial<CreateReminderInput> {
  id: string
  status?: "active" | "paused" | "completed" | "missed" | "cancelled"
}

export interface ReminderFilters {
  search?: string
  status?: string
  priority?: string
  category?: string
  date_from?: string
  date_to?: string
  sort_by?: string
  sort_order?: "asc" | "desc"
  page?: number
  limit?: number
}

export interface LoginInput {
  email: string
  password: string
  remember_me?: boolean
}

export interface RegisterInput {
  name: string
  email: string
  password: string
  confirm_password: string
}

export interface CreateTeamInput {
  name: string
  description?: string
}

export interface InviteMemberInput {
  email: string
  role: "admin" | "member"
}

export interface MpesaPaymentInput {
  phone_number: string
  amount: number
  plan_id: string
}

export interface DashboardStats {
  analytics: Analytics
  productivity: ProductivityScore
  upcoming_reminders: Reminder[]
  trends: ReminderTrend[]
  category_breakdown: CategoryBreakdown[]
}

export interface AdminStats {
  total_users: number
  active_subscriptions: number
  mrr: number
  delivery_success_rate: number
  users_trend: number
  subscriptions_trend: number
  mrr_trend: number
  delivery_trend: number
}

export interface SupportTicket {
  id: string
  user_id: string
  user?: User
  subject: string
  message: string
  status: "open" | "in_progress" | "resolved" | "closed"
  priority: "low" | "medium" | "high" | "urgent"
  created_at: string
  updated_at: string
}
