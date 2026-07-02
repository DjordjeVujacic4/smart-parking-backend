from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin

if TYPE_CHECKING:
    from app.models.parking_session import ParkingSession
    from app.models.reservation import Reservation
    from app.models.user import User


class Vehicle(Base, CreatedAtMixin):
    __tablename__ = "vehicles"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    license_plate: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    make: Mapped[str | None] = mapped_column(String(50))
    model: Mapped[str | None] = mapped_column(String(50))

    owner: Mapped[User] = relationship(back_populates="vehicles")
    reservations: Mapped[list[Reservation]] = relationship(back_populates="vehicle")
    parking_sessions: Mapped[list[ParkingSession]] = relationship(back_populates="vehicle")
