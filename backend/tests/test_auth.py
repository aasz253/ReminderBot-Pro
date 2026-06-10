import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post("/api/v1/auth/register", json={
        "email": "newuser@example.com",
        "password": "TestPass123",
        "username": "newuser",
        "full_name": "New User",
    })
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_register_duplicate(client: AsyncClient):
    await client.post("/api/v1/auth/register", json={
        "email": "duplicate@example.com",
        "password": "TestPass123",
        "username": "duplicate1",
    })
    response = await client.post("/api/v1/auth/register", json={
        "email": "duplicate@example.com",
        "password": "TestPass123",
        "username": "duplicate2",
    })
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, sample_user):
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "TestPass123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_invalid_password(client: AsyncClient):
    response = await client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPass123",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient, auth_headers):
    response = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["username"] == "testuser"


@pytest.mark.asyncio
async def test_update_profile(client: AsyncClient, auth_headers):
    response = await client.put("/api/v1/auth/me", headers=auth_headers, json={
        "full_name": "Updated Name",
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Updated Name"


@pytest.mark.asyncio
async def test_forgot_password(client: AsyncClient):
    response = await client.post("/api/v1/auth/forgot-password", json={
        "email": "test@example.com",
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_change_password(client: AsyncClient, auth_headers):
    response = await client.post("/api/v1/auth/change-password", headers=auth_headers, json={
        "current_password": "TestPass123",
        "new_password": "NewPassword123",
    })
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_unauthorized_access(client: AsyncClient):
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient):
    register_resp = await client.post("/api/v1/auth/register", json={
        "email": "refresh_test@example.com",
        "password": "TestPass123",
        "username": "refreshuser",
    })
    refresh_token = register_resp.json()["refresh_token"]

    response = await client.post("/api/v1/auth/refresh-token", json={
        "refresh_token": refresh_token,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
