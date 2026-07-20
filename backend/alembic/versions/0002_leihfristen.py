"""leihfristen config table + ausleihen.faellig_am

Revision ID: 0002
Revises: 0001
Create Date: 2026-07-20

"""
from alembic import op
import sqlalchemy as sa

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "leihfristen",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("kategorie", sa.String(), nullable=True, unique=True),
        sa.Column("frist_tage", sa.Integer(), nullable=False),
        sa.CheckConstraint("frist_tage > 0", name="ck_leihfristen_frist_tage_positiv"),
    )

    op.execute(
        """
        INSERT INTO leihfristen (kategorie, frist_tage) VALUES
            (NULL, 14),
            ('Kamera', 7),
            ('Präsentation', 7),
            ('Mobilgerät', 30)
        """
    )

    op.add_column("ausleihen", sa.Column("faellig_am", sa.Date(), nullable=True))

    op.execute(
        """
        UPDATE ausleihen a
        SET faellig_am = a.ausgeliehen_am + COALESCE(
            (
                SELECT lf.frist_tage
                FROM leihfristen lf
                JOIN geraete g ON g.id = a.geraet_id
                WHERE lf.kategorie = g.kategorie
            ),
            (SELECT lf2.frist_tage FROM leihfristen lf2 WHERE lf2.kategorie IS NULL)
        )
        """
    )

    op.alter_column("ausleihen", "faellig_am", nullable=False)


def downgrade() -> None:
    op.drop_column("ausleihen", "faellig_am")
    op.drop_table("leihfristen")
