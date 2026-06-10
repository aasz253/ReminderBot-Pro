import pytest
from httpx import AsyncClient
from datetime import datetime, timezone, timedelta


@pytest.mark.asyncio
async def test_create_reminder(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/reminders", headers=auth_headers, json={
        "title": "Test Reminder",
        "description": "Test Description",
        "reminder_time": (datetime.now(timezone.utc) + timedelta(hours=2)).isoformat(),
        "timezone": "UTC",
        "priority": "medium",
        "notification_type": "email",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test Reminder"
    assert data["is_active"] == True
    assert data["is_completed"] == False


@pytest.mark.asyncio
async def test_list_reminders(client: AsyncClient, auth_headers, sample_reminder):
    response = await client.get("/api/v1/reminders", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_reminder(client: AsyncClient, auth_headers, sample_reminder):
    response = await client.get(f"/api/v1/reminders/{sample_reminder.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["title"] == "Test Reminder"


@pytest.mark.asyncio
async def test_update_reminder(client: AsyncClient, auth_headers, sample_reminder):
    response = await client.put(
        f"/api/v1/reminders/{sample_reminder.id}",
        headers=auth_headers,
        json={"title": "Updated Reminder", "priority": "high"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Reminder"
    assert response.json()["priority"] == "high"


@pytest.mark.asyncio
async def test_complete_reminder(client: AsyncClient, auth_headers, sample_reminder):
    response = await client.post(
        f"/api/v1/reminders/{sample_reminder.id}/complete",
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["is_completed"] == True


@pytest.mark.asyncio
async def test_pause_resume_reminder(client: AsyncClient, auth_headers, sample_reminder):
    pause_resp = await client.post(
        f"/api/v1/reminders/{sample_reminder.id}/pause",
        headers=auth_headers,
    )
    assert pause_resp.status_code == 200
    assert pause_resp.json()["is_paused"] == True

    resume_resp = await client.post(
        f"/api/v1/reminders/{sample_reminder.id}/resume",
        headers=auth_headers,
    )
    assert resume_resp.status_code == 200
    assert resume_resp.json()["is_paused"] == False


@pytest.mark.asyncio
async def test_delete_reminder(client: AsyncClient, auth_headers, sample_reminder):
    response = await client.delete(
        f"/api/v1/reminders/{sample_reminder.id}",
        headers=auth_headers,
    )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_parse_natural_language(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/reminders/parse", headers=auth_headers, json={
        "query": "remind me to buy groceries in 15 minutes",
    })
    assert response.status_code == 200
    data = response.json()
    assert "title" in data
    assert "reminder_time" in data
    assert "priority" in data


@pytest.mark.asyncio
async def test_upcoming_reminders(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/reminders/upcoming", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_bulk_action(client: AsyncClient, auth_headers, sample_reminder):
    response = await client.post("/api/v1/reminders/bulk-action", headers=auth_headers, json={
        "reminder_ids": [str(sample_reminder.id)],
        "action": "complete",
    })
    assert response.status_code == 200
    assert response.json()["count"] == 1


@pytest.mark.asyncio
async def test_reminder_quota_validation(client: AsyncClient, auth_headers):
    from app.models.user import User
    from app.services.subscription_service import PLAN_LIMITS

    for _ in range(5):
        await client.post("/api/v1/reminders", headers=auth_headers, json={
            "title": f"Quota Test Reminder",
            "reminder_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
            "timezone": "UTC",
        })

    response = await client.post("/api/v1/reminders", headers=auth_headers, json={
        "title": "Over Quota Reminder",
        "reminder_time": (datetime.now(timezone.utc) + timedelta(days=1)).isoformat(),
        "timezone": "UTC",
    })
    assert response.status_code == 403
