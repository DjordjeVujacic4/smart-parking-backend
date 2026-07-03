from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.enums import SpotStatus
from app.models.parking_location import ParkingLocation
from app.models.parking_spot import ParkingSpot


class LocationNotFoundError(Exception):
    pass


def list_locations(db: Session) -> list[ParkingLocation]:
    return list(db.scalars(select(ParkingLocation).order_by(ParkingLocation.id)))


def get_location(db: Session, location_id: int) -> ParkingLocation:
    location = db.get(ParkingLocation, location_id)
    if location is None:
        raise LocationNotFoundError(location_id)
    return location


def list_spots(db: Session, location_id: int) -> list[ParkingSpot]:
    get_location(db, location_id)
    return list(
        db.scalars(
            select(ParkingSpot)
            .where(ParkingSpot.location_id == location_id)
            .order_by(ParkingSpot.spot_number)
        )
    )


def list_available_spots(db: Session, location_id: int) -> list[ParkingSpot]:
    get_location(db, location_id)
    return list(
        db.scalars(
            select(ParkingSpot)
            .where(
                ParkingSpot.location_id == location_id,
                ParkingSpot.status == SpotStatus.AVAILABLE,
            )
            .order_by(ParkingSpot.spot_number)
        )
    )


def get_statistics(db: Session, location_id: int) -> dict:
    get_location(db, location_id)
    rows = db.execute(
        select(ParkingSpot.status, func.count())
        .where(ParkingSpot.location_id == location_id)
        .group_by(ParkingSpot.status)
    ).all()
    counts = {status: count for status, count in rows}
    return {
        "location_id": location_id,
        "total_spots": sum(counts.values()),
        "available_spots": counts.get(SpotStatus.AVAILABLE, 0),
        "occupied_spots": counts.get(SpotStatus.OCCUPIED, 0),
    }
