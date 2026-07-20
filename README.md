# Geräteverleih

Ersatz für die bisherige Excel-Verleihliste eines internen Geräteverleihs. Umsetzung erfolgt schrittweise entlang der Teile aus `AUFGABE.md`; aktuell ist **Teil 1 (Datenübernahme)** umgesetzt.

## Tech-Stack

- **Datenbank:** PostgreSQL (per Docker Compose)
- **Backend:** Python, FastAPI, SQLAlchemy 2.0, Alembic
- **ETL:** pandas (Extraktion + Iteration), reine Python-Funktionen für die Validierungslogik (leicht testbar ohne DB)
- **Tests:** pytest
- **Frontend:** Angular (folgt ab Teil 2)

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

### Tests ausführen

```bash
docker compose exec backend pytest
```

## Projektstruktur

Siehe `.claude/CLAUDE.md` für die vollständige Zielstruktur. Aktuell vorhanden:

```
backend/
  app/
    api/           FastAPI-Router (Teil 1: /api/import/*)
    core/          Settings, DB-Session
    models/        SQLAlchemy-Modelle des sauberen Schemas
    schemas/       Pydantic-Response-Modelle
    etl/           extract -> transform -> load -> report -> run
    tests/         pytest
  alembic/         Schema-Migrationen für geraete/ausleihen/import_report
data/
  altdaten_seed.sql   Rohdaten (unverändert, wird per Docker-Init geladen)
ANNAHMEN.md           Dokumentierte Annahmen/Geschäftsregeln je Teil
```

## Assumptions

Alle Entscheidungen zu unklaren Fachfragen (z. B. Umgang mit doppelter Inventarnummer, leerer Bezeichnung, unplausiblem Rückgabedatum) stehen in [ANNAHMEN.md](ANNAHMEN.md).
