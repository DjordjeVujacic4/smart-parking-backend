from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import ReservationStatus
from app.schemas.parking_location import ParkingSpotRead
from app.schemas.vehicle import VehicleRead


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
    vehicle: VehicleRead
    parking_spot: ParkingSpotRead = Field(
        validation_alias="spot", serialization_alias="parking_spot"
    )


class ReservationList(BaseModel):
    items: list[ReservationRead]
    total: int
