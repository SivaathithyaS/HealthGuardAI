from fastapi import APIRouter, HTTPException
from app.schemas.heart import HeartFeatures, PredictResponse
from app.services import prediction_service

router = APIRouter()


@router.post("/heart", response_model=PredictResponse)
def predict_heart(features: HeartFeatures):
    try:
        result = prediction_service.predict("heart", features.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result
