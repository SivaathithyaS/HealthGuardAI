import os
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, List
from backend.app.schemas.heart import HeartFeatures, PredictionResponse, ShapFactor

MODEL_PATH = "backend/data/heart_pipeline.pkl"

FEATURE_METADATA = {
    "age": {
        "label": "Age",
        "desc": "Patient age in years"
    },
    "sex": {
        "label": "Biological Sex",
        "desc": lambda v: "Male" if v == 1 else "Female"
    },
    "cp": {
        "label": "Chest Pain Pattern",
        "desc": lambda v: {0: "Typical Angina", 1: "Atypical Angina", 2: "Non-Anginal Pain", 3: "Asymptomatic"}.get(int(v), "Chest Pain")
    },
    "trestbps": {
        "label": "Resting Blood Pressure",
        "desc": lambda v: f"{v:.0f} mm Hg resting systolic BP"
    },
    "chol": {
        "label": "Serum Cholesterol",
        "desc": lambda v: f"{v:.0f} mg/dL circulating cholesterol"
    },
    "fbs": {
        "label": "Fasting Blood Sugar",
        "desc": lambda v: "Elevated (>120 mg/dL)" if v == 1 else "Normal (≤120 mg/dL)"
    },
    "restecg": {
        "label": "Resting ECG Result",
        "desc": lambda v: {0: "Normal", 1: "ST-T Wave Abnormality", 2: "Left Ventricular Hypertrophy"}.get(int(v), "ECG Finding")
    },
    "thalach": {
        "label": "Max Heart Rate Achieved",
        "desc": lambda v: f"{v:.0f} bpm under exercise stress"
    },
    "exang": {
        "label": "Exercise Induced Angina",
        "desc": lambda v: "Present during exertion" if v == 1 else "Absent"
    },
    "oldpeak": {
        "label": "ST Depression (Exercise)",
        "desc": lambda v: f"{v:.1f} mm depression relative to baseline"
    },
    "slope": {
        "label": "Peak Exercise ST Slope",
        "desc": lambda v: {0: "Upsloping", 1: "Flat", 2: "Downsloping"}.get(int(v), "ST Slope")
    },
    "ca": {
        "label": "Major Vessels Colored",
        "desc": lambda v: f"{int(v)} major coronary vessels visible"
    },
    "thal": {
        "label": "Thalassemia Test",
        "desc": lambda v: {1: "Normal Blood Flow", 2: "Fixed Defect", 3: "Reversible Defect"}.get(int(v), "Normal/Mild")
    }
}

class PredictionService:
    def __init__(self):
        self.artifact = None
        self._load_model()

    def _load_model(self):
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model artifact not found at {MODEL_PATH}. Train the model first.")
        self.artifact = joblib.load(MODEL_PATH)
        self.ensemble = self.artifact["ensemble_model"]
        self.explainer = self.artifact["shap_explainer"]
        self.feature_names = self.artifact["feature_names"]
        self.metrics = self.artifact.get("metrics", {})

    def predict_heart_disease(self, features: HeartFeatures) -> PredictionResponse:
        input_dict = features.model_dump()
        df = pd.DataFrame([input_dict])[self.feature_names]
        
        # Risk probability from soft voting ensemble
        proba = float(self.ensemble.predict_proba(df)[0, 1])
        risk_score = round(proba, 4)
        risk_pct = round(proba * 100.0, 1)
        
        if risk_score >= 0.65:
            risk_label = "High Risk"
            risk_color = "#ef4444"  # Red
        elif risk_score >= 0.35:
            risk_label = "Moderate Risk"
            risk_color = "#f59e0b"  # Amber
        else:
            risk_label = "Low Risk"
            risk_color = "#10b981"  # Emerald Green
            
        # Compute SHAP values
        shap_vals = self.explainer.shap_values(df)
        if isinstance(shap_vals, list):
            # Binary classification list [class 0, class 1]
            raw_shap = shap_vals[1][0]
        elif len(shap_vals.shape) == 3:
            raw_shap = shap_vals[0, :, 1]
        else:
            raw_shap = shap_vals[0]
            
        factors: List[ShapFactor] = []
        for feat_name, val, shap_val in zip(self.feature_names, df.iloc[0], raw_shap):
            shap_f = float(shap_val)
            meta = FEATURE_METADATA.get(feat_name, {"label": feat_name, "desc": str(val)})
            desc_func = meta["desc"]
            desc_str = desc_func(val) if callable(desc_func) else str(desc_func)
            
            factors.append(ShapFactor(
                feature=feat_name,
                feature_name=meta["label"],
                feature_value=val,
                shap_value=round(shap_f, 4),
                impact="increases_risk" if shap_f > 0 else "reduces_risk",
                description=desc_str
            ))
            
        # Sort by absolute impact
        sorted_factors = sorted(factors, key=lambda x: abs(x.shap_value), reverse=True)
        top_positive = [f for f in sorted_factors if f.shap_value > 0][:5]
        top_negative = [f for f in sorted_factors if f.shap_value < 0][:5]
        
        return PredictionResponse(
            disease="heart_disease",
            risk_score=risk_score,
            risk_percentage=risk_pct,
            risk_label=risk_label,
            risk_color=risk_color,
            model_metrics=self.metrics,
            shap_factors=sorted_factors,
            top_positive_factors=top_positive,
            top_negative_factors=top_negative
        )

prediction_service = PredictionService()
