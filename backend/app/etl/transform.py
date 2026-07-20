"""Row-level validation/cleaning for the Teil 1 import.

Each `transform_*_row` function is a pure function: raw dict in, `RowDecision`
out. Kept pandas-free and side-effect-free on purpose so the business rules
in ANNAHMEN.md can be unit-tested without a database or a DataFrame.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

ACCEPTED = "accepted"
ACCEPTED_WITH_CAVEAT = "accepted_with_caveat"
REJECTED = "rejected"

_DATE_FORMATS = ("%Y-%m-%d", "%d.%m.%Y")


@dataclass(frozen=True)
class ParsedDate:
    value: date | None
    reformatted: bool
    error: bool


def parse_date(raw: str | None) -> ParsedDate:
    text_value = (raw or "").strip()
    if not text_value:
        return ParsedDate(None, False, False)
    for index, fmt in enumerate(_DATE_FORMATS):
        try:
            parsed = datetime.strptime(text_value, fmt).date()
        except ValueError:
            continue
        return ParsedDate(parsed, reformatted=index != 0, error=False)
    return ParsedDate(None, False, True)


@dataclass(frozen=True)
class RowDecision:
    status: str  # accepted | accepted_with_caveat | rejected
    reason: str
    data: dict[str, Any] | None = None


def transform_inventar_row(row: dict[str, Any], seen_inventarnummern: set[str]) -> RowDecision:
    inventarnummer = (row.get("inventarnummer") or "").strip()
    if not inventarnummer:
        return RowDecision(REJECTED, "Inventarnummer fehlt")

    if inventarnummer in seen_inventarnummern:
        return RowDecision(
            REJECTED,
            f"Doppelte Inventarnummer '{inventarnummer}', erste Zeile wurde übernommen",
        )

    menge_raw = (row.get("menge") or "").strip()
    try:
        menge = int(menge_raw)
    except ValueError:
        return RowDecision(REJECTED, "Menge fehlt oder ungültig")
    if menge < 0:
        return RowDecision(REJECTED, "Menge fehlt oder ungültig")

    caveats: list[str] = []

    bezeichnung_raw = row.get("bezeichnung") or ""
    bezeichnung = bezeichnung_raw.strip()
    if bezeichnung != bezeichnung_raw:
        caveats.append("Bezeichnung getrimmt")
    if not bezeichnung:
        bezeichnung = f"Unbekannt ({inventarnummer})"
        caveats.append("Bezeichnung fehlte")

    kategorie = (row.get("kategorie") or "").strip()
    if not kategorie:
        kategorie = "Sonstige"
        caveats.append("Kategorie fehlte")

    parsed_date = parse_date(row.get("angeschafft_am"))
    angeschafft_am = parsed_date.value
    if parsed_date.error:
        caveats.append("Anschaffungsdatum nicht parsebar")
    else:
        if parsed_date.reformatted:
            caveats.append("Datumsformat normalisiert")
        if angeschafft_am is not None and angeschafft_am > date.today():
            caveats.append("Anschaffungsdatum liegt in der Zukunft")

    if menge == 0:
        caveats.append("Menge ist 0")

    cleaned = {
        "inventarnummer": inventarnummer,
        "bezeichnung": bezeichnung,
        "kategorie": kategorie,
        "menge": menge,
        "angeschafft_am": angeschafft_am,
    }

    if caveats:
        return RowDecision(ACCEPTED_WITH_CAVEAT, "; ".join(caveats), cleaned)
    return RowDecision(ACCEPTED, "OK", cleaned)


def transform_ausleihe_row(row: dict[str, Any], valid_inventarnummern: set[str]) -> RowDecision:
    inventarnummer = (row.get("inventarnummer") or "").strip()
    if inventarnummer not in valid_inventarnummern:
        return RowDecision(REJECTED, "Gerät nicht im Bestand gefunden")

    ausgeliehen_von = (row.get("ausgeliehen_von") or "").strip()
    if not ausgeliehen_von:
        return RowDecision(REJECTED, "Ausleiher fehlt")

    parsed_von = parse_date(row.get("ausgeliehen_am"))
    if parsed_von.error or parsed_von.value is None:
        return RowDecision(REJECTED, "Ausleihdatum fehlt oder ungültig")

    caveats: list[str] = []
    if parsed_von.reformatted:
        caveats.append("Datumsformat normalisiert (Ausleihdatum)")

    parsed_zurueck = parse_date(row.get("zurueckgegeben_am"))
    if parsed_zurueck.error:
        caveats.append("Rückgabedatum nicht parsebar, als offen behandelt")
        zurueckgegeben_am = None
    else:
        zurueckgegeben_am = parsed_zurueck.value
        if zurueckgegeben_am is not None:
            if parsed_zurueck.reformatted:
                caveats.append("Datumsformat normalisiert (Rückgabedatum)")
            if zurueckgegeben_am < parsed_von.value:
                return RowDecision(REJECTED, "Rückgabedatum liegt vor Ausleihdatum")

    cleaned = {
        "inventarnummer": inventarnummer,
        "ausgeliehen_von": ausgeliehen_von,
        "ausgeliehen_am": parsed_von.value,
        "zurueckgegeben_am": zurueckgegeben_am,
    }

    if caveats:
        return RowDecision(ACCEPTED_WITH_CAVEAT, "; ".join(caveats), cleaned)
    return RowDecision(ACCEPTED, "OK", cleaned)
