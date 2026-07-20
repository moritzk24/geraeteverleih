from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class GeraetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    inventarnummer: str
    bezeichnung: str
    kategorie: str
    menge: int
    angeschafft_am: date | None
    verfuegbare_menge: int
    verfuegbar: bool
    ausgemustert: bool
    ausgemustert_am: date | None


class GeraetCreate(BaseModel):
    inventarnummer: str
    bezeichnung: str
    kategorie: str
    menge: int
    angeschafft_am: date | None = None

    @field_validator("inventarnummer", "bezeichnung", "kategorie")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("darf nicht leer sein")
        return value

    @field_validator("menge")
    @classmethod
    def menge_nicht_negativ(cls, value: int) -> int:
        if value < 0:
            raise ValueError("menge darf nicht negativ sein")
        return value


class GeraetUpdate(BaseModel):
    bezeichnung: str
    kategorie: str
    menge: int
    angeschafft_am: date | None = None

    @field_validator("bezeichnung", "kategorie")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("darf nicht leer sein")
        return value

    @field_validator("menge")
    @classmethod
    def menge_nicht_negativ(cls, value: int) -> int:
        if value < 0:
            raise ValueError("menge darf nicht negativ sein")
        return value
