from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin

if TYPE_CHECKING:
    from app.models.parking_spot import ParkingSpot


class ParkingLocation(Base, CreatedAtMixin):
    __tablename__ = "parking_locations"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    address: Mapped[str] = mapped_column(String(255))

    spots: Mapped[list[ParkingSpot]] = relationship(
        back_populates="location", cascade="all, delete-orphan"
    )
