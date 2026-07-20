from pydantic import BaseModel, ConfigDict, Field


class LeihfristOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    kategorie: str | None
    frist_tage: int


class LeihfristUpsert(BaseModel):
    frist_tage: int = Field(gt=0)
