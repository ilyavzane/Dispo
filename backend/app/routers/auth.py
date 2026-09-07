from fastapi import APIRouter

import app.services.auth as auth_service
from app.schemas.users_schemas import LoginOut, UserLogin, UserOut, UserRegistration

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserOut, status_code=201)
async def register(user: UserRegistration):
    response = await auth_service.register(
        name=user.name, password=user.password, role=user.role, email=user.email.lower()
    )

    return response


@auth_router.post("/login", status_code=200, response_model=LoginOut)
async def login(user: UserLogin):
    response = await auth_service.login(user.email.lower(), user.password)

    return response
