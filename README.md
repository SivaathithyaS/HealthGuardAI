# HealthGuard AI

An explainable hybrid machine learning framework for multi-disease risk prediction
and personalized preventive healthcare.

## Repo structure

```
HealthGuardAI/
├── frontend/        React + Tailwind UI                        → Frontend
├── backend/         FastAPI app (auth, routing, services)       → Backend
│   └── app/
│       ├── api/routes/     Endpoint definitions
│       ├── core/           Config, security, JWT
│       ├── models/         SQLAlchemy DB models
│       ├── schemas/        Pydantic request/response schemas
│       ├── services/       Prediction, roadmap, OCR, PDF logic  → shared: Backend + ML + Integration
│       └── db/              DB session, migrations
├── ml/               Datasets, notebooks, training, saved models → ML/Data
├── docker/           Dockerfiles, docker-compose               → Integration
├── docs/             Architecture notes, API contracts, diagrams
└── .github/workflows/ CI (lint/test on PR)
```

## Role → folder ownership

| Role | Owns | Also touches |
|---|---|---|
| ML/Data | `ml/` entirely | `backend/app/services/prediction_service.py`, `backend/app/services/roadmap_service.py` |
| Backend | `backend/app/api`, `core`, `models`, `schemas`, `db` | auth, DB schema, wiring services into routes |
| Frontend | `frontend/` entirely | `docs/api-contract.md` (consumes it) |
| Full-stack/Integration | `docker/`, `.github/`, `backend/app/services/ocr_service.py`, `pdf_service.py` | deployment config, ties everything together |

`backend/app/services/` is the seam where ML's model code gets wrapped into something
the API can call — ML and Backend should agree early on the function signature
(input dict → prediction + SHAP values out), documented in `docs/api-contract.md`.

## Git workflow (branch-based, shared repo)

We're using one shared repo with feature branches, not forks — simpler to keep in
sync for a 4-person team with write access.

1. Clone the repo once: `git clone <repo-url>`
2. Never commit to `main` directly. Branch per feature:
   `git checkout -b feature/<role>-<short-description>`
   e.g. `feature/ml-heart-disease-model`, `feature/frontend-auth-page`
3. Commit small, push often: `git push origin feature/<branch-name>`
4. Open a Pull Request into `main`. At least one other teammate reviews before merge.
5. Delete the branch after merge.

Branch naming convention: `feature/...`, `fix/...`, `docs/...`

## Getting started

Backend:
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```
cd frontend
npm install
npm run dev
```

Full stack (once Dockerfiles are filled in):
```
docker compose up --build
```

## Status

Early scaffolding — see `docs/` for architecture and API contract as they're defined.
