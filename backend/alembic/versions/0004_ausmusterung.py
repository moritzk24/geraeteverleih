"""ausmusterung: retire flag on geraete

Revision ID: 0004
Revises: 0003
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("geraete", sa.Column("ausgemustert_am", sa.Date(), nullable=True))


def downgrade() -> None:
    op.drop_column("geraete", "ausgemustert_am")
