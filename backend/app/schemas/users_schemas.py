from pydantic import BaseModel, Field, EmailStr
from typing import Literal


class UserRegistration(BaseModel):
    name: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=36)
    email: EmailStr = Field(max_length=254)
    role: Literal["driver", "dispatcher"]


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: str
    status: Literal["pending", "approved", "rejected"]
