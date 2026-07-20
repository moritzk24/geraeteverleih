from datetime import datetime

from sqlalchemy import JSON, CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import Base


class ImportReportEntry(Base):
    __tablename__ = "import_report"
    __table_args__ = (
        CheckConstraint(
            "decision IN ('accepted', 'accepted_with_caveat', 'rejected')",
            name="ck_import_report_decision",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    run_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False)
    source_table: Mapped[str] = mapped_column(String, nullable=False)
    row_identifier: Mapped[str] = mapped_column(String, nullable=False)
    raw_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
