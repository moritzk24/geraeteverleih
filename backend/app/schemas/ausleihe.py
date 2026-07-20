from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator


class AusleiheCreate(BaseModel):
    geraet_id: int
    ausgeliehen_von: str

    @field_validator("ausgeliehen_von")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("ausgeliehen_von darf nicht leer sein")
        return value


class AusleiheOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    geraet_id: int
    inventarnummer: str
    bezeichnung: str
    ausgeliehen_von: str
    ausgeliehen_am: date
    zurueckgegeben_am: date | None
