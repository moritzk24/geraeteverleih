from sqlalchemy import CheckConstraint, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class Leihfrist(Base):
    __tablename__ = "leihfristen"
    __table_args__ = (CheckConstraint("frist_tage > 0", name="ck_leihfristen_frist_tage_positiv"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    kategorie: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    frist_tage: Mapped[int] = mapped_column(Integer, nullable=False)
