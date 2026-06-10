import asyncio
import pytest
from typing import AsyncGenerator, Generator
from uuid import uuid4

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.core.config import settings
from app.core.security import get_password_hash
from app.main import app
from app.models.user import User


TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def test_db(test_engine) -> AsyncGenerator[AsyncSession, None]:
    session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )()
    try:
        yield session
    finally:
        await session.rollback()
        await session.close()


@pytest.fixture
async def client(test_db) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        yield test_db

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
async def sample_user(test_db: AsyncSession) -> User:
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        full_name="Test User",
        hashed_password=get_password_hash("TestPass123"),
        is_active=True,
        is_verified=True,
    )
    test_db.add(user)
    await test_db.commit()
    return user


@pytest.fixture
async def auth_headers(client: AsyncClient, sample_user: User) -> dict:
    from app.core.security import create_access_token
    token = create_access_token({"sub": str(sample_user.id), "email": sample_user.email})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def sample_reminder(test_db: AsyncSession, sample_user: User):
    from app.models.reminder import Reminder
    from datetime import datetime, timezone, timedelta

    reminder = Reminder(
        id=uuid4(),
        user_id=sample_user.id,
        title="Test Reminder",
        description="Test Description",
        reminder_time=datetime.now(timezone.utc) + timedelta(hours=1),
        timezone="UTC",
    )
    test_db.add(reminder)
    await test_db.commit()
    return reminder
