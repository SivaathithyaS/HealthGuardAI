from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.routes.heart_routes import router as heart_router
from backend.app.routes.report_routes import router as report_router
from backend.app.routes.analysis_routes import router as analysis_router

app = FastAPI(
    title="HealthGuard AI — Multimodal Clinical Decision Support Platform",
    description="Multimodal Clinical Intelligence, Document-Aware AI Screening, Explainability & Prevention Architecture.",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(analysis_router)
app.include_router(heart_router)
app.include_router(report_router)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "HealthGuard AI Multimodal Platform",
        "architecture": "Document Classifier + Modality Router + Isolated Analysis Lifecycle",
        "supported_modalities": ["BRAIN_MRI_REPORT", "LAB_REPORT", "BRAIN_CT_REPORT", "ECG_REPORT"],
        "active_models": ["neuro_oncology_v1.4", "cardiovascular_v1.1", "diabetes_v1.1", "ckd_v1.1", "liver_v1.1"],
        "version": "2.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
