from datetime import datetime, timezone
from decimal import Decimal
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field, field_validator

from app.enums import LoadStatus


class LoadCreate(BaseModel):
    origin: str = Field(min_length=1)
    destination: str = Field(min_length=1)
    pickup_date: AwareDatetime
    weight: Decimal = Field(max_digits=8, decimal_places=2, gt=0)
    rate: Decimal = Field(max_digits=8, decimal_places=2, gt=0)

    @field_validator("pickup_date")
    @classmethod
    def not_in_past(cls, v):
        if v < datetime.now(timezone.utc):
            raise ValueError("Pickup date must be in the future")

        return v


class LoadOut(BaseModel):
    id: int
    origin: str
    destination: str
    pickup_date: AwareDatetime
    weight: Decimal
    rate: Decimal
    assigned_driver_id: int | None = None
    status: LoadStatus
    updated_at: datetime | None = None
    created_at: datetime
    created_by: int
    assigned_by: int | None = None


class LoadUpdate(BaseModel):
    origin: str | None = Field(default=None, min_length=1)
    destination: str | None = Field(default=None, min_length=1)
    pickup_date: AwareDatetime | None = None
    weight: Decimal | None = Field(default=None, max_digits=8, decimal_places=2, gt=0)
    rate: Decimal | None = Field(default=None, max_digits=8, decimal_places=2, gt=0)

    @field_validator("pickup_date")
    @classmethod
    def not_in_past(cls, v):
        if v is None:
            return None

        if v < datetime.now(timezone.utc):
            raise ValueError("Pickup date must be in the future")

        return v


class UpdateStatus(BaseModel):
    new_status: Literal[LoadStatus.IN_TRANSIT, LoadStatus.DELIVERED]
