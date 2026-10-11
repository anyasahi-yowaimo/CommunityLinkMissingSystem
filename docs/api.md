# API guide

Interactive OpenAPI: `/docs`; schema: `/openapi.json`.

- `GET /health`, `GET /health/ready`
- `GET /api/clubs?q=&limit=`, `POST /api/clubs`, `GET /api/clubs/{id}`, `PATCH /api/clubs/{id}`
- `GET /api/needs?status=`, `POST /api/needs`, `PATCH /api/needs/{id}`
- `GET /api/recommendations?status=`, `POST /api/recommendations/generate`, `GET /api/recommendations/{id}`
- `POST /api/recommendations/{id}/feedback`, `/accept`, `/reject`
- `GET /api/analytics/overview`, `/quality`, `/graph`

JSON request errors use FastAPI/Pydantic validation responses (422). Missing records use 404, duplicate club names use 409, readiness database failures use 503. There is no authentication in this demo; that is a security limitation, not a production recommendation.
