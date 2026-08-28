from fastapi import APIRouter
import app.services.auth_service as auth_service
from app.schemas.users_schemas import UserRegistration, UserOut

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=UserOut, status_code=201)
async def register(user: UserRegistration):
    response = await auth_service.register(
        name=user.name, password=user.password, role=user.role, email=user.email.lower()
    )

    return response
