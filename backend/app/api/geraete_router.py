from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.ausleihen_router import build_ausleihe_out, list_ausleihen_query
from app.core.db import get_db
from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.schemas.ausleihe import AusleiheOut
from app.schemas.geraet import GeraetCreate, GeraetOut, GeraetUpdate
from app.services.availability import verfuegbare_menge
from app.services.geraete import gebundene_menge

router = APIRouter(prefix="/api/geraete", tags=["geraete"])


def build_geraet_out(geraet: Geraet, verfuegbare_menge_wert: int) -> GeraetOut:
    ausgemustert = geraet.ausgemustert_am is not None
    return GeraetOut(
        id=geraet.id,
        inventarnummer=geraet.inventarnummer,
        bezeichnung=geraet.bezeichnung,
        kategorie=geraet.kategorie,
        menge=geraet.menge,
        angeschafft_am=geraet.angeschafft_am,
        verfuegbare_menge=verfuegbare_menge_wert,
        verfuegbar=(not ausgemustert) and verfuegbare_menge_wert > 0,
        ausgemustert=ausgemustert,
        ausgemustert_am=geraet.ausgemustert_am,
    )


def _list_geraete(
    db: Session,
    search: str | None,
    kategorie: str | None,
    nur_verfuegbare: bool,
    inkl_ausgemustert: bool,
) -> list[GeraetOut]:
    offene_counts = (
        select(Ausleihe.geraet_id, func.count().label("offene"))
        .where(Ausleihe.zurueckgegeben_am.is_(None))
        .group_by(Ausleihe.geraet_id)
        .subquery()
    )

    stmt = select(Geraet, func.coalesce(offene_counts.c.offene, 0)).outerjoin(
        offene_counts, Geraet.id == offene_counts.c.geraet_id
    )

    if not inkl_ausgemustert:
        stmt = stmt.where(Geraet.ausgemustert_am.is_(None))
    if search:
        pattern = f"%{search}%"
        stmt = stmt.where(
            or_(Geraet.bezeichnung.ilike(pattern), Geraet.inventarnummer.ilike(pattern))
        )
    if kategorie:
        stmt = stmt.where(Geraet.kategorie == kategorie)

    stmt = stmt.order_by(Geraet.bezeichnung)

    result = []
    for geraet, offene in db.execute(stmt).all():
        geraet_out = build_geraet_out(geraet, geraet.menge - offene)
        if nur_verfuegbare and not geraet_out.verfuegbar:
            continue
        result.append(geraet_out)
    return result


@router.get("", response_model=list[GeraetOut])
def list_geraete(
    search: str | None = Query(default=None),
    kategorie: str | None = Query(default=None),
    nur_verfuegbare: bool = Query(default=False),
    inkl_ausgemustert: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[GeraetOut]:
    return _list_geraete(db, search, kategorie, nur_verfuegbare, inkl_ausgemustert)


@router.get("/kategorien", response_model=list[str])
def list_kategorien(db: Session = Depends(get_db)) -> list[str]:
    stmt = select(Geraet.kategorie).distinct().order_by(Geraet.kategorie)
    return list(db.execute(stmt).scalars().all())


@router.post("", response_model=GeraetOut, status_code=201)
def create_geraet(payload: GeraetCreate, db: Session = Depends(get_db)) -> GeraetOut:
    vorhanden = db.execute(
        select(Geraet).where(Geraet.inventarnummer == payload.inventarnummer)
    ).scalar_one_or_none()
    if vorhanden is not None:
        raise HTTPException(
            status_code=409, detail=f"Inventarnummer {payload.inventarnummer} bereits vergeben"
        )

    geraet = Geraet(
        inventarnummer=payload.inventarnummer,
        bezeichnung=payload.bezeichnung,
        kategorie=payload.kategorie,
        menge=payload.menge,
        angeschafft_am=payload.angeschafft_am,
    )
    db.add(geraet)
    db.commit()
    db.refresh(geraet)
    return build_geraet_out(geraet, geraet.menge)


@router.put("/{geraet_id}", response_model=GeraetOut)
def update_geraet(geraet_id: int, payload: GeraetUpdate, db: Session = Depends(get_db)) -> GeraetOut:
    geraet = db.get(Geraet, geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")

    if payload.menge < geraet.menge:
        gebunden = gebundene_menge(db, geraet.id)
        if payload.menge < gebunden:
            raise HTTPException(
                status_code=409,
                detail=f"Menge kann nicht unter die aktuell gebundene Menge ({gebunden}) gesenkt werden",
            )

    geraet.bezeichnung = payload.bezeichnung
    geraet.kategorie = payload.kategorie
    geraet.menge = payload.menge
    geraet.angeschafft_am = payload.angeschafft_am
    db.commit()
    db.refresh(geraet)
    return build_geraet_out(geraet, verfuegbare_menge(db, geraet))


@router.post("/{geraet_id}/ausmustern", response_model=GeraetOut)
def ausmustern(geraet_id: int, db: Session = Depends(get_db)) -> GeraetOut:
    geraet = db.get(Geraet, geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    if geraet.ausgemustert_am is not None:
        raise HTTPException(
            status_code=409,
            detail=f"Gerät ist bereits ausgemustert seit {geraet.ausgemustert_am.isoformat()}",
        )

    geraet.ausgemustert_am = date.today()
    db.commit()
    db.refresh(geraet)
    return build_geraet_out(geraet, verfuegbare_menge(db, geraet))


@router.get("/{geraet_id}", response_model=GeraetOut)
def get_geraet(geraet_id: int, db: Session = Depends(get_db)) -> GeraetOut:
    geraet = db.get(Geraet, geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    return build_geraet_out(geraet, verfuegbare_menge(db, geraet))


@router.get("/{geraet_id}/ausleihen", response_model=list[AusleiheOut])
def get_geraet_ausleihen(geraet_id: int, db: Session = Depends(get_db)) -> list[AusleiheOut]:
    geraet = db.get(Geraet, geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    rows = list_ausleihen_query(db, geraet_id=geraet_id, person=None, offen=None)
    return [build_ausleihe_out(a, g) for a, g in rows]
