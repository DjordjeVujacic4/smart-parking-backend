from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.config import get_settings
from app.models.enums import ReservationStatus, SpotStatus
from app.models.parking_spot import ParkingSpot
from app.models.reservation import Reservation
from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.reservation import ReservationCreate


class VehicleNotFoundError(Exception):
    pass


class VehicleOwnershipError(Exception):
    pass


class SpotNotFoundError(Exception):
    pass


class SpotNotAvailableError(Exception):
    pass


class ActiveReservationExistsError(Exception):
    pass


class ReservationNotFoundError(Exception):
    pass


class ReservationNotActiveError(Exception):
    pass


def _with_related(statement):
    """Eager-load the vehicle and spot (with its location) to avoid N+1 queries."""
    return statement.options(
        joinedload(Reservation.vehicle),
        joinedload(Reservation.spot).joinedload(ParkingSpot.location),
    )


def list_reservations(db: Session, user: User) -> list[Reservation]:
    return list(
        db.scalars(
            _with_related(
                select(Reservation)
                .where(Reservation.user_id == user.id)
                .order_by(Reservation.id)
            )
        )
    )


def get_reservation(db: Session, user: User, reservation_id: int) -> Reservation:
    reservation = db.scalar(
        _with_related(
            select(Reservation).where(
                Reservation.id == reservation_id, Reservation.user_id == user.id
            )
        )
    )
    if reservation is None:
        raise ReservationNotFoundError(reservation_id)
    return reservation


def create_reservation(db: Session, user: User, data: ReservationCreate) -> Reservation:
    vehicle = db.get(Vehicle, data.vehicle_id)
    if vehicle is None:
        raise VehicleNotFoundError(data.vehicle_id)
    if vehicle.user_id != user.id:
        raise VehicleOwnershipError(data.vehicle_id)

    spot = db.scalar(
        select(ParkingSpot).where(ParkingSpot.id == data.spot_id).with_for_update()
    )
    if spot is None:
        raise SpotNotFoundError(data.spot_id)
    if spot.status != SpotStatus.AVAILABLE:
        raise SpotNotAvailableError(data.spot_id)

    active = db.scalar(
        select(Reservation).where(
            Reservation.user_id == user.id,
            Reservation.status == ReservationStatus.ACTIVE,
        )
    )
    if active is not None:
        raise ActiveReservationExistsError(user.id)

    try:
        spot.status = SpotStatus.RESERVED
        reservation = Reservation(
            user_id=user.id,
            vehicle_id=vehicle.id,
            spot_id=spot.id,
            status=ReservationStatus.ACTIVE,
            expires_at=datetime.now(timezone.utc)
            + timedelta(minutes=get_settings().reservation_duration_minutes),
        )
        db.add(reservation)
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, user: User, reservation_id: int) -> Reservation:
    reservation = get_reservation(db, user, reservation_id)
    if reservation.status != ReservationStatus.ACTIVE:
        raise ReservationNotActiveError(reservation_id)

    try:
        spot = db.scalar(
            select(ParkingSpot)
            .where(ParkingSpot.id == reservation.spot_id)
            .with_for_update()
        )
        reservation.status = ReservationStatus.CANCELLED
        if spot is not None:
            spot.status = SpotStatus.AVAILABLE
        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(reservation)
    return reservation


def expire_overdue_reservations(db: Session) -> int:
    now = datetime.now(timezone.utc)
    reservations = list(
        db.scalars(
            select(Reservation)
            .where(
                Reservation.status == ReservationStatus.ACTIVE,
                Reservation.expires_at < now,
            )
            .with_for_update()
        )
    )
    if not reservations:
        return 0

    try:
        for reservation in reservations:
            reservation.status = ReservationStatus.EXPIRED
            spot = db.scalar(
                select(ParkingSpot)
                .where(ParkingSpot.id == reservation.spot_id)
                .with_for_update()
            )
            if spot is not None and spot.status == SpotStatus.RESERVED:
                spot.status = SpotStatus.AVAILABLE
        db.commit()
    except Exception:
        db.rollback()
        raise

    return len(reservations)
