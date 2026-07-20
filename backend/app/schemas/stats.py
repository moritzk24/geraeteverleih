from pydantic import BaseModel


class TopPersonOut(BaseModel):
    person: str
    anzahl_offene_ausleihen: int


class TopGeraetOut(BaseModel):
    geraet_id: int
    inventarnummer: str
    bezeichnung: str
    anzahl_ausleihen: int


class AuslastungOut(BaseModel):
    kategorie: str
    kapazitaet: int
    gebunden: int
    quote: float | None
    label: str
