from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.parking_session import ParkingSession
    from app.models.reservation import Reservation
    from app.models.vehicle import Vehicle


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[str] = mapped_column(String(255))

    vehicles: Mapped[list[Vehicle]] = relationship(
        back_populates="owner", cascade="all, delete-orphan"
    )
    reservations: Mapped[list[Reservation]] = relationship(back_populates="user")
    parking_sessions: Mapped[list[ParkingSession]] = relationship(back_populates="user")
