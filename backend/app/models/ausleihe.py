from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Ausleihe(Base):
    __tablename__ = "ausleihen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geraet_id: Mapped[int] = mapped_column(ForeignKey("geraete.id"), nullable=False)
    ausgeliehen_von: Mapped[str] = mapped_column(String, nullable=False)
    ausgeliehen_am: Mapped[date] = mapped_column(Date, nullable=False)
    faellig_am: Mapped[date] = mapped_column(Date, nullable=False)
    zurueckgegeben_am: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    geraet: Mapped["Geraet"] = relationship(back_populates="ausleihen")
