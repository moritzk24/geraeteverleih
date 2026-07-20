"""reservierungen table

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "reservierungen",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("geraet_id", sa.Integer(), sa.ForeignKey("geraete.id"), nullable=False),
        sa.Column("reserviert_von", sa.String(), nullable=False),
        sa.Column("start_datum", sa.Date(), nullable=False),
        sa.Column("end_datum", sa.Date(), nullable=False),
        sa.Column("storniert_am", sa.Date(), nullable=True),
        sa.Column("ausleihe_id", sa.Integer(), sa.ForeignKey("ausleihen.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("end_datum >= start_datum", name="ck_reservierungen_end_nach_start"),
    )


def downgrade() -> None:
    op.drop_table("reservierungen")
