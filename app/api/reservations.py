from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.reservation import ReservationCreate, ReservationList, ReservationRead
from app.services import reservation_service
from app.services.reservation_service import (
    ActiveReservationExistsError,
    ReservationNotActiveError,
    ReservationNotFoundError,
    SpotNotAvailableError,
    SpotNotFoundError,
    VehicleNotFoundError,
    VehicleOwnershipError,
)

router = APIRouter(prefix="/reservations", tags=["reservations"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]

_RESERVATION_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
)


@router.post("", response_model=ReservationRead, status_code=status.HTTP_201_CREATED)
def create_reservation(
    data: ReservationCreate, current_user: CurrentUser, db: DbSession
) -> ReservationRead:
    try:
        return reservation_service.create_reservation(db, current_user, data)
    except VehicleNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found"
        )
    except SpotNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parking spot not found"
        )
    except VehicleOwnershipError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Vehicle does not belong to the current user",
        )
    except SpotNotAvailableError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Parking spot is not available"
        )
    except ActiveReservationExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already has an active reservation",
        )


@router.get("", response_model=ReservationList)
def list_reservations(current_user: CurrentUser, db: DbSession) -> ReservationList:
    reservations = reservation_service.list_reservations(db, current_user)
    return ReservationList(items=reservations, total=len(reservations))


@router.get("/{reservation_id}", response_model=ReservationRead)
def get_reservation(
    reservation_id: int, current_user: CurrentUser, db: DbSession
) -> ReservationRead:
    try:
        return reservation_service.get_reservation(db, current_user, reservation_id)
    except ReservationNotFoundError:
        raise _RESERVATION_NOT_FOUND


@router.delete("/{reservation_id}", response_model=ReservationRead)
def cancel_reservation(
    reservation_id: int, current_user: CurrentUser, db: DbSession
) -> ReservationRead:
    try:
        return reservation_service.cancel_reservation(db, current_user, reservation_id)
    except ReservationNotFoundError:
        raise _RESERVATION_NOT_FOUND
    except ReservationNotActiveError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only an active reservation can be cancelled",
        )
