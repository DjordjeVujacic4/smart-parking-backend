from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import ReservationStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.parking_session import ParkingSession
    from app.models.parking_spot import ParkingSpot
    from app.models.user import User
    from app.models.vehicle import Vehicle


class Reservation(Base, TimestampMixin):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    spot_id: Mapped[int] = mapped_column(ForeignKey("parking_spots.id"))
    status: Mapped[ReservationStatus] = mapped_column(default=ReservationStatus.ACTIVE)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="reservations")
    vehicle: Mapped[Vehicle] = relationship(back_populates="reservations")
    spot: Mapped[ParkingSpot] = relationship(back_populates="reservations")
    parking_session: Mapped[ParkingSession | None] = relationship(back_populates="reservation")
