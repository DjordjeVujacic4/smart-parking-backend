from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ReservationStatus


class ReservationCreate(BaseModel):
    vehicle_id: int
    spot_id: int


class ReservationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    vehicle_id: int
    spot_id: int
    status: ReservationStatus
    expires_at: datetime
    created_at: datetime


class ReservationList(BaseModel):
    items: list[ReservationRead]
    total: int
