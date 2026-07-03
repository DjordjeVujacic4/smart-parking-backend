"""add coordinates to parking locations

Revision ID: 04626b50a98c
Revises: b2dc5eab06b8
Create Date: 2026-07-03 15:36:34.799246

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '04626b50a98c'
down_revision: str | None = 'b2dc5eab06b8'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('parking_locations', sa.Column('latitude', sa.Float(), nullable=True))
    op.add_column('parking_locations', sa.Column('longitude', sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column('parking_locations', 'longitude')
    op.drop_column('parking_locations', 'latitude')
