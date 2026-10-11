# Architecture

Browser HTML/CSS/vanilla JavaScript is served by FastAPI at `/`. The browser calls JSON endpoints on the same origin. FastAPI validates inputs with Pydantic, SQLAlchemy persists records, and the recommendation service reads current club/need/collaboration rows to generate candidate pairs. Recommendations are stored as snapshots with score components, evidence records, proposal fields, fingerprint, and model version.

NetworkX's `MultiDiGraph` is rebuilt from database rows when graph analytics is requested; it is not a second source of truth. Node identifiers use `club:<id>`, `need:<id>`, `skill:<canonical-name>`, and `resource:<canonical-name>`. Relationships are typed and include source/verification or permission attributes.

Ranking formula: `0.35*N + 0.25*C + 0.20*F + 0.15*A - 0.05*R`. Components are intended to lie in [0,1]. Current baseline calculates N from verified required-skill coverage, C from distinct verified skills and permitted required resources, F from simple schedule compatibility, A from title/description completeness, and R currently zero after duplicate hard-exclusion. A failed hard check is excluded before scoring.

## Trust boundaries and limitations

The app is a local synthetic-data demo. There is no real login, coordinator identity, or production authorization in this MVP. Do not expose it to untrusted networks. SQLite is the local default. PostgreSQL configuration exists for deployment but requires installing the driver and verifying migrations/deployment. Database tables are initialized from SQLAlchemy metadata; a production migration history remains future work.
