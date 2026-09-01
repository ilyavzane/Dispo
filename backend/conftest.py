import os
from dotenv import load_dotenv
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.security import generate_hash

load_dotenv()
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL")


APPROVED_EMAIL = "approved@test.com"
REJECTED_EMAIL = "rejected@test.com"
ADMIN_EMAIL = "admin@test.com"

TEST_PASSWORD = "12345678"


async def _truncate_users():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    await conn.execute("TRUNCATE users RESTART IDENTITY CASCADE")
    await conn.close()


async def _create_new_user(
    name: str, password_hash: str, email: str, role: str, status: str
):
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    user_id = await conn.fetchval(
        "INSERT INTO users (name, password_hash, email, role, status) VALUES ($1, $2, $3, $4, $5) RETURNING id",
        name,
        password_hash,
        email,
        role,
        status,
    )
    await conn.close()

    return user_id


@pytest.fixture(autouse=True)
def clean_db():
    asyncio.run(_truncate_users())


@pytest.fixture
def approved_user():
    user_id = asyncio.run(
        _create_new_user(
            name="ilya",
            password_hash=generate_hash(TEST_PASSWORD),
            email=APPROVED_EMAIL,
            role="driver",
            status="approved",
        )
    )
    return {"email": APPROVED_EMAIL, "password": TEST_PASSWORD, "user_id": user_id}


@pytest.fixture
def rejected_user():
    user_id = asyncio.run(
        _create_new_user(
            name="ilya",
            password_hash=generate_hash(TEST_PASSWORD),
            email=REJECTED_EMAIL,
            role="driver",
            status="rejected",
        )
    )
    return {"email": REJECTED_EMAIL, "password": TEST_PASSWORD, "user_id": user_id}


@pytest.fixture
def admin_user():
    user_id = asyncio.run(
        _create_new_user(
            name="admin_test",
            password_hash=generate_hash(TEST_PASSWORD),
            email=ADMIN_EMAIL,
            role="admin",
            status="approved",
        )
    )
    return {"email": ADMIN_EMAIL, "password": TEST_PASSWORD, "user_id": user_id}


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
