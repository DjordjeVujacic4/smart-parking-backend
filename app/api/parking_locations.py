from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.parking_location import (
    ParkingLocationRead,
    ParkingLocationStatistics,
    ParkingSpotRead,
)
from app.services import parking_location_service
from app.services.parking_location_service import LocationNotFoundError

router = APIRouter(prefix="/locations", tags=["parking-locations"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Parking location not found"
)


@router.get("", response_model=list[ParkingLocationRead])
def list_locations(current_user: CurrentUser, db: DbSession) -> list[ParkingLocationRead]:
    return parking_location_service.list_locations(db)


@router.get("/{location_id}", response_model=ParkingLocationRead)
def get_location(
    location_id: int, current_user: CurrentUser, db: DbSession
) -> ParkingLocationRead:
    try:
        return parking_location_service.get_location(db, location_id)
    except LocationNotFoundError:
        raise _NOT_FOUND


@router.get("/{location_id}/spots", response_model=list[ParkingSpotRead])
def list_spots(
    location_id: int, current_user: CurrentUser, db: DbSession
) -> list[ParkingSpotRead]:
    try:
        return parking_location_service.list_spots(db, location_id)
    except LocationNotFoundError:
        raise _NOT_FOUND


@router.get("/{location_id}/spots/available", response_model=list[ParkingSpotRead])
def list_available_spots(
    location_id: int, current_user: CurrentUser, db: DbSession
) -> list[ParkingSpotRead]:
    try:
        return parking_location_service.list_available_spots(db, location_id)
    except LocationNotFoundError:
        raise _NOT_FOUND


@router.get("/{location_id}/statistics", response_model=ParkingLocationStatistics)
def get_statistics(
    location_id: int, current_user: CurrentUser, db: DbSession
) -> ParkingLocationStatistics:
    try:
        return parking_location_service.get_statistics(db, location_id)
    except LocationNotFoundError:
        raise _NOT_FOUND
