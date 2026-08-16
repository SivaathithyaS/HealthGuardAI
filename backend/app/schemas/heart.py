from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Note: Field boundaries are anchored in the UCI Cleveland clinical training distribution
# to protect against unsafe model extrapolation while allowing full adult clinical range.
class HeartFeatures(BaseModel):
    age: float = Field(..., ge=29.0, le=77.0, description="Patient age in years (29 - 77)")
    sex: int = Field(..., ge=0, le=1, description="0 = Female, 1 = Male")
    cp: int = Field(..., ge=0, le=3, description="Chest Pain Type (0: Typical Angina, 1: Atypical Angina, 2: Non-anginal, 3: Asymptomatic)")
    trestbps: float = Field(..., ge=94.0, le=200.0, description="Resting Blood Pressure (mm Hg, 94 - 200)")
    chol: float = Field(..., ge=126.0, le=564.0, description="Serum Cholesterol in mg/dl (126 - 564)")
    fbs: int = Field(..., ge=0, le=1, description="Fasting Blood Sugar > 120 mg/dl (0 = No, 1 = Yes)")
    restecg: int = Field(..., ge=0, le=2, description="Resting ECG Results (0: Normal, 1: ST-T wave abnormality, 2: Left ventricular hypertrophy)")
    thalach: float = Field(..., ge=71.0, le=202.0, description="Maximum Heart Rate Achieved (71 - 202 bpm)")
    exang: int = Field(..., ge=0, le=1, description="Exercise Induced Angina (0 = No, 1 = Yes)")
    oldpeak: float = Field(..., ge=0.0, le=6.2, description="ST depression induced by exercise relative to rest (0.0 - 6.2)")
    slope: int = Field(..., ge=0, le=2, description="Slope of the peak exercise ST segment (0: Upsloping, 1: Flat, 2: Downsloping)")
    ca: int = Field(..., ge=0, le=3, description="Number of major vessels (0-3) colored by flourosopy")
    thal: int = Field(..., ge=0, le=3, description="Thalassemia (1: Normal, 2: Fixed Defect, 3: Reversible Defect)")

class ShapFactor(BaseModel):
    feature: str
    feature_name: str
    feature_value: Any
    shap_value: float
    impact: str  # "increases_risk" or "reduces_risk"
    description: str

class PredictionResponse(BaseModel):
    disease: str = "heart_disease"
    risk_score: float = Field(..., description="Calculated probability between 0.0 and 1.0")
    risk_percentage: float = Field(..., description="Calculated risk as percentage 0-100%")
    risk_label: str = Field(..., description="'Low Risk', 'Moderate Risk', or 'High Risk'")
    risk_color: str
    model_metrics: Dict[str, float]
    shap_factors: List[ShapFactor]
    top_positive_factors: List[ShapFactor]
    top_negative_factors: List[ShapFactor]

class WhatIfSimulation(BaseModel):
    feature: str
    feature_label: str
    current_value: float
    target_value: float
    change_description: str
    baseline_risk_score: float
    simulated_risk_score: float
    risk_reduction_pct: float
    category: str

class PreventionGoal(BaseModel):
    title: str
    action: str
    clinical_rationale: str
    impact_level: str  # "High", "Medium", "Moderate"

class StagedRoadmap(BaseModel):
    short_term: List[PreventionGoal]    # 1 - 4 Weeks
    medium_term: List[PreventionGoal]   # 1 - 3 Months
    long_term: List[PreventionGoal]     # 6+ Months

class RoadmapResponse(BaseModel):
    disease: str = "heart_disease"
    baseline_risk_score: float
    baseline_risk_label: str
    modifiable_what_if: List[WhatIfSimulation]
    maximum_possible_risk_reduction_pct: float
    staged_goals: StagedRoadmap
    clinical_disclaimer: str
