# AGENT.md — Geräteverleih Practice Task

## 0. Source of truth

`AUFGABE.md` (attached in repo root) is the canonical spec. This file governs *how* you work, not *what* the app does — if the two conflict on scope, AUFGABE.md wins.

## 1. Hard rule: plan before code

For every part of the task (Teil 1–6), do the following in order:

1. **Plan first.** Write a short plan covering: what you'll build, the data model / schema changes, API endpoints (method, path, request/response), edge cases you found, and any assumption you're making where AUFGABE.md leaves a decision open (availability, overdue, utilization, dirty-data handling, etc.).
2. **Stop. Wait for explicit approval** ("go", "approved", "sieht gut aus", etc.) before writing any code. Do not pre-emptively scaffold files while "just drafting the plan."
3. **Implement only that part.** Don't jump ahead to later Teile even if the solution is obvious — the parts build on each other and I want to review incrementally.
4. **Report back.** After implementing, summarize what changed, call out deviations from the plan, and list new assumptions. Then stop again before starting the next part.

If a business rule is ambiguous and consequential (e.g. what counts as "available"), don't silently pick one — state it in the plan, and write it into `ANNAHMEN.md` once approved.

## 2. Tech stack (fixed, do not deviate without asking)

- **Database:** PostgreSQL, run via Docker Compose (not SQLite — explicitly forbidden by the task).
- **Backend:** Python. FastAPI recommended (async, pydantic validation, good fit for a small CRUD+ETL app) — confirm or override before Teil 1 planning.
- **Frontend:** Angular.
- **ETL / migration:** Python, using pandas for the cleaning/transform steps.
- **Testing:** pytest, focused on the availability and reservation logic (required by Teil 4, not a nice-to-have).
- **Migrations (schema):** Alembic (or equivalent) for the clean schema, separate from the one-off ETL import script.

## 3. Repository layout

```
/backend
  /app
    /api            FastAPI routers (thin — no business logic here)
    /core            settings, DB session, config
    /models          SQLAlchemy models (clean schema)
    /schemas         pydantic request/response models
    /services        business logic: availability, due-date calc, reservation checks, stats
    /etl
      extract.py     read alt_inventar / alt_ausleihen
      transform.py   cleaning + row-level validation/decisions
      load.py        write into clean schema
      report.py      build + persist the import report
      run.py         orchestrates extract -> transform -> load -> report, idempotent
    /tests           pytest, esp. availability/reservation edge cases
  /migrations        Alembic
  Dockerfile
/frontend              Angular app
/data                  altdaten_seed.sql (given, do not edit)
docker-compose.yml     postgres + backend (+ frontend if containerized)
ANNAHMEN.md            all documented assumptions/business rules, one place
TEIL6.md               the short written part (data observations + 3 questions)
README.md              setup + how to run + how to run the import + how to run tests
```

Rationale for calling this out explicitly: the task is graded partly on "Denkweise und Handwerk" (thinking and craftsmanship), so keeping ETL, business logic, and API routing in separate layers is itself part of the deliverable, not just internal hygiene.

## 4. ETL / migration layer requirements (Teil 1)

- Must be **re-runnable / idempotent** — running it twice shouldn't duplicate rows.
- Structured as distinct, independently testable steps: **extract → validate/transform → load → report.**
- Each row from `alt_inventar` / `alt_ausleihen` gets a disposition: `accepted`, `accepted_with_caveat`, or `rejected`, with a human-readable reason.
- The import report is **persisted** (its own table, e.g. `import_report`) and exposed via API or UI — not just printed to console, per the spec.
- Validation rules must be explicit and enumerable in the plan before coding (e.g. unparseable dates, missing/negative Menge, duplicate Inventarnummer, inconsistent category labels, empty vs. malformed Rückgabedatum). List them, don't invent silently.

## 5. Definition of done per part

- **Teil 1:** migration script/endpoint runs against the seeded Postgres container; import report queryable; ANNAHMEN.md has the dirty-data decisions.
- **Teil 2:** device list with search/filter (free text, category, "available only"); create/return a loan with availability check and a clear rejection reason when unavailable; history by device and by person.
- **Teil 3:** loan-period rules in a config table (not hardcoded); due date computed and shown on loan creation; an overdue view.
- **Teil 4:** reservations with availability check across open loans (on-time and overdue) and other reservations; cancel; pickup converts reservation → loan; a handful of well-chosen unit tests on the availability/reservation logic.
- **Teil 5:** device CRUD incl. retire (soft-delete, history retained, no longer loanable); a small stats view (most-borrowed person, most-borrowed devices, utilization per category — definition documented).
- **Teil 6:** half-page write-up, data observations + 3 questions for the client's office lead. Plain markdown, not code.

## 6. Communication protocol

- Plan messages: goal, schema delta, endpoints, edge cases/assumptions, test plan. Keep it scannable, not a wall of text.
- Do not start implementation in the same turn as the plan.
- Progress updates after implementing: concise — what was built, what deviated, what's next. No step-by-step narration of tool calls.
- Time-box awareness: the task is scoped for ~4–6 hours of human effort; don't gold-plate. If something is cut, say so explicitly (this is required by the task, not optional).

## 7. Explicitly out of scope unless time remains

CSV export of overdue loans, QR code per device, notification concept (sketch only, per spec — do not build). Only touch these after Teil 1–6 are done and approved.