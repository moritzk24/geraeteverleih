"""Auswertungen: top-personen/-geraete queries and Auslastung math.

`berechne_auslastung_quote` and `bestimme_auslastung_label` are pure
functions so the boundary decisions (40%/80%, Kapazität 0) can be
unit-tested without a database, matching the approach elsewhere in
services/.
"""

from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.models.reservierung import Reservierung


def berechne_auslastung_quote(kapazitaet: int, gebunden: int) -> float | None:
    if kapazitaet == 0:
        return None
    return gebunden / kapazitaet


def bestimme_auslastung_label(quote: float | None) -> str:
    if quote is None:
        return "n/a"
    if quote < 0.4:
        return "niedrig"
    if quote <= 0.8:
        return "mittel"
    return "hoch"


def top_personen(db: Session, limit: int) -> list[tuple[str, int]]:
    stmt = (
        select(Ausleihe.ausgeliehen_von, func.count().label("anzahl"))
        .where(Ausleihe.zurueckgegeben_am.is_(None))
        .group_by(Ausleihe.ausgeliehen_von)
        .order_by(func.count().desc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def top_geraete(db: Session, limit: int) -> list[tuple[Geraet, int]]:
    stmt = (
        select(Geraet, func.count(Ausleihe.id).label("anzahl"))
        .join(Ausleihe, Ausleihe.geraet_id == Geraet.id)
        .group_by(Geraet.id)
        .order_by(func.count(Ausleihe.id).desc())
        .limit(limit)
    )
    return list(db.execute(stmt).all())


def auslastung_je_kategorie(db: Session, heute: date | None = None) -> list[dict]:
    heute = heute or date.today()

    kategorien = sorted(db.execute(select(Geraet.kategorie).distinct()).scalars().all())

    kapazitaet_by_kategorie = dict(
        db.execute(
            select(Geraet.kategorie, func.sum(Geraet.menge))
            .where(Geraet.ausgemustert_am.is_(None))
            .group_by(Geraet.kategorie)
        ).all()
    )

    offene_by_kategorie = dict(
        db.execute(
            select(Geraet.kategorie, func.count())
            .select_from(Ausleihe)
            .join(Geraet, Ausleihe.geraet_id == Geraet.id)
            .where(Ausleihe.zurueckgegeben_am.is_(None), Geraet.ausgemustert_am.is_(None))
            .group_by(Geraet.kategorie)
        ).all()
    )

    reservierungen_by_kategorie = dict(
        db.execute(
            select(Geraet.kategorie, func.count())
            .select_from(Reservierung)
            .join(Geraet, Reservierung.geraet_id == Geraet.id)
            .where(
                Reservierung.storniert_am.is_(None),
                Reservierung.ausleihe_id.is_(None),
                Reservierung.start_datum <= heute,
                Reservierung.end_datum >= heute,
                Geraet.ausgemustert_am.is_(None),
            )
            .group_by(Geraet.kategorie)
        ).all()
    )

    result = []
    for kategorie in kategorien:
        kapazitaet = kapazitaet_by_kategorie.get(kategorie, 0)
        gebunden = offene_by_kategorie.get(kategorie, 0) + reservierungen_by_kategorie.get(kategorie, 0)
        quote = berechne_auslastung_quote(kapazitaet, gebunden)
        result.append(
            {
                "kategorie": kategorie,
                "kapazitaet": kapazitaet,
                "gebunden": gebunden,
                "quote": quote,
                "label": bestimme_auslastung_label(quote),
            }
        )
    return result
