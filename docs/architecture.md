# Architecture overview

React frontend → FastAPI backend (JWT auth) → four core services:
  - prediction_service   (hybrid ensemble + SHAP)      [ML/Data]
  - roadmap_service       (what-if sim + goals)          [ML/Data]
  - ocr_service            (report extraction)             [Integration]
  - pdf_service             (report export)                  [Integration]

All services read/write a shared data layer:
  - PostgreSQL   (users, prediction history, roadmap progress)
  - Model store  (trained model artifacts, loaded at API startup)

See the architecture diagram from the capstone review deck for the visual version.
