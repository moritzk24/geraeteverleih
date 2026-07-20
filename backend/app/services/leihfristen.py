"""Loan-period (Leihfrist) lookup and due-date/overdue math.

`waehle_frist_tage`, `berechne_faellig_am` and `ist_ueberfaellig` are pure
functions (dict/date in, value out) so the business rules can be
unit-tested without a database, matching the approach in `etl/transform.py`.
"""

from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.leihfrist import Leihfrist

DEFAULT_FRIST_TAGE = 14


def waehle_frist_tage(frist_by_kategorie: dict[str | None, int], kategorie: str) -> int:
    if kategorie in frist_by_kategorie:
        return frist_by_kategorie[kategorie]
    return frist_by_kategorie.get(None, DEFAULT_FRIST_TAGE)


def berechne_faellig_am(ausgeliehen_am: date, frist_tage: int) -> date:
    return ausgeliehen_am + timedelta(days=frist_tage)


def ist_ueberfaellig(faellig_am: date, zurueckgegeben_am: date | None, heute: date | None = None) -> bool:
    if zurueckgegeben_am is not None:
        return False
    return faellig_am < (heute or date.today())


def _frist_by_kategorie(db: Session) -> dict[str | None, int]:
    stmt = select(Leihfrist.kategorie, Leihfrist.frist_tage)
    return dict(db.execute(stmt).all())


def ermittle_frist_tage(db: Session, kategorie: str) -> int:
    return waehle_frist_tage(_frist_by_kategorie(db), kategorie)


def ermittle_faellig_am(db: Session, kategorie: str, ausgeliehen_am: date) -> date:
    return berechne_faellig_am(ausgeliehen_am, ermittle_frist_tage(db, kategorie))


def list_leihfristen(db: Session) -> list[Leihfrist]:
    stmt = select(Leihfrist).order_by(Leihfrist.kategorie.is_(None).desc(), Leihfrist.kategorie)
    return list(db.execute(stmt).scalars().all())


def upsert_leihfrist(db: Session, kategorie: str | None, frist_tage: int) -> Leihfrist:
    stmt = select(Leihfrist).where(Leihfrist.kategorie == kategorie)
    leihfrist = db.execute(stmt).scalar_one_or_none()
    if leihfrist is None:
        leihfrist = Leihfrist(kategorie=kategorie, frist_tage=frist_tage)
        db.add(leihfrist)
    else:
        leihfrist.frist_tage = frist_tage
    db.commit()
    db.refresh(leihfrist)
    return leihfrist
