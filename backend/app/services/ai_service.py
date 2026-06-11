import re
import json
from datetime import datetime, timedelta, timezone
from typing import Optional, List, Tuple
from uuid import UUID

import httpx

from app.core.config import settings
from app.models.user import User
from app.models.reminder import Reminder, Priority


class AIService:
    def __init__(self):
        self.use_openai = bool(settings.OPENAI_API_KEY)
        self.use_openrouter = bool(settings.OPENROUTER_API_KEY)
        self.use_ai = self.use_openai or self.use_openrouter

        if self.use_openai:
            self.models = ["gpt-3.5-turbo"]
            self.api_key = settings.OPENAI_API_KEY
            self.api_base = "https://api.openai.com/v1"
        elif self.use_openrouter:
            self.models = [settings.OPENROUTER_MODEL, *settings.OPENROUTER_FALLBACK_MODELS]
            self.api_key = settings.OPENROUTER_API_KEY
            self.api_base = "https://openrouter.ai/api/v1"
        else:
            self.models = []
            self.api_key = None
            self.api_base = None

    async def _chat_completion(self, messages: list, temperature: float = 0.1) -> Optional[dict]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.use_openrouter:
            headers["HTTP-Referer"] = settings.FRONTEND_URL
            headers["X-Title"] = settings.APP_NAME

        for model in self.models:
            try:
                async with httpx.AsyncClient(timeout=15) as client:
                    response = await client.post(
                        f"{self.api_base}/chat/completions",
                        headers=headers,
                        json={"model": model, "messages": messages, "temperature": temperature},
                    )
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        return json.loads(content)
            except Exception:
                continue
        return None

    async def parse_natural_language(self, query: str) -> dict:
        if self.use_ai:
            try:
                return await self._parse_with_ai(query)
            except Exception:
                return self._parse_rule_based(query)
        return self._parse_rule_based(query)

    async def _parse_with_ai(self, query: str) -> dict:
        prompt = (
            "Parse the following reminder request and return JSON with fields: "
            "title, description, reminder_time (ISO 8601 with timezone), priority (low/medium/high/urgent). "
            f"Current time is {datetime.now(timezone.utc).isoformat()}. "
            f"Query: {query}"
        )

        parsed = await self._chat_completion([
            {"role": "system", "content": "You are a reminder parsing assistant. Return only JSON."},
            {"role": "user", "content": prompt},
        ])
        if parsed:
            return {
                "title": parsed.get("title", query),
                "reminder_time": parsed.get("reminder_time"),
                "timezone": parsed.get("timezone", "UTC"),
                "priority": parsed.get("priority", "medium"),
                "description": parsed.get("description"),
            }

        return self._parse_rule_based(query)

    def _parse_rule_based(self, query: str) -> dict:
        from app.utils.date_utils import parse_natural_date

        query_lower = query.lower().strip()

        time_match = re.search(
            r'(?:in\s+)?(\d+)\s*(minute|min|minutes|hour|hours|day|days|week|weeks|month|months)\s*(?:from now)?(?:\s*,?\s*)?',
            query_lower,
        )
        at_match = re.search(r'(?:at|by|for)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?', query_lower)
        tomorrow_match = re.search(r'\btomorrow\b', query_lower)
        today_match = re.search(r'\btoday\b', query_lower)
        next_match = re.search(r'\bnext\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b', query_lower)

        reminder_time = datetime.now(timezone.utc) + timedelta(hours=1)

        if time_match:
            amount = int(time_match.group(1))
            unit = time_match.group(2)
            unit_map = {
                "minute": "minutes", "min": "minutes", "minutes": "minutes",
                "hour": "hours", "hours": "hours",
                "day": "days", "days": "days",
                "week": "weeks", "weeks": "weeks",
                "month": "months", "months": "months",
            }
            unit = unit_map.get(unit, "hours")
            kwargs = {unit: amount}
            reminder_time = datetime.now(timezone.utc) + timedelta(**kwargs)
        elif at_match:
            hour = int(at_match.group(1))
            minute = int(at_match.group(2)) if at_match.group(2) else 0
            ampm = at_match.group(3)
            if ampm:
                if ampm.lower() == "pm" and hour < 12:
                    hour += 12
                elif ampm.lower() == "am" and hour == 12:
                    hour = 0

            now = datetime.now(timezone.utc)
            reminder_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if reminder_time <= now:
                reminder_time += timedelta(days=1)
        elif tomorrow_match:
            reminder_time = datetime.now(timezone.utc).replace(
                hour=9, minute=0, second=0, microsecond=0
            ) + timedelta(days=1)

        priority_map = {
            "urgent": "urgent", "asap": "urgent", "critical": "urgent",
            "important": "high", "high": "high",
            "medium": "medium",
            "low": "low", "minor": "low",
        }
        priority = "medium"
        for word, pri in priority_map.items():
            if word in query_lower:
                priority = pri
                break

        title = query
        for prefix in ["remind me to ", "remind me that ", "remind me about ", "set a reminder for ", "set a reminder to "]:
            if title.lower().startswith(prefix):
                title = title[len(prefix):]
                break

        for suffix in [" in 15 minutes", " in 30 minutes", " in an hour", " in 1 hour", " tomorrow", " today"]:
            if title.lower().endswith(suffix):
                title = title[:-len(suffix)]
                break

        time_extract_pattern = re.compile(
            r'\s+(?:in|at|by|for|on)\s+\d+.*$|\s+tomorrow|\s+next\s+\w+',
            re.IGNORECASE,
        )
        title = time_extract_pattern.sub("", title).strip().capitalize()

        if not title:
            title = query

        return {
            "title": title,
            "reminder_time": reminder_time.isoformat(),
            "timezone": "UTC",
            "priority": priority,
            "description": None,
        }

    async def generate_suggestions(self, user: User) -> List[dict]:
        suggestions = [
            {"title": "Drink water", "description": "Stay hydrated!", "priority": "low", "category": "health"},
            {"title": "Daily standup meeting", "description": "Team sync", "priority": "high", "category": "work"},
            {"title": "Read for 30 minutes", "description": "Personal development", "priority": "medium", "category": "personal"},
            {"title": "Review weekly goals", "description": "Sunday planning", "priority": "medium", "category": "work"},
            {"title": "Take medication", "description": "Health reminder", "priority": "high", "category": "health"},
        ]

        if self.use_ai:
            try:
                ai_suggestions = await self._generate_ai_suggestions(user)
                if ai_suggestions:
                    return ai_suggestions
            except Exception:
                pass

        return suggestions

    async def _generate_ai_suggestions(self, user: User) -> Optional[List[dict]]:
        prompt = (
            "Generate 5 personalized reminder suggestions for a productivity app user. "
            "Return JSON array of objects with title, description, priority (low/medium/high/urgent), category."
        )
        return await self._chat_completion([
            {"role": "system", "content": "Return only JSON."},
            {"role": "user", "content": prompt},
        ], temperature=0.7)

    async def generate_study_schedule(self, exam_date: datetime, subjects: List[str]) -> List[dict]:
        now = datetime.now(timezone.utc)
        days_until_exam = (exam_date - now).days
        if days_until_exam <= 0:
            return [{"title": "Exam is today or past!", "reminder_time": now.isoformat(), "priority": "urgent"}]

        schedule = []
        days_per_subject = max(1, days_until_exam // len(subjects))

        for i, subject in enumerate(subjects):
            study_date = now + timedelta(days=i * days_per_subject)
            schedule.append({
                "title": f"Study {subject}",
                "description": f"Study session for {subject}",
                "reminder_time": study_date.replace(hour=10, minute=0, second=0, microsecond=0).isoformat(),
                "priority": "high",
                "category": "study",
                "duration_minutes": 120,
            })

        schedule.append({
            "title": "Final review before exam",
            "description": "Review all subjects",
            "reminder_time": exam_date.replace(hour=8, minute=0, second=0, microsecond=0).isoformat(),
            "priority": "urgent",
            "category": "study",
            "duration_minutes": 180,
        })

        return schedule

    async def analyze_productivity(self, user_id: UUID) -> dict:
        return {
            "analysis": "Productivity analysis requires historical data collection.",
            "suggestions": [
                "Set specific time blocks for recurring tasks",
                "Use priority levels to focus on important tasks first",
                "Review and adjust your reminder times for better consistency",
            ],
            "peak_hours": "Morning hours (8-11 AM) typically show highest completion rates",
            "recommendation": "Try grouping similar tasks together for better focus",
        }

    async def classify_reminder(self, title: str) -> str:
        categories = {
            "work": ["meeting", "deadline", "project", "report", "email", "call", "presentation", "client"],
            "health": ["medication", "exercise", "workout", "gym", "yoga", "doctor", "dentist", "walk", "water"],
            "personal": ["read", "book", "hobby", "meditate", "journal", "reflect"],
            "finance": ["bill", "payment", "invoice", "budget", "tax", "subscription", "renew"],
            "social": ["birthday", "anniversary", "party", "dinner", "lunch", "coffee", "friend", "family"],
            "study": ["study", "class", "course", "lesson", "tutorial", "homework", "assignment", "exam", "test"],
            "shopping": ["buy", "purchase", "order", "groceries", "shop", "store"],
            "travel": ["flight", "hotel", "booking", "trip", "travel", "pack", "departure"],
        }

        title_lower = title.lower()
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for kw in keywords if kw in title_lower)
            if score > 0:
                scores[category] = score

        if scores:
            return max(scores, key=scores.get)
        return "general"
