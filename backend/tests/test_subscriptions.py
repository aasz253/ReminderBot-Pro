import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_plans(client: AsyncClient):
    response = await client.get("/api/v1/subscriptions/plans")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    plan_codes = [p["code"] for p in data]
    assert "free" in plan_codes
    assert "premium" in plan_codes
    assert "business" in plan_codes


@pytest.mark.asyncio
async def test_get_my_subscription(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/subscriptions/my", headers=auth_headers)
    assert response.status_code in [200, 404]


@pytest.mark.asyncio
async def test_create_subscription(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/subscriptions", headers=auth_headers, json={
        "plan": "premium",
        "payment_provider": "stripe",
        "payment_reference": "test_sub_ref_123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["plan"] == "premium"
    assert data["status"] in ["active", "trial"]


@pytest.mark.asyncio
async def test_get_limits(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/subscriptions/limits", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "max_reminders" in data
    assert "max_teams" in data


@pytest.mark.asyncio
async def test_cancel_subscription(client: AsyncClient, auth_headers):
    await client.post("/api/v1/subscriptions", headers=auth_headers, json={
        "plan": "premium",
        "payment_provider": "stripe",
        "payment_reference": "cancel_test_ref",
    })

    response = await client.post("/api/v1/subscriptions/cancel", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


@pytest.mark.asyncio
async def test_upgrade_subscription(client: AsyncClient, auth_headers):
    await client.post("/api/v1/subscriptions", headers=auth_headers, json={
        "plan": "premium",
        "payment_provider": "stripe",
        "payment_reference": "upgrade_test_ref",
    })

    response = await client.post("/api/v1/subscriptions/upgrade", headers=auth_headers, json={
        "plan": "business",
        "payment_provider": "stripe",
        "payment_reference": "upgraded_ref_456",
    })
    assert response.status_code == 200
    assert response.json()["plan"] == "business"
