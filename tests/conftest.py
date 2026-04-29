import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import AsyncGenerator

import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
async def test_engine():
    """Создает тестовый engine на всю сессию тестов"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.create_all(sync_conn, checkfirst=True))

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(lambda sync_conn: Base.metadata.drop_all(sync_conn))

    await engine.dispose()


@pytest.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    test_session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with test_session_factory() as session:
        yield session
        if session.in_transaction():
            await session.rollback()
        await session.close()


@pytest.fixture(scope="function")
async def async_client(test_session):
    async def override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test"
    ) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
async def test_wallet(async_client):
    """Создает тестовый кошелек и возвращает его ID"""
    response = await async_client.post("/api/v1/wallets/create-wallet")
    assert response.status_code == 201
    return response.json()["wallet_id"]

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test (requires database)"
    )
    config.addinivalue_line(
        "markers",
        "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers",
        "unit: mark test as unit test (fast, no database)"
    )
