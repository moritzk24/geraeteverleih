from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.leihfrist import LeihfristOut, LeihfristUpsert
from app.services.leihfristen import list_leihfristen, upsert_leihfrist

router = APIRouter(prefix="/api/leihfristen", tags=["leihfristen"])

DEFAULT_PATH_SEGMENT = "default"


@router.get("", response_model=list[LeihfristOut])
def get_leihfristen(db: Session = Depends(get_db)) -> list[LeihfristOut]:
    return list_leihfristen(db)


@router.put("/{kategorie}", response_model=LeihfristOut)
def put_leihfrist(kategorie: str, payload: LeihfristUpsert, db: Session = Depends(get_db)) -> LeihfristOut:
    ziel_kategorie = None if kategorie == DEFAULT_PATH_SEGMENT else kategorie
    return upsert_leihfrist(db, ziel_kategorie, payload.frist_tage)
