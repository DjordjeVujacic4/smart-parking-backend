from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.enums import ReservationStatus, SessionStatus, SpotStatus
from app.models.parking_session import ParkingSession
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.user import User


class ReservationNotFoundError(Exception):
    pass


class ReservationAlreadyFulfilledError(Exception):
    pass


class ReservationExpiredError(Exception):
    pass


class ReservationNotActiveError(Exception):
    pass


class SpotNotReservedError(Exception):
    pass


class ActiveSessionExistsError(Exception):
    pass


class SessionNotFoundError(Exception):
    pass


class SessionAlreadyCompletedError(Exception):
    pass


def check_in(db: Session, user: User, reservation_id: int) -> ParkingSession:
    reservation = db.scalar(
        select(Reservation)
        .where(Reservation.id == reservation_id, Reservation.user_id == user.id)
        .with_for_update()
    )
    if reservation is None:
        raise ReservationNotFoundError(reservation_id)
    if reservation.status == ReservationStatus.FULFILLED:
        raise ReservationAlreadyFulfilledError(reservation_id)
    if reservation.status == ReservationStatus.EXPIRED:
        raise ReservationExpiredError(reservation_id)
    if reservation.status != ReservationStatus.ACTIVE:
        raise ReservationNotActiveError(reservation_id)

    now = datetime.now(timezone.utc)
    if reservation.expires_at < now:
        raise ReservationExpiredError(reservation_id)

    spot = db.scalar(
        select(ParkingSpot)
        .where(ParkingSpot.id == reservation.spot_id)
        .with_for_update()
    )
    if spot is None or spot.status != SpotStatus.RESERVED:
        raise SpotNotReservedError(reservation.spot_id)

    existing_session = db.scalar(
        select(ParkingSession).where(ParkingSession.reservation_id == reservation.id)
    )
    if existing_session is not None:
        raise ActiveSessionExistsError(reservation_id)

    try:
        reservation.status = ReservationStatus.FULFILLED
        spot.status = SpotStatus.OCCUPIED
        parking_session = ParkingSession(
            user_id=reservation.user_id,
            vehicle_id=reservation.vehicle_id,
            spot_id=reservation.spot_id,
            reservation_id=reservation.id,
            status=SessionStatus.ACTIVE,
            check_in_at=now,
        )
        db.add(parking_session)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(parking_session)
    return parking_session


def check_out(db: Session, user: User, parking_session_id: int) -> ParkingSession:
    parking_session = db.scalar(
        select(ParkingSession)
        .where(
            ParkingSession.id == parking_session_id,
            ParkingSession.user_id == user.id,
        )
        .with_for_update()
    )
    if parking_session is None:
        raise SessionNotFoundError(parking_session_id)
    if parking_session.status == SessionStatus.COMPLETED:
        raise SessionAlreadyCompletedError(parking_session_id)

    try:
        parking_session.status = SessionStatus.COMPLETED
        parking_session.check_out_at = datetime.now(timezone.utc)
        spot = db.scalar(
            select(ParkingSpot)
            .where(ParkingSpot.id == parking_session.spot_id)
            .with_for_update()
        )
        if spot is not None and spot.status == SpotStatus.OCCUPIED:
            spot.status = SpotStatus.AVAILABLE
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(parking_session)
    return parking_session
