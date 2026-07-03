from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.vehicle import Vehicle
from app.schemas.vehicle import VehicleCreate, VehicleUpdate


class VehicleNotFoundError(Exception):
    pass


class DuplicateLicensePlateError(Exception):
    pass


def _get_by_plate(db: Session, license_plate: str) -> Vehicle | None:
    return db.scalar(select(Vehicle).where(Vehicle.license_plate == license_plate))


def list_vehicles(db: Session, owner: User) -> list[Vehicle]:
    return list(db.scalars(select(Vehicle).where(Vehicle.user_id == owner.id)))


def get_vehicle(db: Session, owner: User, vehicle_id: int) -> Vehicle:
    vehicle = db.scalar(
        select(Vehicle).where(
            Vehicle.id == vehicle_id, Vehicle.user_id == owner.id
        )
    )
    if vehicle is None:
        raise VehicleNotFoundError(vehicle_id)
    return vehicle


def create_vehicle(db: Session, owner: User, data: VehicleCreate) -> Vehicle:
    if _get_by_plate(db, data.license_plate) is not None:
        raise DuplicateLicensePlateError(data.license_plate)

    vehicle = Vehicle(
        user_id=owner.id,
        license_plate=data.license_plate,
        make=data.make,
        model=data.model,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def update_vehicle(
    db: Session, owner: User, vehicle_id: int, data: VehicleUpdate
) -> Vehicle:
    vehicle = get_vehicle(db, owner, vehicle_id)
    updates = data.model_dump(exclude_unset=True)

    new_plate = updates.get("license_plate")
    if new_plate is not None and new_plate != vehicle.license_plate:
        if _get_by_plate(db, new_plate) is not None:
            raise DuplicateLicensePlateError(new_plate)

    for field, value in updates.items():
        setattr(vehicle, field, value)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def delete_vehicle(db: Session, owner: User, vehicle_id: int) -> None:
    vehicle = get_vehicle(db, owner, vehicle_id)
    db.delete(vehicle)
    db.commit()
