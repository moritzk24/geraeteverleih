from datetime import date

from pydantic import BaseModel, ConfigDict, field_validator, model_validator


class ReservierungCreate(BaseModel):
    geraet_id: int
    reserviert_von: str
    start_datum: date
    end_datum: date

    @field_validator("reserviert_von")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("reserviert_von darf nicht leer sein")
        return value

    @field_validator("start_datum")
    @classmethod
    def start_in_zukunft(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("start_datum darf nicht in der Vergangenheit liegen")
        return value

    @model_validator(mode="after")
    def end_nicht_vor_start(self) -> "ReservierungCreate":
        if self.end_datum < self.start_datum:
            raise ValueError("end_datum darf nicht vor start_datum liegen")
        return self


class ReservierungOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    geraet_id: int
    inventarnummer: str
    bezeichnung: str
    reserviert_von: str
    start_datum: date
    end_datum: date
    status: str
    ausleihe_id: int | None
