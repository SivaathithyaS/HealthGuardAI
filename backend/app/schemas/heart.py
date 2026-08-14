from pydantic import BaseModel, Field


class HeartFeatures(BaseModel):
    age: int = Field(..., ge=1, le=120)
    sex: int = Field(..., ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(..., ge=0, le=3, description="chest pain type (0-3)")
    trestbps: int = Field(..., ge=60, le=250, description="resting blood pressure")
    chol: int = Field(..., ge=100, le=600, description="serum cholesterol mg/dl")
    fbs: int = Field(..., ge=0, le=1, description="fasting blood sugar > 120 mg/dl")
    restecg: int = Field(..., ge=0, le=2)
    thalach: int = Field(..., ge=60, le=250, description="max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="exercise induced angina")
    oldpeak: float = Field(..., ge=0, le=10)
    slope: int = Field(..., ge=0, le=2)
    ca: int = Field(..., ge=0, le=4, description="number of major vessels colored")
    thal: int = Field(..., ge=0, le=3)


class PredictResponse(BaseModel):
    risk_score: float
    risk_label: str
    shap_values: dict
    top_factors: list


class RoadmapResponse(BaseModel):
    baseline_risk: float
    what_if: list
    goals: dict
