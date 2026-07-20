from app.etl.transform import (
    ACCEPTED,
    ACCEPTED_WITH_CAVEAT,
    REJECTED,
    transform_ausleihe_row,
    transform_inventar_row,
)


def test_valid_row_is_accepted_without_caveat():
    row = {
        "inventarnummer": "IT-001",
        "bezeichnung": "Dell Latitude 5540",
        "kategorie": "Laptop",
        "menge": "4",
        "angeschafft_am": "2023-05-12",
    }
    decision = transform_inventar_row(row, seen_inventarnummern=set())
    assert decision.status == ACCEPTED
    assert decision.data["menge"] == 4


def test_duplicate_inventarnummer_is_rejected():
    row = {
        "inventarnummer": "IT-005",
        "bezeichnung": "iPad Air Testgerät",
        "kategorie": "Mobilgerät",
        "menge": "1",
        "angeschafft_am": "02.02.2024",
    }
    decision = transform_inventar_row(row, seen_inventarnummern={"IT-005"})
    assert decision.status == REJECTED
    assert "Doppelte Inventarnummer" in decision.reason


def test_empty_bezeichnung_gets_placeholder_and_caveat():
    row = {
        "inventarnummer": "IT-007",
        "bezeichnung": "",
        "kategorie": "Werkzeug",
        "menge": "1",
        "angeschafft_am": "2020-01-10",
    }
    decision = transform_inventar_row(row, seen_inventarnummern=set())
    assert decision.status == ACCEPTED_WITH_CAVEAT
    assert decision.data["bezeichnung"] == "Unbekannt (IT-007)"


def test_invalid_menge_is_rejected():
    row = {
        "inventarnummer": "IT-099",
        "bezeichnung": "Kaputtes Gerät",
        "kategorie": "Sonstige",
        "menge": "nicht-numerisch",
        "angeschafft_am": "2024-01-01",
    }
    decision = transform_inventar_row(row, seen_inventarnummern=set())
    assert decision.status == REJECTED


def test_german_date_format_is_normalized_with_caveat():
    row = {
        "inventarnummer": "IT-002",
        "bezeichnung": "Logitech MX Master 3",
        "kategorie": "Maus",
        "menge": "10",
        "angeschafft_am": "12.01.2024",
    }
    decision = transform_inventar_row(row, seen_inventarnummern=set())
    assert decision.status == ACCEPTED_WITH_CAVEAT
    assert decision.data["angeschafft_am"].isoformat() == "2024-01-12"


def test_ausleihe_referencing_unknown_geraet_is_rejected():
    row = {
        "inventarnummer": "IT-042",
        "ausgeliehen_von": "Paul Neumann",
        "ausgeliehen_am": "2026-06-01",
        "zurueckgegeben_am": "",
    }
    decision = transform_ausleihe_row(row, valid_inventarnummern={"IT-001"})
    assert decision.status == REJECTED
    assert "nicht im Bestand" in decision.reason


def test_open_loan_with_empty_return_date_is_accepted_without_caveat():
    row = {
        "inventarnummer": "IT-015",
        "ausgeliehen_von": "Mehmet Aydin",
        "ausgeliehen_am": "2026-06-08",
        "zurueckgegeben_am": "",
    }
    decision = transform_ausleihe_row(row, valid_inventarnummern={"IT-015"})
    assert decision.status == ACCEPTED
    assert decision.data["zurueckgegeben_am"] is None


def test_return_before_loan_date_is_rejected():
    row = {
        "inventarnummer": "IT-006",
        "ausgeliehen_von": "Lisa Hoffmann",
        "ausgeliehen_am": "2026-06-15",
        "zurueckgegeben_am": "2026-06-10",
    }
    decision = transform_ausleihe_row(row, valid_inventarnummern={"IT-006"})
    assert decision.status == REJECTED
    assert "Rückgabedatum liegt vor Ausleihdatum" in decision.reason
