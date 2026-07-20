from datetime import date

from app.services.leihfristen import (
    DEFAULT_FRIST_TAGE,
    berechne_faellig_am,
    ist_ueberfaellig,
    waehle_frist_tage,
)

FRISTEN = {None: 14, "Kamera": 7, "Präsentation": 7, "Mobilgerät": 30}


def test_waehle_frist_tage_verwendet_kategorie_spezifische_frist():
    assert waehle_frist_tage(FRISTEN, "Kamera") == 7
    assert waehle_frist_tage(FRISTEN, "Mobilgerät") == 30


def test_waehle_frist_tage_faellt_auf_default_zeile_zurueck():
    assert waehle_frist_tage(FRISTEN, "Werkzeug") == 14


def test_waehle_frist_tage_faellt_auf_hartkodierten_default_zurueck_wenn_keine_default_zeile_existiert():
    assert waehle_frist_tage({"Kamera": 7}, "Werkzeug") == DEFAULT_FRIST_TAGE


def test_berechne_faellig_am_addiert_frist_tage():
    assert berechne_faellig_am(date(2026, 1, 1), 14) == date(2026, 1, 15)


def test_ist_ueberfaellig_offen_und_frist_abgelaufen():
    assert ist_ueberfaellig(date(2026, 1, 1), None, heute=date(2026, 1, 2)) is True


def test_ist_ueberfaellig_offen_und_noch_innerhalb_der_frist():
    assert ist_ueberfaellig(date(2026, 1, 10), None, heute=date(2026, 1, 2)) is False


def test_ist_ueberfaellig_zurueckgegeben_zaehlt_nicht_als_ueberfaellig_auch_wenn_zu_spaet():
    assert ist_ueberfaellig(date(2026, 1, 1), date(2026, 1, 5), heute=date(2026, 1, 10)) is False
