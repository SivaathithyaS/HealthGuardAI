"""
Owned by: ML/Data role

Contract:
    generate_roadmap(disease: str, features: dict, shap_values: dict) -> dict
        returns: {
            "what_if": list[dict],     # [{"change": str, "new_risk_score": float}, ...]
            "goals": {
                "short_term": list[str],
                "medium_term": list[str],
                "long_term": list[str],
            }
        }
"""


def generate_roadmap(disease: str, features: dict, shap_values: dict) -> dict:
    raise NotImplementedError
