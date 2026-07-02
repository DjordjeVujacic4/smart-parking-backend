from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import SessionStatus
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.parking_spot import ParkingSpot
    from app.models.reservation import Reservation
    from app.models.user import User
    from app.models.vehicle import Vehicle


class ParkingSession(Base, TimestampMixin):
    __tablename__ = "parking_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id"))
    spot_id: Mapped[int] = mapped_column(ForeignKey("parking_spots.id"))
    reservation_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservations.id"), unique=True
    )
    status: Mapped[SessionStatus] = mapped_column(default=SessionStatus.ACTIVE)
    check_in_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    check_out_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    user: Mapped[User] = relationship(back_populates="parking_sessions")
    vehicle: Mapped[Vehicle] = relationship(back_populates="parking_sessions")
    spot: Mapped[ParkingSpot] = relationship(back_populates="parking_sessions")
    reservation: Mapped[Reservation | None] = relationship(back_populates="parking_session")
