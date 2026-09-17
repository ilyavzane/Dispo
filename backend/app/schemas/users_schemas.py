from typing import Literal

from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.enums import Roles, Statuses


class UserRegistration(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=36)
    email: EmailStr = Field(max_length=254)
    role: Literal[Roles.DRIVER, Roles.DISPATCHER]


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: Roles
    status: Literal[Statuses.PENDING, Statuses.APPROVED, Statuses.REJECTED]
    created_at: datetime


class DriversOut(UserOut):
    is_available: bool


class UserLogin(BaseModel):
    email: EmailStr = Field(max_length=254)
    password: str


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class UserStatusUpdate(BaseModel):
    new_status: Literal[Statuses.APPROVED, Statuses.REJECTED]
