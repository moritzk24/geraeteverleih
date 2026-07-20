from typing import Any

from sqlalchemy.orm import Session

from app.etl.transform import RowDecision
from app.models.import_report import ImportReportEntry


def persist_report(
    db: Session,
    source_table: str,
    raw_rows: list[dict[str, Any]],
    decisions: list[RowDecision],
    row_identifier_fn,
) -> None:
    for raw_row, decision in zip(raw_rows, decisions):
        db.add(
            ImportReportEntry(
                source_table=source_table,
                row_identifier=row_identifier_fn(raw_row),
                raw_data=raw_row,
                decision=decision.status,
                reason=decision.reason,
            )
        )
