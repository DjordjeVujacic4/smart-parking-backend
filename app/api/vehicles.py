from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from app.services import vehicle_service
from app.services.vehicle_service import (
    DuplicateLicensePlateError,
    VehicleNotFoundError,
)

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

_DUPLICATE_PLATE = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="License plate already registered"
)
_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
)


@router.post("", response_model=VehicleRead, status_code=status.HTTP_201_CREATED)
def create_vehicle(
    data: VehicleCreate, current_user: CurrentUser, db: DbSession
) -> VehicleRead:
    try:
        return vehicle_service.create_vehicle(db, current_user, data)
    except DuplicateLicensePlateError:
        raise _DUPLICATE_PLATE


@router.get("", response_model=list[VehicleRead])
def list_vehicles(current_user: CurrentUser, db: DbSession) -> list[VehicleRead]:
    return vehicle_service.list_vehicles(db, current_user)


@router.get("/{vehicle_id}", response_model=VehicleRead)
def get_vehicle(
    vehicle_id: int, current_user: CurrentUser, db: DbSession
) -> VehicleRead:
    try:
        return vehicle_service.get_vehicle(db, current_user, vehicle_id)
    except VehicleNotFoundError:
        raise _NOT_FOUND


@router.patch("/{vehicle_id}", response_model=VehicleRead)
def update_vehicle(
    vehicle_id: int, data: VehicleUpdate, current_user: CurrentUser, db: DbSession
) -> VehicleRead:
    try:
        return vehicle_service.update_vehicle(db, current_user, vehicle_id, data)
    except VehicleNotFoundError:
        raise _NOT_FOUND
    except DuplicateLicensePlateError:
        raise _DUPLICATE_PLATE


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vehicle(
    vehicle_id: int, current_user: CurrentUser, db: DbSession
) -> None:
    try:
        vehicle_service.delete_vehicle(db, current_user, vehicle_id)
    except VehicleNotFoundError:
        raise _NOT_FOUND
