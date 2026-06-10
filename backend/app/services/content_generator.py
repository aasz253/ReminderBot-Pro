from datetime import datetime
from typing import Optional

from app.models.reminder import Reminder
from app.models.payment import Payment


class ContentGenerator:
    def __init__(self):
        self.base_url = "https://reminderbot.com"

    def welcome_email(self, username: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="text-align: center; padding: 30px 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px;">
<h1 style="color: #fff; margin: 0;">Welcome to ReminderBot Pro!</h1>
</div>
<div style="padding: 30px 0;">
<p>Hi {username},</p>
<p>Welcome to <strong>ReminderBot Pro</strong>! We are excited to help you stay organized and never miss an important task again.</p>
<p>Here are a few things you can do to get started:</p>
<ul>
<li>Create your first reminder</li>
<li>Set up notification preferences (Telegram, WhatsApp, Email, SMS)</li>
<li>Explore our template marketplace for ready-made reminders</li>
<li>Invite team members for collaboration</li>
</ul>
<p>Ready to get started? <a href="{self.base_url}/dashboard" style="display: inline-block; padding: 12px 24px; background: #667eea; color: #fff; text-decoration: none; border-radius: 5px; margin-top: 10px;">Go to Dashboard</a></p>
</div>
<div style="border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999;">
<p>&copy; 2024 ReminderBot Pro. All rights reserved.</p>
</div>
</body>
</html>"""

    def verification_email(self, code: str) -> str:
        verify_url = f"{self.base_url}/verify-email?token={code}"
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="text-align: center; padding: 30px 0;">
<h2 style="color: #667eea;">Verify Your Email Address</h2>
</div>
<div style="padding: 20px 0;">
<p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
<div style="text-align: center; padding: 20px;">
<a href="{verify_url}" style="display: inline-block; padding: 14px 28px; background: #667eea; color: #fff; text-decoration: none; border-radius: 5px; font-size: 16px;">Verify Email</a>
</div>
<p>Or copy and paste this link in your browser:</p>
<p style="word-break: break-all; color: #667eea;">{verify_url}</p>
<p>This link will expire in 24 hours.</p>
</div>
<div style="border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999;">
<p>If you did not create an account, please ignore this email.</p>
</div>
</body>
</html>"""

    def password_reset_email(self, link: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="text-align: center; padding: 30px 0;">
<h2 style="color: #667eea;">Reset Your Password</h2>
</div>
<div style="padding: 20px 0;">
<p>We received a request to reset your password. Click the button below to set a new password:</p>
<div style="text-align: center; padding: 20px;">
<a href="{link}" style="display: inline-block; padding: 14px 28px; background: #667eea; color: #fff; text-decoration: none; border-radius: 5px; font-size: 16px;">Reset Password</a>
</div>
<p>Or copy and paste this link in your browser:</p>
<p style="word-break: break-all; color: #667eea;">{link}</p>
<p>This link will expire in 1 hour.</p>
</div>
<div style="border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999;">
<p>If you did not request a password reset, please ignore this email.</p>
</div>
</body>
</html>"""

    def reminder_notification_email(self, reminder: Reminder) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); padding: 20px; border-radius: 10px; text-align: center;">
<h1 style="color: #fff; margin: 0; font-size: 24px;">⏰ Reminder</h1>
</div>
<div style="padding: 30px 0;">
<h2 style="color: #333;">{reminder.title}</h2>
{'' if not reminder.description else f'<p style="font-size: 16px; color: #666;">{reminder.description}</p>'}
<div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 20px 0;">
<p style="margin: 5px 0;"><strong>Priority:</strong> <span style="color: {'#dc3545' if reminder.priority.value == 'urgent' else '#ffc107' if reminder.priority.value == 'high' else '#28a745' if reminder.priority.value == 'medium' else '#6c757d'};">{reminder.priority.value.upper()}</span></p>
<p style="margin: 5px 0;"><strong>Time:</strong> {reminder.reminder_time.strftime('%B %d, %Y at %I:%M %p %Z')}</p>
{'' if not reminder.is_recurring else f'<p style="margin: 5px 0;"><strong>Repeats:</strong> {reminder.repeat_type.value.title()}</p>'}
</div>
<a href="{self.base_url}/reminders/{reminder.id}" style="display: inline-block; padding: 12px 24px; background: #667eea; color: #fff; text-decoration: none; border-radius: 5px;">View Reminder</a>
</div>
<div style="border-top: 1px solid #eee; padding-top: 20px; font-size: 12px; color: #999;">
<p>Sent by ReminderBot Pro</p>
</div>
</body>
</html>"""

    def subscription_confirmation_email(self, plan: str, amount: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="text-align: center; padding: 30px 0; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); border-radius: 10px;">
<h1 style="color: #fff; margin: 0;">Subscription Confirmed!</h1>
</div>
<div style="padding: 30px 0;">
<p>Thank you for subscribing to <strong>ReminderBot Pro {plan.title()}</strong>!</p>
<div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
<h3 style="margin: 0 0 15px 0; color: #333;">Subscription Details</h3>
<p><strong>Plan:</strong> {plan.title()}</p>
<p><strong>Amount:</strong> {amount}</p>
<p><strong>Status:</strong> Active</p>
</div>
<p>You now have access to all {plan.title()} features. Start exploring!</p>
<a href="{self.base_url}/dashboard" style="display: inline-block; padding: 12px 24px; background: #667eea; color: #fff; text-decoration: none; border-radius: 5px;">Go to Dashboard</a>
</div>
</body>
</html>"""

    def payment_receipt_email(self, payment: Payment, invoice_url: str) -> str:
        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
<div style="text-align: center; padding: 30px 0; border-bottom: 2px solid #667eea;">
<h1 style="color: #667eea; margin: 0;">Payment Receipt</h1>
</div>
<div style="padding: 30px 0;">
<div style="background: #f8f9fa; padding: 20px; border-radius: 8px;">
<h3 style="margin: 0 0 15px 0;">Transaction Details</h3>
<table style="width: 100%; border-collapse: collapse;">
<tr><td style="padding: 8px 0; color: #666;">Receipt No:</td><td style="padding: 8px 0; text-align: right;">{payment.provider_reference}</td></tr>
<tr><td style="padding: 8px 0; color: #666;">Amount:</td><td style="padding: 8px 0; text-align: right; font-size: 18px; font-weight: bold;">{payment.currency} {payment.amount}</td></tr>
<tr><td style="padding: 8px 0; color: #666;">Payment Method:</td><td style="padding: 8px 0; text-align: right;">{payment.provider.value.upper()}</td></tr>
<tr><td style="padding: 8px 0; color: #666;">Date:</td><td style="padding: 8px 0; text-align: right;">{payment.created_at.strftime('%B %d, %Y %I:%M %p')}</td></tr>
<tr><td style="padding: 8px 0; color: #666;">Status:</td><td style="padding: 8px 0; text-align: right; color: #28a745;">{payment.status.value.upper()}</td></tr>
</table>
</div>
<div style="text-align: center; padding: 20px;">
<a href="{invoice_url}" style="display: inline-block; padding: 12px 24px; background: #667eea; color: #fff; text-decoration: none; border-radius: 5px;">Download Invoice</a>
</div>
</div>
</body>
</html>"""
