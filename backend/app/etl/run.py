import json
from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from app.etl.extract import extract_ausleihen, extract_inventar
from app.etl.load import load_ausleihen, load_geraete, wipe_clean_tables
from app.etl.report import persist_report
from app.etl.transform import transform_ausleihe_row, transform_inventar_row


def _inventar_identifier(row: dict[str, Any]) -> str:
    return (row.get("inventarnummer") or "").strip() or "<leer>"


def _ausleihe_identifier(row: dict[str, Any]) -> str:
    return "|".join(
        [
            (row.get("inventarnummer") or "").strip() or "<leer>",
            (row.get("ausgeliehen_von") or "").strip() or "<leer>",
            (row.get("ausgeliehen_am") or "").strip() or "<leer>",
        ]
    )


def run_import(db: Session) -> dict[str, Any]:
    inventar_raw = extract_inventar(db).to_dict("records")
    ausleihen_raw = extract_ausleihen(db).to_dict("records")

    seen_inventarnummern: set[str] = set()
    inventar_decisions = []
    for row in inventar_raw:
        decision = transform_inventar_row(row, seen_inventarnummern)
        if decision.data is not None:
            seen_inventarnummern.add(decision.data["inventarnummer"])
        inventar_decisions.append(decision)

    valid_inventarnummern = {
        decision.data["inventarnummer"]
        for decision in inventar_decisions
        if decision.data is not None
    }

    ausleihen_decisions = [
        transform_ausleihe_row(row, valid_inventarnummern) for row in ausleihen_raw
    ]

    wipe_clean_tables(db)
    inventarnummer_to_id = load_geraete(db, inventar_decisions)
    load_ausleihen(db, ausleihen_decisions, inventarnummer_to_id)

    persist_report(db, "alt_inventar", inventar_raw, inventar_decisions, _inventar_identifier)
    persist_report(db, "alt_ausleihen", ausleihen_raw, ausleihen_decisions, _ausleihe_identifier)

    db.commit()

    return {
        "alt_inventar": dict(Counter(d.status for d in inventar_decisions)),
        "alt_ausleihen": dict(Counter(d.status for d in ausleihen_decisions)),
    }


if __name__ == "__main__":
    from app.core.db import SessionLocal

    session = SessionLocal()
    try:
        result = run_import(session)
    finally:
        session.close()
    print(json.dumps(result, indent=2, ensure_ascii=False))
