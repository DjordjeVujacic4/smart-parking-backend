from pydantic import BaseModel, ConfigDict

from app.models.enums import SpotStatus


class ParkingLocationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    address: str
    latitude: float | None
    longitude: float | None


class ParkingSpotRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_id: int
    spot_number: str
    status: SpotStatus
    location: ParkingLocationRead | None = None


class ParkingLocationStatistics(BaseModel):
    location_id: int
    total_spots: int
    available_spots: int
    occupied_spots: int
