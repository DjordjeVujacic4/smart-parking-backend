"""add completed reservation status

Revision ID: d3e4f5a6b7c8
Revises: c7f1a2b3d4e5
Create Date: 2026-07-06 10:00:00.000000

"""
from collections.abc import Sequence

from alembic import op


revision: str = 'd3e4f5a6b7c8'
down_revision: str | None = 'c7f1a2b3d4e5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE reservationstatus ADD VALUE IF NOT EXISTS 'COMPLETED'")


def downgrade() -> None:
    # PostgreSQL cannot drop a value from an enum, so recreate the type
    # without COMPLETED. Any reservation left in the COMPLETED state is
    # reverted to its prior terminal-ish state (PARKED) before the swap so
    # the cast cannot fail.
    op.execute(
        "UPDATE reservations SET status = 'PARKED' WHERE status = 'COMPLETED'"
    )
    op.execute("ALTER TYPE reservationstatus RENAME TO reservationstatus_old")
    op.execute(
        "CREATE TYPE reservationstatus AS ENUM "
        "('ACTIVE', 'EXPIRED', 'CANCELLED', 'PARKED')"
    )
    op.execute(
        "ALTER TABLE reservations ALTER COLUMN status "
        "TYPE reservationstatus USING status::text::reservationstatus"
    )
    op.execute("DROP TYPE reservationstatus_old")
