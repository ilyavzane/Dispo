import app.repository as repository
from app.security import generate_hash
from asyncpg import UniqueViolationError
from fastapi import HTTPException
from typing import Any


async def register(name: str, password: str, email: str, role: str) -> dict[str, Any]:
    hashed_password = generate_hash(password)

    try:
        response = await repository.add_new_user_to_db(
            name=name, password_hash=hashed_password, email=email, role=role
        )
    except UniqueViolationError:
        raise HTTPException(status_code=409, detail="Email already registered")

    return response
