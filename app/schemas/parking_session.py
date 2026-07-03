from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import SessionStatus


class CheckInRequest(BaseModel):
    reservation_id: int


class CheckOutRequest(BaseModel):
    parking_session_id: int


class ParkingSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reservation_id: int | None
    vehicle_id: int
    spot_id: int
    status: SessionStatus
    check_in_at: datetime
    check_out_at: datetime | None
