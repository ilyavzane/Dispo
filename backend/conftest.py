import os
from dotenv import load_dotenv
import asyncio
import asyncpg
import pytest
from fastapi.testclient import TestClient

load_dotenv()
os.environ["DATABASE_URL"] = os.getenv("TEST_DATABASE_URL")

from app.main import app


async def _truncate_users():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    await conn.execute("TRUNCATE users RESTART IDENTITY CASCADE")
    await conn.close()


@pytest.fixture(autouse=True)
def clean_db():
    asyncio.run(_truncate_users())


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client
