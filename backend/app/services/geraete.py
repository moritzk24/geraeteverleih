from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.reservierung import Reservierung
from app.services.availability import offene_ausleihen_count


def aktive_reservierungen_count(db: Session, geraet_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Reservierung)
        .where(
            Reservierung.geraet_id == geraet_id,
            Reservierung.storniert_am.is_(None),
            Reservierung.ausleihe_id.is_(None),
        )
    )
    return db.execute(stmt).scalar_one()


def gebundene_menge(db: Session, geraet_id: int) -> int:
    return offene_ausleihen_count(db, geraet_id) + aktive_reservierungen_count(db, geraet_id)
