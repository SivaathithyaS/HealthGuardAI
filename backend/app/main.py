from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HealthGuard AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# from app.api.routes import auth, predict, roadmap, ocr, reports
# app.include_router(auth.router, prefix="/auth", tags=["auth"])
# app.include_router(predict.router, prefix="/predict", tags=["prediction"])
# app.include_router(roadmap.router, prefix="/roadmap", tags=["roadmap"])
# app.include_router(ocr.router, prefix="/ocr", tags=["ocr"])
# app.include_router(reports.router, prefix="/reports", tags=["reports"])


@app.get("/health")
def health_check():
    return {"status": "ok"}
