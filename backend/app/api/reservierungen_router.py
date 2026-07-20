from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.ausleihen_router import build_ausleihe_out
from app.core.db import get_db
from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.models.reservierung import Reservierung
from app.schemas.ausleihe import AusleiheOut
from app.schemas.reservierung import ReservierungCreate, ReservierungOut
from app.services.leihfristen import ermittle_faellig_am
from app.services.reservierungen import ist_aktiv, list_reservierungen, verfuegbare_menge_im_zeitraum

router = APIRouter(prefix="/api/reservierungen", tags=["reservierungen"])


def reservierung_status(reservierung: Reservierung) -> str:
    if reservierung.ausleihe_id is not None:
        return "abgeholt"
    if reservierung.storniert_am is not None:
        return "storniert"
    return "aktiv"


def build_reservierung_out(reservierung: Reservierung, geraet: Geraet) -> ReservierungOut:
    return ReservierungOut(
        id=reservierung.id,
        geraet_id=reservierung.geraet_id,
        inventarnummer=geraet.inventarnummer,
        bezeichnung=geraet.bezeichnung,
        reserviert_von=reservierung.reserviert_von,
        start_datum=reservierung.start_datum,
        end_datum=reservierung.end_datum,
        status=reservierung_status(reservierung),
        ausleihe_id=reservierung.ausleihe_id,
    )


@router.get("", response_model=list[ReservierungOut])
def get_reservierungen(
    geraet_id: int | None = Query(default=None),
    person: str | None = Query(default=None),
    status: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ReservierungOut]:
    rows = list_reservierungen(db, geraet_id=geraet_id, person=person, status=status)
    return [build_reservierung_out(r, g) for r, g in rows]


@router.post("", response_model=ReservierungOut, status_code=201)
def create_reservierung(payload: ReservierungCreate, db: Session = Depends(get_db)) -> ReservierungOut:
    geraet = db.get(Geraet, payload.geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")

    verfuegbar = verfuegbare_menge_im_zeitraum(db, geraet, payload.start_datum, payload.end_datum)
    if verfuegbar <= 0:
        raise HTTPException(
            status_code=409,
            detail=f"Kein Exemplar im gewünschten Zeitraum verfügbar (0 von {geraet.menge} verfügbar)",
        )

    reservierung = Reservierung(
        geraet_id=geraet.id,
        reserviert_von=payload.reserviert_von,
        start_datum=payload.start_datum,
        end_datum=payload.end_datum,
    )
    db.add(reservierung)
    db.commit()
    db.refresh(reservierung)
    return build_reservierung_out(reservierung, geraet)


@router.post("/{reservierung_id}/stornieren", response_model=ReservierungOut)
def stornieren(reservierung_id: int, db: Session = Depends(get_db)) -> ReservierungOut:
    reservierung = db.get(Reservierung, reservierung_id)
    if reservierung is None:
        raise HTTPException(status_code=404, detail="Reservierung nicht gefunden")
    if not ist_aktiv(reservierung):
        raise HTTPException(status_code=409, detail=f"Reservierung ist bereits {reservierung_status(reservierung)}")

    reservierung.storniert_am = date.today()
    db.commit()
    db.refresh(reservierung)
    geraet = db.get(Geraet, reservierung.geraet_id)
    return build_reservierung_out(reservierung, geraet)


@router.post("/{reservierung_id}/abholen", response_model=AusleiheOut)
def abholen(reservierung_id: int, db: Session = Depends(get_db)) -> AusleiheOut:
    reservierung = db.get(Reservierung, reservierung_id)
    if reservierung is None:
        raise HTTPException(status_code=404, detail="Reservierung nicht gefunden")
    if not ist_aktiv(reservierung):
        raise HTTPException(status_code=409, detail=f"Reservierung ist bereits {reservierung_status(reservierung)}")

    geraet = db.get(Geraet, reservierung.geraet_id)
    ausgeliehen_am = date.today()
    ausleihe = Ausleihe(
        geraet_id=geraet.id,
        ausgeliehen_von=reservierung.reserviert_von,
        ausgeliehen_am=ausgeliehen_am,
        faellig_am=ermittle_faellig_am(db, geraet.kategorie, ausgeliehen_am),
        zurueckgegeben_am=None,
    )
    db.add(ausleihe)
    db.flush()
    reservierung.ausleihe_id = ausleihe.id
    db.commit()
    db.refresh(ausleihe)
    return build_ausleihe_out(ausleihe, geraet)
