import app.repository as repository
from app.security import generate_hash, check_password, create_jwt_token
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


async def login(email: str, password: str) -> dict[str, Any]:

    user_data = await repository.get_user_by_email(email)

    if user_data is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if not check_password(
        entered_password=password, password_hash=user_data["password_hash"]
    ):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if user_data["status"] == "pending":
        raise HTTPException(status_code=403, detail="Account is pending approval")

    if user_data["status"] == "rejected":
        raise HTTPException(status_code=403, detail="Account is rejected")

    token = create_jwt_token(user_data["id"])

    return {"access_token": token, "token_type": "bearer", "user": user_data}
