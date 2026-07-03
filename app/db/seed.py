from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.models.enums import SpotStatus
from app.models.parking_location import ParkingLocation
from app.models.parking_spot import ParkingSpot

PARKING_LOCATIONS = [
    {
        "name": "FON Parking",
        "address": "Jove Ilića 154, Beograd",
        "latitude": 44.7866,
        "longitude": 20.4922,
        "prefix": "A",
        "count": 20,
        "width": 2,
    },
    {
        "name": "Galerija Shopping Center",
        "address": "Bulevar Vudroa Vilsona 12, Beograd",
        "latitude": 44.8010,
        "longitude": 20.4489,
        "prefix": "G",
        "count": 100,
        "width": 3,
    },
    {
        "name": "Rajićeva Shopping Center",
        "address": "Knez Mihailova 54, Beograd",
        "latitude": 44.8176,
        "longitude": 20.4569,
        "prefix": "R",
        "count": 80,
        "width": 3,
    },
    {
        "name": "Aerodrom Nikola Tesla",
        "address": "Aerodrom Nikola Tesla 59, Beograd",
        "latitude": 44.8184,
        "longitude": 20.3091,
        "prefix": "N",
        "count": 120,
        "width": 3,
    },
    {
        "name": "Dorćol City Parking",
        "address": "Dobračina 2, Beograd",
        "latitude": 44.8236,
        "longitude": 20.4653,
        "prefix": "D",
        "count": 50,
        "width": 3,
    },
]


def seed(db: Session) -> None:
    for spec in PARKING_LOCATIONS:
        exists = db.scalar(
            select(ParkingLocation).where(ParkingLocation.name == spec["name"])
        )
        if exists is not None:
            continue

        location = ParkingLocation(
            name=spec["name"],
            address=spec["address"],
            latitude=spec["latitude"],
            longitude=spec["longitude"],
        )
        location.spots = [
            ParkingSpot(
                spot_number=f"{spec['prefix']}{number:0{spec['width']}d}",
                status=SpotStatus.AVAILABLE,
            )
            for number in range(1, spec["count"] + 1)
        ]
        db.add(location)

    db.commit()


def main() -> None:
    with SessionLocal() as db:
        seed(db)


if __name__ == "__main__":
    main()
