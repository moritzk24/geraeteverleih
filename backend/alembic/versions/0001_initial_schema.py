"""initial clean schema: geraete, ausleihen, import_report

Revision ID: 0001
Revises:
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "geraete",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("inventarnummer", sa.String(), nullable=False, unique=True),
        sa.Column("bezeichnung", sa.String(), nullable=False),
        sa.Column("kategorie", sa.String(), nullable=False),
        sa.Column("menge", sa.Integer(), nullable=False),
        sa.Column("angeschafft_am", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint("menge >= 0", name="ck_geraete_menge_nonneg"),
    )

    op.create_table(
        "ausleihen",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("geraet_id", sa.Integer(), sa.ForeignKey("geraete.id"), nullable=False),
        sa.Column("ausgeliehen_von", sa.String(), nullable=False),
        sa.Column("ausgeliehen_am", sa.Date(), nullable=False),
        sa.Column("zurueckgegeben_am", sa.Date(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "import_report",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("source_table", sa.String(), nullable=False),
        sa.Column("row_identifier", sa.String(), nullable=False),
        sa.Column("raw_data", sa.JSON(), nullable=False),
        sa.Column("decision", sa.String(), nullable=False),
        sa.Column("reason", sa.String(), nullable=False),
        sa.CheckConstraint(
            "decision IN ('accepted', 'accepted_with_caveat', 'rejected')",
            name="ck_import_report_decision",
        ),
    )


def downgrade() -> None:
    op.drop_table("import_report")
    op.drop_table("ausleihen")
    op.drop_table("geraete")
