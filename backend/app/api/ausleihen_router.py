from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.schemas.ausleihe import AusleiheCreate, AusleiheOut
from app.services.availability import verfuegbare_menge
from app.services.leihfristen import ermittle_faellig_am, ist_ueberfaellig

router = APIRouter(prefix="/api/ausleihen", tags=["ausleihen"])


def build_ausleihe_out(ausleihe: Ausleihe, geraet: Geraet) -> AusleiheOut:
    return AusleiheOut(
        id=ausleihe.id,
        geraet_id=ausleihe.geraet_id,
        inventarnummer=geraet.inventarnummer,
        bezeichnung=geraet.bezeichnung,
        ausgeliehen_von=ausleihe.ausgeliehen_von,
        ausgeliehen_am=ausleihe.ausgeliehen_am,
        faellig_am=ausleihe.faellig_am,
        zurueckgegeben_am=ausleihe.zurueckgegeben_am,
        ueberfaellig=ist_ueberfaellig(ausleihe.faellig_am, ausleihe.zurueckgegeben_am),
    )


def list_ausleihen_query(
    db: Session,
    geraet_id: int | None,
    person: str | None,
    offen: bool | None,
    ueberfaellig: bool | None = None,
) -> list[tuple[Ausleihe, Geraet]]:
    stmt = select(Ausleihe, Geraet).join(Geraet, Ausleihe.geraet_id == Geraet.id)
    if geraet_id is not None:
        stmt = stmt.where(Ausleihe.geraet_id == geraet_id)
    if person:
        stmt = stmt.where(Ausleihe.ausgeliehen_von.ilike(f"%{person}%"))
    if offen is not None:
        if offen:
            stmt = stmt.where(Ausleihe.zurueckgegeben_am.is_(None))
        else:
            stmt = stmt.where(Ausleihe.zurueckgegeben_am.is_not(None))
    if ueberfaellig:
        stmt = stmt.where(Ausleihe.zurueckgegeben_am.is_(None), Ausleihe.faellig_am < date.today())
    stmt = stmt.order_by(Ausleihe.ausgeliehen_am.desc())
    return [(a, g) for a, g in db.execute(stmt).all()]


@router.get("", response_model=list[AusleiheOut])
def list_ausleihen(
    geraet_id: int | None = Query(default=None),
    person: str | None = Query(default=None),
    offen: bool | None = Query(default=None),
    ueberfaellig: bool | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[AusleiheOut]:
    rows = list_ausleihen_query(db, geraet_id=geraet_id, person=person, offen=offen, ueberfaellig=ueberfaellig)
    return [build_ausleihe_out(a, g) for a, g in rows]


@router.post("", response_model=AusleiheOut, status_code=201)
def create_ausleihe(payload: AusleiheCreate, db: Session = Depends(get_db)) -> AusleiheOut:
    geraet = db.get(Geraet, payload.geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")

    verfuegbar = verfuegbare_menge(db, geraet)
    if verfuegbar <= 0:
        raise HTTPException(
            status_code=409,
            detail=f"Kein Exemplar verfügbar (0 von {geraet.menge} verfügbar)",
        )

    ausgeliehen_am = date.today()
    ausleihe = Ausleihe(
        geraet_id=geraet.id,
        ausgeliehen_von=payload.ausgeliehen_von,
        ausgeliehen_am=ausgeliehen_am,
        faellig_am=ermittle_faellig_am(db, geraet.kategorie, ausgeliehen_am),
        zurueckgegeben_am=None,
    )
    db.add(ausleihe)
    db.commit()
    db.refresh(ausleihe)
    return build_ausleihe_out(ausleihe, geraet)


@router.post("/{ausleihe_id}/rueckgabe", response_model=AusleiheOut)
def rueckgabe(ausleihe_id: int, db: Session = Depends(get_db)) -> AusleiheOut:
    ausleihe = db.get(Ausleihe, ausleihe_id)
    if ausleihe is None:
        raise HTTPException(status_code=404, detail="Ausleihe nicht gefunden")
    if ausleihe.zurueckgegeben_am is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Bereits zurückgegeben am {ausleihe.zurueckgegeben_am.isoformat()}",
        )

    ausleihe.zurueckgegeben_am = date.today()
    db.commit()
    db.refresh(ausleihe)
    geraet = db.get(Geraet, ausleihe.geraet_id)
    return build_ausleihe_out(ausleihe, geraet)
