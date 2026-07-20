from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.etl.run import run_import
from app.models.import_report import ImportReportEntry
from app.schemas.import_report import (
    ImportReportEntryOut,
    ImportReportSummaryRow,
    ImportRunResult,
)

router = APIRouter(prefix="/api", tags=["import"])


@router.post("/import/run", response_model=ImportRunResult)
def trigger_import(db: Session = Depends(get_db)) -> ImportRunResult:
    summary = run_import(db)
    return ImportRunResult(**summary)


@router.get("/import-report", response_model=list[ImportReportEntryOut])
def list_report(
    source_table: str | None = Query(default=None),
    decision: str | None = Query(default=None),
    inventarnummer: str | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list[ImportReportEntry]:
    stmt = select(ImportReportEntry)
    if source_table:
        stmt = stmt.where(ImportReportEntry.source_table == source_table)
    if decision:
        stmt = stmt.where(ImportReportEntry.decision == decision)
    if inventarnummer:
        stmt = stmt.where(ImportReportEntry.row_identifier.ilike(f"%{inventarnummer}%"))
    stmt = stmt.order_by(ImportReportEntry.id)
    return list(db.execute(stmt).scalars().all())


@router.get("/import-report/summary", response_model=list[ImportReportSummaryRow])
def report_summary(db: Session = Depends(get_db)) -> list[ImportReportSummaryRow]:
    stmt = (
        select(
            ImportReportEntry.source_table,
            ImportReportEntry.decision,
            func.count().label("count"),
        )
        .group_by(ImportReportEntry.source_table, ImportReportEntry.decision)
        .order_by(ImportReportEntry.source_table, ImportReportEntry.decision)
    )
    rows = db.execute(stmt).all()
    return [
        ImportReportSummaryRow(source_table=row.source_table, decision=row.decision, count=row.count)
        for row in rows
    ]
