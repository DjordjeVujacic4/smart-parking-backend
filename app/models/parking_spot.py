from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SpotStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.parking_location import ParkingLocation
    from app.models.parking_session import ParkingSession
    from app.models.reservation import Reservation


class ParkingSpot(Base, TimestampMixin):
    __tablename__ = "parking_spots"
    __table_args__ = (UniqueConstraint("location_id", "spot_number"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    location_id: Mapped[int] = mapped_column(ForeignKey("parking_locations.id"))
    spot_number: Mapped[str] = mapped_column(String(20))
    status: Mapped[SpotStatus] = mapped_column(default=SpotStatus.AVAILABLE)

    location: Mapped[ParkingLocation] = relationship(back_populates="spots")
    reservations: Mapped[list[Reservation]] = relationship(back_populates="spot")
    parking_sessions: Mapped[list[ParkingSession]] = relationship(back_populates="spot")
