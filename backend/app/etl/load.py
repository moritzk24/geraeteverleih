from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.etl.transform import ACCEPTED, ACCEPTED_WITH_CAVEAT, RowDecision
from app.models.ausleihe import Ausleihe
from app.models.geraet import Geraet
from app.models.import_report import ImportReportEntry
from app.services.leihfristen import ermittle_faellig_am

_LOADABLE = (ACCEPTED, ACCEPTED_WITH_CAVEAT)


def wipe_clean_tables(db: Session) -> None:
    db.execute(delete(Ausleihe))
    db.execute(delete(Geraet))
    db.execute(delete(ImportReportEntry))


def load_geraete(db: Session, decisions: list[RowDecision]) -> dict[str, Geraet]:
    inventarnummer_to_geraet: dict[str, Geraet] = {}
    for decision in decisions:
        if decision.status not in _LOADABLE:
            continue
        geraet = Geraet(**decision.data)
        db.add(geraet)
        db.flush()
        inventarnummer_to_geraet[decision.data["inventarnummer"]] = geraet
    return inventarnummer_to_geraet


def load_ausleihen(
    db: Session, decisions: list[RowDecision], inventarnummer_to_geraet: dict[str, Geraet]
) -> None:
    for decision in decisions:
        if decision.status not in _LOADABLE:
            continue
        data = dict(decision.data)
        inventarnummer = data.pop("inventarnummer")
        geraet = inventarnummer_to_geraet[inventarnummer]
        faellig_am = ermittle_faellig_am(db, geraet.kategorie, data["ausgeliehen_am"])
        ausleihe = Ausleihe(geraet_id=geraet.id, faellig_am=faellig_am, **data)
        db.add(ausleihe)
