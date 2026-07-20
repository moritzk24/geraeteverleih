from datetime import date

from app.models.reservierung import Reservierung
from app.services.reservierungen import (
    berechne_verfuegbare_menge_zeitraum,
    intervalle_ueberlappen,
    ist_aktiv,
)


def test_intervalle_ueberlappen_getrennte_zeitraeume_ueberlappen_nicht():
    assert intervalle_ueberlappen(date(2026, 8, 1), date(2026, 8, 5), date(2026, 8, 10), date(2026, 8, 15)) is False


def test_intervalle_ueberlappen_teilweise_ueberschneidung():
    assert intervalle_ueberlappen(date(2026, 8, 1), date(2026, 8, 10), date(2026, 8, 5), date(2026, 8, 15)) is True


def test_intervalle_ueberlappen_beruehrende_intervalle_gelten_als_ueberlappung():
    # end_datum von A == start_datum von B: konservativ blockierend, s. ANNAHMEN.md
    assert intervalle_ueberlappen(date(2026, 8, 1), date(2026, 8, 10), date(2026, 8, 10), date(2026, 8, 20)) is True


def test_intervalle_ueberlappen_ein_intervall_enthaelt_das_andere():
    assert intervalle_ueberlappen(date(2026, 8, 1), date(2026, 8, 20), date(2026, 8, 5), date(2026, 8, 10)) is True


def test_verfuegbare_menge_zeitraum_ohne_konflikte():
    assert berechne_verfuegbare_menge_zeitraum(menge=3, offene_ausleihen=0, ueberlappende_reservierungen=0) == 3


def test_verfuegbare_menge_zeitraum_offene_ausleihe_blockiert_unabhaengig_vom_zeitraum():
    # Einzelstück, eine offene (ggf. überfällige) Ausleihe -> 0 verfügbar, auch ohne Reservierungen
    assert berechne_verfuegbare_menge_zeitraum(menge=1, offene_ausleihen=1, ueberlappende_reservierungen=0) == 0


def test_verfuegbare_menge_zeitraum_ueberlappende_reservierung_blockiert():
    assert berechne_verfuegbare_menge_zeitraum(menge=1, offene_ausleihen=0, ueberlappende_reservierungen=1) == 0


def test_verfuegbare_menge_zeitraum_mehrere_geraete_ein_konflikt_bleibt_verfuegbar():
    assert berechne_verfuegbare_menge_zeitraum(menge=3, offene_ausleihen=1, ueberlappende_reservierungen=1) == 1


def test_ist_aktiv_frische_reservierung():
    assert ist_aktiv(Reservierung(storniert_am=None, ausleihe_id=None)) is True


def test_ist_aktiv_stornierte_reservierung_ist_nicht_aktiv():
    assert ist_aktiv(Reservierung(storniert_am=date(2026, 7, 20), ausleihe_id=None)) is False


def test_ist_aktiv_abgeholte_reservierung_ist_nicht_aktiv():
    assert ist_aktiv(Reservierung(storniert_am=None, ausleihe_id=42)) is False
