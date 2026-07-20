from app.services.availability import berechne_verfuegbare_menge, ist_verfuegbar_ab_menge


def test_verfuegbare_menge_ohne_offene_ausleihen():
    assert berechne_verfuegbare_menge(menge=5, offene_ausleihen=0) == 5


def test_verfuegbare_menge_teilweise_ausgeliehen():
    assert berechne_verfuegbare_menge(menge=5, offene_ausleihen=3) == 2


def test_verfuegbare_menge_vollstaendig_ausgeliehen_ist_nicht_verfuegbar():
    verfuegbar = berechne_verfuegbare_menge(menge=2, offene_ausleihen=2)
    assert verfuegbar == 0
    assert ist_verfuegbar_ab_menge(verfuegbar) is False


def test_einzelstueck_ist_verfuegbar_ohne_offene_ausleihe():
    verfuegbar = berechne_verfuegbare_menge(menge=1, offene_ausleihen=0)
    assert ist_verfuegbar_ab_menge(verfuegbar) is True
