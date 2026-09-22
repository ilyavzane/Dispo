import asyncpg

from app.config import DATABASE_URL

pool = None


async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


async def check_health():
    try:
        await pool.fetchval("SELECT 1")

        return {"status": "ok", "database": "ok"}
    except (OSError, asyncpg.PostgresError):
        return {"status": "error", "database": "down"}
