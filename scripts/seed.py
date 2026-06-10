#!/usr/bin/env python3
"""ReminderBot Pro - Database Seeder

Creates default data: categories, demo user, sample reminders, subscription plans.

Usage:
    python -m scripts.seed
"""

import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    import asyncpg
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "asyncpg"])
    import asyncpg


DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://reminderbot:reminderbot_secret@localhost:5432/reminderbot",
)


def parse_database_url(url: str) -> dict:
    """Parse a PostgreSQL URL into connection parameters."""
    from urllib.parse import urlparse

    parsed = urlparse(url)
    host = parsed.hostname or "localhost"
    port = parsed.port or 5432
    user = parsed.username or "reminderbot"
    password = parsed.password or "reminderbot_secret"
    database = parsed.path.lstrip("/") or "reminderbot"
    return {
        "host": host,
        "port": port,
        "user": user,
        "password": password,
        "database": database,
    }


async def seed():
    conn = await asyncpg.connect(**parse_database_url(DATABASE_URL))

    existing = await conn.fetchval("SELECT COUNT(*) FROM categories")
    if existing and existing > 0:
        print(f"Database already seeded ({existing} categories found). Skipping.")
        await conn.close()
        return

    # Categories
    categories_data = [
        ("Work", "Work-related reminders and deadlines", "#4A90D9", True),
        ("School", "Academic deadlines and study reminders", "#7B68EE", True),
        ("Health", "Health, fitness, and medication reminders", "#2ECC71", True),
        ("Finance", "Bills, payments, and financial tasks", "#E74C3C", True),
        ("Family", "Family events and activities", "#F39C12", True),
        ("Personal", "Personal goals and errands", "#9B59B6", True),
        ("Travel", "Travel plans and itineraries", "#1ABC9C", True),
    ]

    category_ids = []
    for name, description, color, is_default in categories_data:
        cid = await conn.fetchval(
            """INSERT INTO categories (id, name, description, color, is_default, created_at)
               VALUES ($1, $2, $3, $4, $5, $6)
               ON CONFLICT (name) DO UPDATE SET name = EXCLUDED.name
               RETURNING id""",
            uuid4(),
            name,
            description,
            color,
            is_default,
            datetime.now(timezone.utc),
        )
        category_ids.append(cid)
    print(f"Created {len(category_ids)} categories")

    # Demo user
    demo_user_id = uuid4()
    await conn.execute(
        """INSERT INTO users (id, email, password_hash, full_name, is_active, is_verified, created_at)
           VALUES ($1, $2, $3, $4, $5, $6, $7)
           ON CONFLICT (email) DO NOTHING""",
        demo_user_id,
        "demo@reminderbot.com",
        "$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1Qlq5pVwLXFqGqJxMoM0nYx7qKuS",  # password: demo123
        "Demo User",
        True,
        True,
        datetime.now(timezone.utc),
    )
    print(f"Created demo user: demo@reminderbot.com / demo123")

    # Sample reminders
    now = datetime.now(timezone.utc)
    reminders_data = [
        (
            "Team standup meeting",
            "Daily standup with the engineering team",
            now + timedelta(hours=9),
            "high",
            category_ids[0],
        ),
        (
            "Submit quarterly report",
            "Complete and submit Q3 financial report",
            now + timedelta(days=3, hours=14),
            "urgent",
            category_ids[0],
        ),
        (
            "Gym session",
            "Evening workout at the gym",
            now + timedelta(hours=18),
            "medium",
            category_ids[2],
        ),
        (
            "Pay electricity bill",
            "Monthly electricity bill payment due",
            now + timedelta(days=5),
            "high",
            category_ids[3],
        ),
        (
            "Dentist appointment",
            "Regular dental checkup at 10 AM",
            now + timedelta(days=14, hours=10),
            "medium",
            category_ids[2],
        ),
        (
            "Buy groceries",
            "Weekly grocery shopping - milk, eggs, bread, vegetables",
            now + timedelta(days=2, hours=10),
            "low",
            category_ids[5],
        ),
        (
            "Flight booking",
            "Book flight tickets for holiday trip",
            now + timedelta(days=30),
            "medium",
            category_ids[6],
        ),
        (
            "Read 'Atomic Habits'",
            "Finish reading Chapter 5 this week",
            now + timedelta(days=7),
            "low",
            category_ids[5],
        ),
    ]

    for title, description, due_at, priority, category_id in reminders_data:
        await conn.execute(
            """INSERT INTO reminders (id, user_id, category_id, title, description, due_at, priority, status, created_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)""",
            uuid4(),
            demo_user_id,
            category_id,
            title,
            description,
            due_at,
            priority,
            "active",
            now,
        )
    print(f"Created {len(reminders_data)} sample reminders")

    # Subscription plans
    plans_data = [
        ("Free", 0, 10, 0, 1, "Basic free tier with limited reminders"),
        ("Pro", 9.99, 1000, 100, 10, "Pro tier with SMS and advanced features"),
        ("Business", 29.99, 10000, 500, 50, "Business tier for teams"),
    ]

    for name, price, max_reminders, sms_quota, team_members, description in plans_data:
        await conn.execute(
            """INSERT INTO subscription_plans (id, name, price, max_reminders, sms_quota, team_members, description, created_at)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
               ON CONFLICT (name) DO NOTHING""",
            uuid4(),
            name,
            price,
            max_reminders,
            sms_quota,
            team_members,
            description,
            now,
        )
    print(f"Created {len(plans_data)} subscription plans")

    await conn.close()
    print("\n✅ Database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
