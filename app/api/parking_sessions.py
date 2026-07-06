from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.parking_session import (
    CheckInRequest,
    CheckOutRequest,
    ParkingSessionRead,
)
from app.services import parking_session_service
from app.services.parking_session_service import (
    ActiveSessionExistsError,
    ReservationAlreadyParkedError,
    ReservationExpiredError,
    ReservationNotActiveError,
    ReservationNotFoundError,
    SessionAlreadyCompletedError,
    SessionNotFoundError,
    SpotNotReservedError,
)

router = APIRouter(tags=["parking-sessions"])

CurrentUser = Annotated[User, Depends(get_current_user)]
DbSession = Annotated[Session, Depends(get_db)]


def _conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_409_CONFLICT, detail=detail)


@router.post("/checkin", response_model=ParkingSessionRead, status_code=status.HTTP_201_CREATED)
def check_in(
    data: CheckInRequest, current_user: CurrentUser, db: DbSession
) -> ParkingSessionRead:
    try:
        return parking_session_service.check_in(db, current_user, data.reservation_id)
    except ReservationNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Reservation not found"
        )
    except ReservationAlreadyParkedError:
        raise _conflict("Reservation already parked")
    except ReservationExpiredError:
        raise _conflict("Reservation has expired")
    except ReservationNotActiveError:
        raise _conflict("Reservation is not active")
    except SpotNotReservedError:
        raise _conflict("Parking spot is not reserved")
    except ActiveSessionExistsError:
        raise _conflict("Reservation already has a parking session")


@router.post("/checkout", response_model=ParkingSessionRead)
def check_out(
    data: CheckOutRequest, current_user: CurrentUser, db: DbSession
) -> ParkingSessionRead:
    try:
        return parking_session_service.check_out(
            db, current_user, data.parking_session_id
        )
    except SessionNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Parking session not found"
        )
    except SessionAlreadyCompletedError:
        raise _conflict("Parking session already completed")
