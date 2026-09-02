import asyncio
import os

import asyncpg
from app.security import generate_hash
from asyncpg import UniqueViolationError
from dotenv import load_dotenv

load_dotenv()

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

password_hash = generate_hash(ADMIN_PASSWORD)


async def create_admin():
    conn = await asyncpg.connect(os.getenv("DATABASE_URL"))

    try:
        await conn.execute(
            "INSERT INTO users (name, password_hash, email, role, status) VALUES ($1, $2, $3, $4, $5)",
            "administrator",
            password_hash,
            ADMIN_EMAIL,
            "admin",
            "approved",
        )

        print("Admin profile has been created")
    except UniqueViolationError:
        print("Admin profile has already been created")

    await conn.close()


asyncio.run(create_admin())
