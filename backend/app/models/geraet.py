from datetime import date, datetime

from sqlalchemy import CheckConstraint, Date, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Geraet(Base):
    __tablename__ = "geraete"
    __table_args__ = (CheckConstraint("menge >= 0", name="ck_geraete_menge_nonneg"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    inventarnummer: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    bezeichnung: Mapped[str] = mapped_column(String, nullable=False)
    kategorie: Mapped[str] = mapped_column(String, nullable=False)
    menge: Mapped[int] = mapped_column(Integer, nullable=False)
    angeschafft_am: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    ausleihen: Mapped[list["Ausleihe"]] = relationship(back_populates="geraet")
