from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.ausleihen_router import build_ausleihe_out, list_ausleihen_query
from app.core.db import get_db
from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.schemas.ausleihe import AusleiheOut
from app.schemas.geraet import GeraetOut
from app.services.availability import verfuegbare_menge

router = APIRouter(prefix="/api/geraete", tags=["geraete"])


def _list_geraete(
    db: Session,
    search: str | None,
    kategorie: str | None,
    nur_verfuegbare: bool,
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
        verfuegbare_menge = geraet.menge - offene
        if nur_verfuegbare and verfuegbare_menge <= 0:
            continue
        result.append(
            GeraetOut(
                id=geraet.id,
                inventarnummer=geraet.inventarnummer,
                bezeichnung=geraet.bezeichnung,
                kategorie=geraet.kategorie,
                menge=geraet.menge,
                angeschafft_am=geraet.angeschafft_am,
                verfuegbare_menge=verfuegbare_menge,
                verfuegbar=verfuegbare_menge > 0,
            )
        )
    return result


@router.get("", response_model=list[GeraetOut])
def list_geraete(
    search: str | None = Query(default=None),
    kategorie: str | None = Query(default=None),
    nur_verfuegbare: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> list[GeraetOut]:
    return _list_geraete(db, search, kategorie, nur_verfuegbare)


@router.get("/kategorien", response_model=list[str])
def list_kategorien(db: Session = Depends(get_db)) -> list[str]:
    stmt = select(Geraet.kategorie).distinct().order_by(Geraet.kategorie)
    return list(db.execute(stmt).scalars().all())


@router.get("/{geraet_id}", response_model=GeraetOut)
def get_geraet(geraet_id: int, db: Session = Depends(get_db)) -> GeraetOut:
    geraet = db.get(Geraet, geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    verfuegbar = verfuegbare_menge(db, geraet)
    return GeraetOut(
        id=geraet.id,
        inventarnummer=geraet.inventarnummer,
        bezeichnung=geraet.bezeichnung,
        kategorie=geraet.kategorie,
        menge=geraet.menge,
        angeschafft_am=geraet.angeschafft_am,
        verfuegbare_menge=verfuegbar,
        verfuegbar=verfuegbar > 0,
    )


@router.get("/{geraet_id}/ausleihen", response_model=list[AusleiheOut])
def get_geraet_ausleihen(geraet_id: int, db: Session = Depends(get_db)) -> list[AusleiheOut]:
    geraet = db.get(Geraet, geraet_id)
    if geraet is None:
        raise HTTPException(status_code=404, detail="Gerät nicht gefunden")
    rows = list_ausleihen_query(db, geraet_id=geraet_id, person=None, offen=None)
    return [build_ausleihe_out(a, g) for a, g in rows]
