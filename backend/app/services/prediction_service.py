"""
Loads the trained heart disease pipeline once at import time and exposes
predict(). Contract unchanged from the earlier stub so nothing else has to
change when more diseases are added later.
"""
import pickle
from pathlib import Path

_ARTIFACT_PATH = Path(__file__).resolve().parent.parent / "ml_models" / "heart_pipeline.pkl"

with open(_ARTIFACT_PATH, "rb") as f:
    _artifact = pickle.load(f)

_ensemble = _artifact["ensemble_model"]
_explainer_model = _artifact["explainer_model"]
_shap_explainer = _artifact["shap_explainer"]
FEATURE_ORDER = _artifact["feature_order"]
FEATURE_MEDIANS = _artifact["feature_medians"]


def _to_row(features: dict):
    """Order a features dict into the row order the model expects."""
    missing = [f for f in FEATURE_ORDER if f not in features]
    if missing:
        raise ValueError(f"Missing required features: {missing}")
    return [[features[f] for f in FEATURE_ORDER]]


def predict(disease: str, features: dict) -> dict:
    if disease != "heart":
        raise ValueError(f"Unsupported disease: {disease}")

    row = _to_row(features)

    risk_score = float(_ensemble.predict_proba(row)[0][1])
    risk_label = "high" if risk_score >= 0.6 else "moderate" if risk_score >= 0.3 else "low"

    shap_result = _shap_explainer(row)
    shap_dict = {
        feat: float(val) for feat, val in zip(FEATURE_ORDER, shap_result.values[0])
    }
    top_factors = sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)[:5]

    return {
        "risk_score": round(risk_score, 4),
        "risk_label": risk_label,
        "shap_values": shap_dict,
        "top_factors": [{"feature": f, "shap_value": round(v, 4)} for f, v in top_factors],
    }
