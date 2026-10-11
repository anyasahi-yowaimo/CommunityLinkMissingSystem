# Verification report

Environment used in this build container: Python 3.13.5, FastAPI 0.128.2, SQLAlchemy 2.0.50, NetworkX 3.6.1, pytest 9.0.2, HTTPX 0.28.1. Docker is not installed in the build container.

- Backend tests: **6 passed**, 0 failed (command: `cd backend && PYTHONPATH=. python -m pytest -q`).
- Seed idempotence: run twice; both runs reported 20 clubs, 7 needs, and 2 collaboration records.
- Local TestClient smoke: `/` returned 200; `/static/app.js` returned 200; `/health/ready` returned 200 with database connected.
- Recommendation generation: HTTP 200 and produced candidates from seeded records (3 candidates on the fresh verification database after the seed was run twice).
- Recommendation listing, overview analytics, and graph analytics returned HTTP 200.
- NetworkX graph was built from current database rows.
- Full real HTTP server process was not independently exercised in this container; Windows launcher is provided but needs user-side verification on Windows.
- Docker Compose/PostgreSQL deployment was not run because Docker is unavailable here.
- Precision@5 / Recall@5 and keyword-baseline comparison are **not reported** because a frozen, complete labelled benchmark was not implemented in this MVP. Do not infer real-world performance from the local smoke benchmark.

## Scope still incomplete

Production authentication/RBAC; complete resource/project CRUD APIs; formal Alembic migration revisions; full fixed-label benchmark and keyword baseline; full required synthetic edge-case matrix; three-club proposal generation/removal test; and end-to-end browser automation remain incomplete. The app is a functional local MVP, not the entire acceptance list from the master specification.
