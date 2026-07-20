from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ImportReportEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    run_at: datetime
    source_table: str
    row_identifier: str
    raw_data: dict[str, Any]
    decision: str
    reason: str


class ImportRunResult(BaseModel):
    alt_inventar: dict[str, int]
    alt_ausleihen: dict[str, int]


class ImportReportSummaryRow(BaseModel):
    source_table: str
    decision: str
    count: int
