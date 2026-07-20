from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.stats import AuslastungOut, TopGeraetOut, TopPersonOut
from app.services.stats import auslastung_je_kategorie, top_geraete, top_personen

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/top-personen", response_model=list[TopPersonOut])
def get_top_personen(
    limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)
) -> list[TopPersonOut]:
    rows = top_personen(db, limit)
    return [TopPersonOut(person=person, anzahl_offene_ausleihen=anzahl) for person, anzahl in rows]


@router.get("/top-geraete", response_model=list[TopGeraetOut])
def get_top_geraete(
    limit: int = Query(default=10, ge=1, le=100), db: Session = Depends(get_db)
) -> list[TopGeraetOut]:
    rows = top_geraete(db, limit)
    return [
        TopGeraetOut(
            geraet_id=geraet.id,
            inventarnummer=geraet.inventarnummer,
            bezeichnung=geraet.bezeichnung,
            anzahl_ausleihen=anzahl,
        )
        for geraet, anzahl in rows
    ]


@router.get("/auslastung", response_model=list[AuslastungOut])
def get_auslastung(db: Session = Depends(get_db)) -> list[AuslastungOut]:
    return [AuslastungOut(**row) for row in auslastung_je_kategorie(db)]
