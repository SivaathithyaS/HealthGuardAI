from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any, List
from backend.app.schemas.heart import HeartFeatures, PredictionResponse, RoadmapResponse
from backend.app.services.prediction_service import prediction_service
from backend.app.services.roadmap_service import roadmap_service

router = APIRouter(prefix="/heart", tags=["Heart Disease"])

# Curated benchmark presets from real patient test sets for rapid UI demoing
SAMPLE_PATIENTS = {
    "high_risk": {
        "title": "High Risk Patient (Severe Multi-Factor Profile)",
        "description": "62 yo with elevated cholesterol (394 mg/dL), resting BP 140 mm Hg, asymptomatic chest pain, and exercise ST depression.",
        "data": {
            "age": 62.0,
            "sex": 1,
            "cp": 3,
            "trestbps": 140.0,
            "chol": 394.0,
            "fbs": 0,
            "restecg": 0,
            "thalach": 157.0,
            "exang": 0,
            "oldpeak": 1.2,
            "slope": 1,
            "ca": 1,
            "thal": 2
        }
    },
    "moderate_risk": {
        "title": "Moderate / Borderline Risk Patient",
        "description": "58 yo with borderline hypertension (136 mm Hg), cholesterol 245 mg/dL, and mild exercise-induced angina.",
        "data": {
            "age": 58.0,
            "sex": 1,
            "cp": 1,
            "trestbps": 136.0,
            "chol": 245.0,
            "fbs": 1,
            "restecg": 1,
            "thalach": 142.0,
            "exang": 1,
            "oldpeak": 1.0,
            "slope": 1,
            "ca": 0,
            "thal": 2
        }
    },
    "low_risk": {
        "title": "Low Risk / Healthy Patient Profile",
        "description": "45 yo female with optimal BP (112 mm Hg), normal cholesterol (180 mg/dL), and excellent aerobic capacity (172 bpm).",
        "data": {
            "age": 45.0,
            "sex": 0,
            "cp": 0,
            "trestbps": 112.0,
            "chol": 180.0,
            "fbs": 0,
            "restecg": 0,
            "thalach": 172.0,
            "exang": 0,
            "oldpeak": 0.0,
            "slope": 0,
            "ca": 0,
            "thal": 1
        }
    }
}

@router.post("/predict", response_model=PredictionResponse)
def predict_heart_risk(features: HeartFeatures):
    try:
        return prediction_service.predict_heart_disease(features)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference error: {str(e)}"
        )

@router.post("/roadmap", response_model=RoadmapResponse)
def get_heart_roadmap(features: HeartFeatures):
    try:
        return roadmap_service.generate_roadmap(features)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Roadmap simulation error: {str(e)}"
        )

@router.get("/samples")
def get_sample_patients():
    return SAMPLE_PATIENTS
