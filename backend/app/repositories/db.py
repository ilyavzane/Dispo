import asyncpg

from app.config import DATABASE_URL

pool = None


async def create_pool():
    global pool
    pool = await asyncpg.create_pool(DATABASE_URL)


async def check_health():
    response = await pool.fetchval("SELECT 1")
    return response
