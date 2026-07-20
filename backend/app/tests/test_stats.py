from app.services.stats import berechne_auslastung_quote, bestimme_auslastung_label


def test_auslastung_quote_kapazitaet_null_ist_none():
    assert berechne_auslastung_quote(kapazitaet=0, gebunden=0) is None


def test_auslastung_quote_berechnet_anteil():
    assert berechne_auslastung_quote(kapazitaet=10, gebunden=3) == 0.3


def test_auslastung_label_niedrig_unter_40_prozent():
    assert bestimme_auslastung_label(0.39) == "niedrig"


def test_auslastung_label_mittel_bei_40_prozent_grenzwert():
    assert bestimme_auslastung_label(0.4) == "mittel"


def test_auslastung_label_mittel_bei_80_prozent_grenzwert():
    assert bestimme_auslastung_label(0.8) == "mittel"


def test_auslastung_label_hoch_ueber_80_prozent():
    assert bestimme_auslastung_label(0.81) == "hoch"


def test_auslastung_label_kapazitaet_null_ist_na():
    assert bestimme_auslastung_label(None) == "n/a"
