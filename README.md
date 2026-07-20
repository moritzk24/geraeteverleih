# Geräteverleih

Ersatz für die bisherige Excel-Verleihliste eines internen Geräteverleihs. Umsetzung erfolgt schrittweise entlang der Teile aus `AUFGABE.md`; aktuell sind **Teil 1 (Datenübernahme)** und **Teil 2 (Verleih)** umgesetzt.

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
    api/           FastAPI-Router (Teil 1: /api/import/*, Teil 2: /api/geraete/*, /api/ausleihen/*)
    core/          Settings, DB-Session
    models/        SQLAlchemy-Modelle des sauberen Schemas
    schemas/       Pydantic-Request-/Response-Modelle
    services/      Business-Logik (Teil 2: Verfügbarkeitsberechnung)
    etl/           extract -> transform -> load -> report -> run
    tests/         pytest
  alembic/         Schema-Migrationen für geraete/ausleihen/import_report
frontend/
  src/app/
    core/          API-Client-Services, Modelle
    features/      geraete-liste (Übersicht + Ausleihe), historie (Historie + Rückgabe)
data/
  altdaten_seed.sql   Rohdaten (unverändert, wird per Docker-Init geladen)
ANNAHMEN.md           Dokumentierte Annahmen/Geschäftsregeln je Teil
```

## Assumptions

Alle Entscheidungen zu unklaren Fachfragen (z. B. Umgang mit doppelter Inventarnummer, leerer Bezeichnung, unplausiblem Rückgabedatum) stehen in [ANNAHMEN.md](ANNAHMEN.md).
