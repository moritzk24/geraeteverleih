from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.db import Base


class Reservierung(Base):
    __tablename__ = "reservierungen"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    geraet_id: Mapped[int] = mapped_column(ForeignKey("geraete.id"), nullable=False)
    reserviert_von: Mapped[str] = mapped_column(String, nullable=False)
    start_datum: Mapped[date] = mapped_column(Date, nullable=False)
    end_datum: Mapped[date] = mapped_column(Date, nullable=False)
    storniert_am: Mapped[date | None] = mapped_column(Date, nullable=True)
    ausleihe_id: Mapped[int | None] = mapped_column(ForeignKey("ausleihen.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)

    geraet: Mapped["Geraet"] = relationship()
    ausleihe: Mapped["Ausleihe | None"] = relationship()
