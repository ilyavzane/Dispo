from pydantic import BaseModel, AwareDatetime, Field
from decimal import Decimal
from datetime import datetime


class LoadCreate(BaseModel):
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    pickup_date: AwareDatetime
    weight: Decimal = Field(max_digits=8, decimal_places=2, gt=0)
    rate: Decimal = Field(max_digits=8, decimal_places=2, gt=0)


class LoadOut(BaseModel):
    id: int
    origin: str
    destination: str
    pickup_date: AwareDatetime
    weight: Decimal
    rate: Decimal
    assigned_driver_id: int | None = None
    status: str
    created_at: datetime
    created_by: int


class LoadUpdate(BaseModel):
    origin: str | None = None
    destination: str | None = None
    pickup_date: AwareDatetime | None = None
    weight: Decimal | None = None
    rate: Decimal | None = None
