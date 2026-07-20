"""Reservation overlap and time-window availability math.

`intervalle_ueberlappen` and `berechne_verfuegbare_menge_zeitraum` are pure
functions so the overlap/capacity rules can be unit-tested without a
database, matching the approach in `services/availability.py`.
"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.geraet import Geraet
from app.models.reservierung import Reservierung
from app.services.availability import offene_ausleihen_count


def intervalle_ueberlappen(start1: date, end1: date, start2: date, end2: date) -> bool:
    return start1 <= end2 and start2 <= end1


def berechne_verfuegbare_menge_zeitraum(menge: int, offene_ausleihen: int, ueberlappende_reservierungen: int) -> int:
    return menge - offene_ausleihen - ueberlappende_reservierungen


def ist_aktiv(reservierung: Reservierung) -> bool:
    return reservierung.storniert_am is None and reservierung.ausleihe_id is None


def ueberlappende_aktive_reservierungen_count(
    db: Session, geraet_id: int, start: date, end: date, exclude_id: int | None = None
) -> int:
    stmt = select(func.count()).select_from(Reservierung).where(
        Reservierung.geraet_id == geraet_id,
        Reservierung.storniert_am.is_(None),
        Reservierung.ausleihe_id.is_(None),
        Reservierung.start_datum <= end,
        Reservierung.end_datum >= start,
    )
    if exclude_id is not None:
        stmt = stmt.where(Reservierung.id != exclude_id)
    return db.execute(stmt).scalar_one()


def verfuegbare_menge_im_zeitraum(db: Session, geraet: Geraet, start: date, end: date) -> int:
    return berechne_verfuegbare_menge_zeitraum(
        geraet.menge,
        offene_ausleihen_count(db, geraet.id),
        ueberlappende_aktive_reservierungen_count(db, geraet.id, start, end),
    )


def ist_verfuegbar_im_zeitraum(db: Session, geraet: Geraet, start: date, end: date) -> bool:
    return verfuegbare_menge_im_zeitraum(db, geraet, start, end) > 0


def list_reservierungen(
    db: Session,
    geraet_id: int | None,
    person: str | None,
    status: str | None,
) -> list[tuple[Reservierung, Geraet]]:
    stmt = select(Reservierung, Geraet).join(Geraet, Reservierung.geraet_id == Geraet.id)
    if geraet_id is not None:
        stmt = stmt.where(Reservierung.geraet_id == geraet_id)
    if person:
        stmt = stmt.where(Reservierung.reserviert_von.ilike(f"%{person}%"))
    if status == "aktiv":
        stmt = stmt.where(Reservierung.storniert_am.is_(None), Reservierung.ausleihe_id.is_(None))
    elif status == "storniert":
        stmt = stmt.where(Reservierung.storniert_am.is_not(None))
    elif status == "abgeholt":
        stmt = stmt.where(Reservierung.ausleihe_id.is_not(None))
    stmt = stmt.order_by(Reservierung.start_datum.desc())
    return [(r, g) for r, g in db.execute(stmt).all()]
