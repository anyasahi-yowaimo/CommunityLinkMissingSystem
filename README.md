
# LinkMissing

A local, evidence-first collaboration discovery prototype for student communities. It uses Python/FastAPI, SQLAlchemy, SQLite by default, NetworkX, and a browser frontend built with plain HTML/CSS/JavaScript. No React, TypeScript, Node build, JDK, XAMPP, paid AI API, or Docker is required to run the local demo.

**Synthetic-data warning:** all seeded clubs, profiles, needs, and partnerships are fictional. Ranking scores are not probabilities of success. This is a hackathon MVP, not production-secure software.

## Windows quick start

1. Install Python 3.11+ (Python 3.13 is suitable).
2. Extract the ZIP to a writable folder.
3. Double-click `start_windows.bat`. The script creates `.venv`, installs dependencies, seeds the database, and starts the web server.
4. Open `http://127.0.0.1:8000`.
5. API docs: `http://127.0.0.1:8000/docs`.

First setup requires internet to install packages. After packages are installed, the local app and SQLite database work offline. Do not close the terminal while using the server.

## Manual commands

From the extracted project directory in PowerShell:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
cd backend
$env:PYTHONPATH = (Get-Location).Path
python scripts\seed_demo_data.py
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Run tests from `backend` after activating the environment:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m pytest -q
```

Run the local smoke benchmark from the project root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
python -m evaluation.benchmark.run_benchmark
```

## Features in this build

- Persistent club and need records in SQLite.
- Database-backed recommendation generation with hard checks for active status, willingness, schedule, workload, verified skills, resource permission, and duplicate recorded scope.
- NetworkX graph rebuilt from persisted club, skill, resource, need, and collaboration data.
- Stored recommendation snapshots, score components, evidence references, proposal, and model version.
- Club creation/editing, need creation/resolution, recommendation detail, feedback, accept/reject, analytics and OpenAPI docs.
- Deterministic seed script for 20 synthetic clubs.

## Important limitations

- SQLite is the local default. PostgreSQL deployment is a documented next step; Docker Compose is supplied but was not verified in this environment.
- This prototype has no real identity provider or production RBAC. Do not expose it to the public internet or store sensitive data.
- No three-club recommendation generator, full collaboration lifecycle UI, user accounts, Alembic revision history, or full fixed-label benchmark is claimed as complete.
- The current benchmark is a smoke run and intentionally does not invent Precision@5 or Recall@5 without a frozen, complete ground-truth set.
- The recommendation model is a deterministic baseline, not a trained ML model. No external AI service is needed.
- Profile permissions and availability are demo fields and should be coordinator-verified in a real pilot.

See `docs/architecture.md`, `docs/api.md`, `docs/demo_script.md`, and `evaluation/README.md`.
# LinkMissingSystem
This is the AI-powered student connection and community discovery platform.
