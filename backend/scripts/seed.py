import asyncio

import asyncpg
from asyncpg import UniqueViolationError

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, DATABASE_URL
from app.security import generate_hash

password_hash = generate_hash(ADMIN_PASSWORD)


async def create_admin():
    conn = await asyncpg.connect(DATABASE_URL)

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
