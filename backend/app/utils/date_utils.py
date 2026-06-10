import re
from datetime import datetime, timedelta, timezone, date
from typing import Optional, List

import pytz
from dateutil import parser as dateparser


def parse_natural_date(text: str) -> Optional[datetime]:
    text = text.strip().lower()

    now = datetime.now(timezone.utc)

    if text in ["now", "immediately", "asap"]:
        return now

    time_match = re.search(
        r'in\s+(\d+)\s*(minute|min|minutes|hour|hours|day|days|week|weeks|month|months|year|years)',
        text,
    )
    if time_match:
        amount = int(time_match.group(1))
        unit = time_match.group(2)
        unit_map = {
            "minute": "minutes", "min": "minutes", "minutes": "minutes",
            "hour": "hours", "hours": "hours",
            "day": "days", "days": "days",
            "week": "weeks", "weeks": "weeks",
            "month": "months", "months": "months",
            "year": "years", "years": "years",
        }
        kwargs = {unit_map.get(unit, "hours"): amount}
        return now + timedelta(**kwargs)

    if text == "tomorrow":
        return now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)

    if text == "today":
        return now.replace(hour=9, minute=0, second=0, microsecond=0)

    if text == "tonight":
        return now.replace(hour=20, minute=0, second=0, microsecond=0)

    if text == "next week":
        return now + timedelta(weeks=1)

    if text == "next month":
        return now + timedelta(days=30)

    if text == "next year":
        return now + timedelta(days=365)

    weekday_match = re.search(r'next\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)', text)
    if weekday_match:
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        target_day = days.index(weekday_match.group(1))
        current_day = now.weekday()
        days_ahead = target_day - current_day
        if days_ahead <= 0:
            days_ahead += 7
        return now.replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=days_ahead)

    time_match = re.search(r'(?:at|by)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', text)
    if time_match:
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        ampm = time_match.group(3)
        if ampm:
            if ampm.lower() == "pm" and hour < 12:
                hour += 12
            elif ampm.lower() == "am" and hour == 12:
                hour = 0
        target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if target <= now:
            target += timedelta(days=1)
        return target

    if re.search(r'\bin\s+(?:an?\s+)?(hour|hr)\b', text):
        return now + timedelta(hours=1)

    if re.search(r'\bin\s+(?:an?\s+)?(minute|min)\b', text):
        return now + timedelta(minutes=1)

    try:
        parsed = dateparser.parse(text, default=now)
        if parsed:
            if parsed.tzinfo is None:
                parsed = parsed.replace(tzinfo=timezone.utc)
            return parsed
    except Exception:
        pass

    return None


def format_reminder_time(dt: datetime, tz: str = "UTC") -> str:
    try:
        user_tz = pytz.timezone(tz)
        local_dt = dt.astimezone(user_tz)
        return local_dt.strftime("%B %d, %Y at %I:%M %p %Z")
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M UTC")


def get_next_cron_run(expression: str) -> Optional[datetime]:
    try:
        from croniter import croniter
        cron = croniter(expression, datetime.now(timezone.utc))
        return cron.get_next(datetime)
    except ImportError:
        return None
    except Exception:
        return None


def calculate_repeat_dates(
    start: datetime,
    repeat_type: str,
    interval: int = 1,
    end_date: Optional[datetime] = None,
    max_count: int = 10,
) -> List[datetime]:
    dates = []
    current = start

    if end_date and end_date.tzinfo is None:
        end_date = end_date.replace(tzinfo=timezone.utc)

    for _ in range(max_count):
        if repeat_type == "daily":
            current = current + timedelta(days=interval)
        elif repeat_type == "weekly":
            current = current + timedelta(weeks=interval)
        elif repeat_type == "monthly":
            month = current.month + interval
            year = current.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            try:
                current = current.replace(year=year, month=month)
            except ValueError:
                import calendar
                last_day = calendar.monthrange(year, month)[1]
                current = current.replace(year=year, month=month, day=last_day)
        elif repeat_type == "yearly":
            current = current.replace(year=current.year + interval)
        else:
            break

        if end_date and current > end_date:
            break

        dates.append(current)

    return dates


def is_dst_safe(dt: datetime, tz: str) -> bool:
    try:
        user_tz = pytz.timezone(tz)
        user_tz.localize(dt.replace(tzinfo=None))
        return True
    except Exception:
        return False


def get_user_now(user_timezone: str) -> datetime:
    try:
        tz = pytz.timezone(user_timezone)
        return datetime.now(tz)
    except Exception:
        return datetime.now(timezone.utc)


def timeago(timestamp: datetime, reference: Optional[datetime] = None) -> str:
    if reference is None:
        reference = datetime.now(timezone.utc)

    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)
    if reference.tzinfo is None:
        reference = reference.replace(tzinfo=timezone.utc)

    diff = reference - timestamp
    seconds = diff.total_seconds()

    if seconds < 0:
        return "in the future"

    if seconds < 60:
        return "just now"
    if seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    if seconds < 86400:
        hours = int(seconds // 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    if seconds < 2592000:
        days = int(seconds // 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
    if seconds < 31536000:
        months = int(seconds // 2592000)
        return f"{months} month{'s' if months != 1 else ''} ago"
    years = int(seconds // 31536000)
    return f"{years} year{'s' if years != 1 else ''} ago"
