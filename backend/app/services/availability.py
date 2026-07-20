from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet


def berechne_verfuegbare_menge(menge: int, offene_ausleihen: int) -> int:
    return menge - offene_ausleihen


def ist_verfuegbar_ab_menge(verfuegbare_menge: int) -> bool:
    return verfuegbare_menge > 0


def offene_ausleihen_count(db: Session, geraet_id: int) -> int:
    stmt = (
        select(func.count())
        .select_from(Ausleihe)
        .where(Ausleihe.geraet_id == geraet_id, Ausleihe.zurueckgegeben_am.is_(None))
    )
    return db.execute(stmt).scalar_one()


def verfuegbare_menge(db: Session, geraet: Geraet) -> int:
    return berechne_verfuegbare_menge(geraet.menge, offene_ausleihen_count(db, geraet.id))


def ist_verfuegbar(db: Session, geraet: Geraet) -> bool:
    return ist_verfuegbar_ab_menge(verfuegbare_menge(db, geraet))
