"""
Prevention roadmap: takes a patient's features + their prediction, simulates
what happens to their risk score if modifiable factors improve, and generates
templated short/medium/long-term goals from the top SHAP-driven factors.

This is intentionally rule-based rather than another ML model — the novelty
claim is the *loop* (explain -> simulate -> recommend), not a fancier model.
"""
from app.services import prediction_service as pred

# Only features a person can realistically influence through lifestyle changes.
# (age, sex, thal, ca are not modifiable and are excluded from what-if simulation.)
MODIFIABLE = {
    "chol": {
        "label": "Cholesterol",
        "improve_delta": -30,
        "goal_short": "Cut saturated fat intake; aim to lower cholesterol by 10-15 mg/dL in 4-6 weeks.",
        "goal_medium": "Adopt a Mediterranean-style diet consistently for 3 months.",
        "goal_long": "Target cholesterol under 200 mg/dL within 6-12 months.",
    },
    "trestbps": {
        "label": "Resting blood pressure",
        "improve_delta": -10,
        "goal_short": "Reduce sodium intake and monitor blood pressure weekly.",
        "goal_medium": "Build a routine of 30 min moderate cardio, 5x/week, for 3 months.",
        "goal_long": "Sustain blood pressure under 130/80 mmHg long-term.",
    },
    "thalach": {
        "label": "Max heart rate achieved (fitness proxy)",
        "improve_delta": +15,
        "goal_short": "Start with 15-20 min brisk walks, 4x/week.",
        "goal_medium": "Progress to structured cardio training over 8-12 weeks.",
        "goal_long": "Reach a sustainable fitness level with improved exercise tolerance.",
    },
    "oldpeak": {
        "label": "ST depression (exercise-induced)",
        "improve_delta": -0.5,
        "goal_short": "Get cleared by a doctor for a structured exercise stress plan.",
        "goal_medium": "Follow a supervised cardiac-safe exercise program for 2-3 months.",
        "goal_long": "Re-test via stress ECG in 6 months to track improvement.",
    },
    "fbs": {
        "label": "Fasting blood sugar",
        "improve_delta": -1,  # binary feature: 1 -> 0
        "goal_short": "Reduce refined sugar/carb intake; monitor fasting glucose.",
        "goal_medium": "Work toward HbA1c in normal range over 3 months.",
        "goal_long": "Maintain fasting blood sugar under 100 mg/dL long-term.",
    },
}


def generate_roadmap(disease: str, features: dict, shap_values: dict) -> dict:
    if disease != "heart":
        raise ValueError(f"Unsupported disease: {disease}")

    baseline = pred.predict(disease, features)
    baseline_risk = baseline["risk_score"]

    # Rank modifiable features by how much they're currently hurting this patient
    # (positive SHAP value = increasing risk), restricted to ones we can simulate.
    modifiable_factors = [
        (feat, val) for feat, val in shap_values.items()
        if feat in MODIFIABLE and val > 0
    ]
    modifiable_factors.sort(key=lambda x: x[1], reverse=True)

    what_if = []
    for feat, _ in modifiable_factors[:3]:
        adjusted = dict(features)
        new_val = adjusted[feat] + MODIFIABLE[feat]["improve_delta"]
        if feat == "fbs":
            new_val = 0
        adjusted[feat] = max(new_val, 0)

        new_result = pred.predict(disease, adjusted)
        what_if.append({
            "feature": feat,
            "label": MODIFIABLE[feat]["label"],
            "change": f"{features[feat]} -> {adjusted[feat]}",
            "baseline_risk": baseline_risk,
            "new_risk_score": new_result["risk_score"],
            "risk_reduction": round(baseline_risk - new_result["risk_score"], 4),
        })

    goals = {"short_term": [], "medium_term": [], "long_term": []}
    for feat, _ in modifiable_factors[:3]:
        info = MODIFIABLE[feat]
        goals["short_term"].append(info["goal_short"])
        goals["medium_term"].append(info["goal_medium"])
        goals["long_term"].append(info["goal_long"])

    if not modifiable_factors:
        goals["short_term"].append(
            "Your top risk factors are non-modifiable (age, sex, or genetic markers). "
            "Discuss monitoring frequency with a doctor."
        )

    return {"baseline_risk": baseline_risk, "what_if": what_if, "goals": goals}
