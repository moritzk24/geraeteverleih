# Geräteverleih

Ersatz für die bisherige Excel-Verleihliste eines internen Geräteverleihs. Umsetzung erfolgt schrittweise entlang der Teile aus `AUFGABE.md`; aktuell sind **Teil 1–5** umgesetzt.

## ⚠️ Bekanntes Problem (offen, noch zu klären)

Das Canon-EOS-R6-Gerät (`IT-009`) zeigt aktuell `verfuegbare_menge = -1` (2 offene Ausleihen bei `menge = 1`) — das Altsystem hat Verfügbarkeit nie durchgesetzt. Die Verfügbarkeitsformel toleriert das rechnerisch (negativ, `verfuegbar = false`), aber die Altdaten sind dadurch nicht bereinigt und die UI erklärt den negativen Wert nicht. **Muss vor Produktivsetzung entschieden werden**, siehe [ANNAHMEN.md](ANNAHMEN.md#teil-2--verleih-kern).

## Tech-Stack

- **Datenbank:** PostgreSQL (per Docker Compose)
- **Backend:** Python, FastAPI, SQLAlchemy 2.0, Alembic
- **ETL:** pandas (Extraktion + Iteration), reine Python-Funktionen für die Validierungslogik (leicht testbar ohne DB)
- **Tests:** pytest
- **Frontend:** Angular 19, standalone Components + Signals

## Setup

Voraussetzung: Docker & Docker Compose.

```bash
# Postgres + Backend starten (Postgres wird beim ersten Start automatisch mit data/altdaten_seed.sql befüllt)
docker compose up --build -d

# Cleanes Schema anlegen (geraete, ausleihen, import_report)
docker compose exec backend alembic upgrade head

# Migration/Import ausführen (idempotent, kann beliebig oft erneut laufen)
docker compose exec backend python -m app.etl.run
```

Die API läuft danach auf `http://localhost:8000` (Swagger-UI unter `/docs`). Postgres ist vom Host aus unter `localhost:5432` erreichbar.

### Import-Bericht einsehen

- `POST /api/import/run` — Import erneut ausführen, liefert eine Zusammenfassung
- `GET /api/import-report` — Report-Zeilen auflisten, filterbar über `?source_table=`, `?decision=`, `?inventarnummer=`
- `GET /api/import-report/summary` — Anzahl je `source_table` × `decision`

### Geräte, Ausleihe, Rückgabe, Historie (Teil 2)

- `GET /api/geraete?search=&kategorie=&nur_verfuegbare=true` — Geräteliste inkl. Verfügbarkeit
- `GET /api/geraete/kategorien` — bekannte Kategorien (für Filter-Dropdown)
- `GET /api/geraete/{id}` — einzelnes Gerät
- `GET /api/geraete/{id}/ausleihen` — Historie eines Geräts
- `GET /api/ausleihen?person=&geraet_id=&offen=` — Ausleihen-Liste/Historie nach Person und/oder Gerät
- `POST /api/ausleihen` `{geraet_id, ausgeliehen_von}` — Ausleihe anlegen (prüft Verfügbarkeit, `409` falls keine)
- `POST /api/ausleihen/{id}/rueckgabe` — offene Ausleihe zurückgeben

### Leihfristen, Überfälligkeit, Reservierungen (Teil 3 & 4)

- `GET /api/leihfristen` / `PUT /api/leihfristen/{kategorie}` (Pfadsegment `default` für die Fallback-Frist) — Fristenkonfiguration
- `GET /api/ausleihen?ueberfaellig=true` — überfällige offene Ausleihen
- `GET /api/reservierungen?geraet_id=&person=&status=` — Reservierungen auflisten
- `POST /api/reservierungen` `{geraet_id, reserviert_von, start_datum, end_datum}` — Reservierung anlegen (prüft Verfügbarkeit im Zeitraum, `409` falls keine)
- `POST /api/reservierungen/{id}/stornieren` — aktive Reservierung stornieren
- `POST /api/reservierungen/{id}/abholen` — Reservierung zur Ausleihe umwandeln

### Geräteverwaltung und Auswertungen (Teil 5)

- `POST /api/geraete` `{inventarnummer, bezeichnung, kategorie, menge, angeschafft_am?}` — Gerät anlegen (`409` bei doppelter Inventarnummer)
- `PUT /api/geraete/{id}` `{bezeichnung, kategorie, menge, angeschafft_am?}` — Gerät bearbeiten (`409`, falls `menge` unter die aktuell gebundene Menge gesenkt würde)
- `POST /api/geraete/{id}/ausmustern` — Gerät ausmustern (nicht mehr ausleihbar/reservierbar, Historie bleibt erhalten, keine Reaktivierung)
- `GET /api/geraete?inkl_ausgemustert=true` — Geräteliste inkl. ausgemusterter Geräte (für die Verwaltungsansicht; Standard-Liste blendet sie aus)
- `GET /api/stats/top-personen` — wer hat aktuell die meisten offenen Ausleihen
- `GET /api/stats/top-geraete` — welche Geräte werden am häufigsten ausgeliehen (gesamt)
- `GET /api/stats/auslastung` — Auslastung je Kategorie (niedrig/mittel/hoch, Definition siehe [ANNAHMEN.md](ANNAHMEN.md#teil-5--verwaltung-und-auswertungen))

### Tests ausführen

```bash
docker compose exec backend pytest
```

### Frontend starten

```bash
cd frontend
npm install
npm start   # http://localhost:4200, erwartet Backend auf http://localhost:8000
```

## Projektstruktur

Siehe `.claude/CLAUDE.md` für die vollständige Zielstruktur. Aktuell vorhanden:

```
backend/
  app/
    api/           FastAPI-Router (import/*, geraete/*, ausleihen/*, leihfristen/*, reservierungen/*, stats/*)
    core/          Settings, DB-Session
    models/        SQLAlchemy-Modelle des sauberen Schemas
    schemas/       Pydantic-Request-/Response-Modelle
    services/      Business-Logik (Verfügbarkeit, Leihfristen, Reservierungen, Geräteverwaltung, Auswertungen)
    etl/           extract -> transform -> load -> report -> run
    tests/         pytest
  alembic/         Schema-Migrationen
frontend/
  src/app/
    core/          API-Client-Services, Modelle
    features/      geraete-liste, historie, ueberfaellig, reservierungen, import-report,
                    geraete-verwaltung (Teil 5), auswertungen (Teil 5)
data/
  altdaten_seed.sql   Rohdaten (unverändert, wird per Docker-Init geladen)
ANNAHMEN.md           Dokumentierte Annahmen/Geschäftsregeln je Teil
```

## Assumptions

Alle Entscheidungen zu unklaren Fachfragen (z. B. Umgang mit doppelter Inventarnummer, leerer Bezeichnung, unplausiblem Rückgabedatum) stehen in [ANNAHMEN.md](ANNAHMEN.md).
