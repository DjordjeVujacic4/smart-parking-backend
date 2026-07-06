"""rename reservation status fulfilled to parked

Revision ID: c7f1a2b3d4e5
Revises: 04626b50a98c
Create Date: 2026-07-06 09:00:00.000000

"""
from collections.abc import Sequence

from alembic import op


revision: str = 'c7f1a2b3d4e5'
down_revision: str | None = '04626b50a98c'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE reservationstatus RENAME VALUE 'FULFILLED' TO 'PARKED'")


def downgrade() -> None:
    op.execute("ALTER TYPE reservationstatus RENAME VALUE 'PARKED' TO 'FULFILLED'")
