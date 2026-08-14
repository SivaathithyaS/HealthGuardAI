from fastapi import APIRouter, HTTPException
from app.schemas.heart import HeartFeatures, RoadmapResponse
from app.services import prediction_service, roadmap_service

router = APIRouter()


@router.post("/heart", response_model=RoadmapResponse)
def roadmap_heart(features: HeartFeatures):
    try:
        feats = features.model_dump()
        prediction = prediction_service.predict("heart", feats)
        result = roadmap_service.generate_roadmap("heart", feats, prediction["shap_values"])
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
