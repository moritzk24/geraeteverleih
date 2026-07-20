from datetime import date

from pydantic import BaseModel, ConfigDict


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
