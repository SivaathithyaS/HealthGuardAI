from pydantic import BaseModel, Field


class HeartFeatures(BaseModel):
    # These bounds reflect the actual ranges found in the UCI Heart Disease
    # training dataset. Values outside these ranges will be rejected because
    # the model has never seen them and predictions would be unreliable.
    age: int = Field(..., ge=29, le=77)
    sex: int = Field(..., ge=0, le=1, description="1 = male, 0 = female")
    cp: int = Field(..., ge=0, le=3, description="chest pain type (0-3)")
    trestbps: int = Field(..., ge=94, le=200, description="resting blood pressure")
    chol: int = Field(..., ge=126, le=564, description="serum cholesterol mg/dl")
    fbs: int = Field(..., ge=0, le=1, description="fasting blood sugar > 120 mg/dl")
    restecg: int = Field(..., ge=0, le=2)
    thalach: int = Field(..., ge=71, le=202, description="max heart rate achieved")
    exang: int = Field(..., ge=0, le=1, description="exercise induced angina")
    oldpeak: float = Field(..., ge=0, le=6.2)
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
