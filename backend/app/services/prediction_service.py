"""
Owned by: ML/Data role (wired into API by Backend role)

Contract:
    predict(disease: str, features: dict) -> dict
        returns: {
            "risk_score": float,          # 0-1
            "risk_label": str,             # "low" | "moderate" | "high"
            "shap_values": dict,           # feature_name -> contribution
            "top_factors": list[str],      # top 5 SHAP factors, ordered
        }

TODO: load trained models from ml/models/, wrap ensemble predict + SHAP explainer.
"""


def predict(disease: str, features: dict) -> dict:
    raise NotImplementedError
