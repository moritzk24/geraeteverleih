from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.etl.transform import ACCEPTED, ACCEPTED_WITH_CAVEAT, RowDecision
from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.models.import_report import ImportReportEntry

_LOADABLE = (ACCEPTED, ACCEPTED_WITH_CAVEAT)


def wipe_clean_tables(db: Session) -> None:
    db.execute(delete(Ausleihe))
    db.execute(delete(Geraet))
    db.execute(delete(ImportReportEntry))


def load_geraete(db: Session, decisions: list[RowDecision]) -> dict[str, int]:
    inventarnummer_to_id: dict[str, int] = {}
    for decision in decisions:
        if decision.status not in _LOADABLE:
            continue
        geraet = Geraet(**decision.data)
        db.add(geraet)
        db.flush()
        inventarnummer_to_id[decision.data["inventarnummer"]] = geraet.id
    return inventarnummer_to_id


def load_ausleihen(db: Session, decisions: list[RowDecision], inventarnummer_to_id: dict[str, int]) -> None:
    for decision in decisions:
        if decision.status not in _LOADABLE:
            continue
        data = dict(decision.data)
        inventarnummer = data.pop("inventarnummer")
        ausleihe = Ausleihe(geraet_id=inventarnummer_to_id[inventarnummer], **data)
        db.add(ausleihe)
