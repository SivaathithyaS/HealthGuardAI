import copy
import pandas as pd
from typing import List, Dict, Any
from backend.app.schemas.heart import (
    HeartFeatures, RoadmapResponse, WhatIfSimulation,
    StagedRoadmap, PreventionGoal
)
from backend.app.services.prediction_service import prediction_service

MODIFIABLE_CONFIG = [
    {
        "feature": "chol",
        "label": "Serum Cholesterol",
        "category": "Lipid Profile",
        "unit": "mg/dL",
        "target_calc": lambda v: max(160.0, v - 40.0) if v > 200 else v,
        "is_applicable": lambda v: v > 200.0,
        "change_text": lambda cur, tgt: f"Reduce total cholesterol from {cur:.0f} to {tgt:.0f} mg/dL (-{cur-tgt:.0f} mg/dL) via dietary lipid management & statin therapy as prescribed.",
        "goals": {
            "short": PreventionGoal(
                title="Saturated Fat & Fiber Optimization",
                action="Limit saturated fat intake to <6% of daily calories; incorporate 10-25g soluble fiber daily (oats, legumes, psyllium husk).",
                clinical_rationale="Soluble fiber binds bile acids in the intestine, directly decreasing LDL-C synthesis and circulating cholesterol.",
                impact_level="High"
            ),
            "medium": PreventionGoal(
                title="Lipid Panel Follow-up & Statin Evaluation",
                action="Perform follow-up lipid profile (LDL-C, HDL-C, Triglycerides) at 8-12 weeks; review statin or ezetimibe eligibility with physician.",
                clinical_rationale="Assesses response to dietary interventions and ensures targeted LDL reduction to prevent atherosclerotic plaque progression.",
                impact_level="High"
            ),
            "long": PreventionGoal(
                title="Sustained Vascular Plaque Stabilization",
                action="Maintain long-term Mediterranean or DASH dietary pattern and annual advanced cardiovascular risk screening.",
                clinical_rationale="Continuous lipid control reduces long-term major adverse cardiovascular events (MACE) by over 25-30%.",
                impact_level="High"
            )
        }
    },
    {
        "feature": "trestbps",
        "label": "Resting Blood Pressure",
        "category": "Hypertension Management",
        "unit": "mm Hg",
        "target_calc": lambda v: max(118.0, v - 18.0) if v > 130 else v,
        "is_applicable": lambda v: v > 125.0,
        "change_text": lambda cur, tgt: f"Lower resting systolic BP from {cur:.0f} to {tgt:.0f} mm Hg (-{cur-tgt:.0f} mm Hg) via sodium restriction, stress reduction & antihypertensive protocol.",
        "goals": {
            "short": PreventionGoal(
                title="Daily Home BP Monitoring & Sodium Reduction",
                action="Log resting blood pressure twice daily (morning/evening) and restrict dietary sodium to <1,500 mg per day.",
                clinical_rationale="Low sodium intake rapidly attenuates systemic vascular resistance and reduces cardiac afterload within 2-4 weeks.",
                impact_level="High"
            ),
            "medium": PreventionGoal(
                title="Aerobic Cardiovascular Conditioning",
                action="Engage in 150 minutes/week of moderate-intensity zone 2 aerobic exercise (brisk walking, cycling, swimming).",
                clinical_rationale="Promotes arterial compliance, endothelial nitric oxide bioavailability, and sustained BP reduction of 5-8 mm Hg.",
                impact_level="High"
            ),
            "long": PreventionGoal(
                title="Long-Term Arterial Wall Remodeling",
                action="Sustain normotensive targets (<120/80 mm Hg) with periodic ambulatory blood pressure monitoring.",
                clinical_rationale="Prevents left ventricular hypertrophy, hypertensive heart disease, and vascular remodeling.",
                impact_level="High"
            )
        }
    },
    {
        "feature": "thalach",
        "label": "Max Heart Rate / Aerobic Fitness",
        "category": "Cardiorespiratory Fitness",
        "unit": "bpm",
        "target_calc": lambda v: min(175.0, v + 20.0) if v < 155 else v,
        "is_applicable": lambda v: v < 155.0,
        "change_text": lambda cur, tgt: f"Increase peak exercise capacity and heart rate reserve from {cur:.0f} to {tgt:.0f} bpm (+{tgt-cur:.0f} bpm) via aerobic interval training.",
        "goals": {
            "short": PreventionGoal(
                title="Base Aerobic Conditioning",
                action="Start with 20-30 minute low-impact aerobic sessions 3-4 times per week keeping heart rate in conversational zone.",
                clinical_rationale="Builds mitochondrial density and enhances stroke volume without inducing excessive myocardial strain.",
                impact_level="Medium"
            ),
            "medium": PreventionGoal(
                title="High-Aerobic Interval Progression",
                action="Introduce supervised aerobic interval sessions (e.g. 4x4 min intervals at 85% peak HR) twice weekly.",
                clinical_rationale="Significantly enhances VO2 max and autonomic tone, lowering resting heart rate and all-cause mortality risk.",
                impact_level="Medium"
            ),
            "long": PreventionGoal(
                title="Comprehensive Physical Fitness Standard",
                action="Achieve and maintain functional aerobic capacity in the upper quartile for age and sex bracket.",
                clinical_rationale="Each 1-MET increase in cardiorespiratory fitness is associated with a 12-15% reduction in cardiovascular mortality.",
                impact_level="Medium"
            )
        }
    },
    {
        "feature": "oldpeak",
        "label": "Exercise ST Depression (Ischemic Burden)",
        "category": "Ischemic Conditioning",
        "unit": "mm",
        "target_calc": lambda v: max(0.0, v - 1.0) if v > 0.5 else v,
        "is_applicable": lambda v: v > 0.5,
        "change_text": lambda cur, tgt: f"Reduce exercise-induced myocardial ischemia marker from {cur:.1f} to {tgt:.1f} mm through medical therapy and medically supervised conditioning.",
        "goals": {
            "short": PreventionGoal(
                title="Clinical Stress Evaluation",
                action="Review ischemic ECG changes with a cardiologist; evaluate need for anti-ischemic pharmacotherapy (e.g. beta-blockers, ACEi).",
                clinical_rationale="Prevents exercise-induced subendocardial hypoperfusion during routine physical activity.",
                impact_level="High"
            ),
            "medium": PreventionGoal(
                title="Supervised Cardiac Rehabilitation",
                action="Participate in a monitored cardiac rehabilitation program with continuous ECG telemetry.",
                clinical_rationale="Stimulates coronary collateralization and raises the ischemic threshold safely.",
                impact_level="High"
            ),
            "long": PreventionGoal(
                title="Serial Non-Invasive Stress Testing",
                action="Repeat exercise stress test or myocardial perfusion imaging annually to assess myocardial perfusion recovery.",
                clinical_rationale="Documents resolution or stabilization of exertion-related coronary insufficiency.",
                impact_level="Medium"
            )
        }
    },
    {
        "feature": "fbs",
        "label": "Fasting Blood Sugar",
        "category": "Glycemic Control",
        "unit": "flag",
        "target_calc": lambda v: 0.0,
        "is_applicable": lambda v: v == 1,
        "change_text": lambda cur, tgt: "Normalize fasting blood glucose to <100 mg/dL through low-glycemic nutrition, weight loss, and insulin sensitivity restoration.",
        "goals": {
            "short": PreventionGoal(
                title="Low-Glycemic Dietary Transition",
                action="Eliminate sugar-sweetened beverages and refined carbohydrates; replace with complex whole grains and healthy fats.",
                clinical_rationale="Reduces postprandial glucose surges and attenuates vascular endothelial oxidative stress.",
                impact_level="Medium"
            ),
            "medium": PreventionGoal(
                title="HbA1c Testing & Metformin Consideration",
                action="Check baseline HbA1c; evaluate insulin resistance metrics (HOMA-IR) with endocrinologist or primary care physician.",
                clinical_rationale="Tight glycemic control prevents microvascular endothelial damage and premature arterial stiffening.",
                impact_level="High"
            ),
            "long": PreventionGoal(
                title="Long-Term Metabolic Homeostasis",
                action="Maintain fasting glucose <100 mg/dL and HbA1c <5.7% through ongoing lifestyle consistency.",
                clinical_rationale="Reverses prediabetic vascular risk and eliminates diabetic macrovascular acceleration.",
                impact_level="High"
            )
        }
    }
]

class RoadmapService:
    def generate_roadmap(self, features: HeartFeatures) -> RoadmapResponse:
        base_resp = prediction_service.predict_heart_disease(features)
        base_risk = base_resp.risk_score
        
        input_dict = features.model_dump()
        what_if_list: List[WhatIfSimulation] = []
        
        short_goals: List[PreventionGoal] = []
        medium_goals: List[PreventionGoal] = []
        long_goals: List[PreventionGoal] = []
        
        # Compound counterfactual test
        compound_features = copy.deepcopy(input_dict)
        
        for cfg in MODIFIABLE_CONFIG:
            feat = cfg["feature"]
            curr_val = float(input_dict[feat])
            
            if cfg["is_applicable"](curr_val):
                tgt_val = float(cfg["target_calc"](curr_val))
                if tgt_val != curr_val:
                    # Single feature counterfactual re-inference
                    sim_dict = copy.deepcopy(input_dict)
                    sim_dict[feat] = tgt_val
                    sim_features = HeartFeatures(**sim_dict)
                    sim_resp = prediction_service.predict_heart_disease(sim_features)
                    
                    # Risk reduction calculation with monotonic safety
                    reduction = max(0.0, round((base_risk - sim_resp.risk_score) * 100.0, 1))
                    
                    if reduction > 0.0:
                        what_if_list.append(WhatIfSimulation(
                            feature=feat,
                            feature_label=cfg["label"],
                            current_value=curr_val,
                            target_value=tgt_val,
                            change_description=cfg["change_text"](curr_val, tgt_val),
                            baseline_risk_score=base_risk,
                            simulated_risk_score=sim_resp.risk_score,
                            risk_reduction_pct=reduction,
                            category=cfg["category"]
                        ))
                        
                        # Add targeted goals
                        goals_dict = cfg["goals"]
                        short_goals.append(goals_dict["short"])
                        medium_goals.append(goals_dict["medium"])
                        long_goals.append(goals_dict["long"])
                        
                        # Update compound vector
                        compound_features[feat] = tgt_val
                        
        # Sort what-if simulations by risk reduction magnitude
        what_if_list = sorted(what_if_list, key=lambda x: x.risk_reduction_pct, reverse=True)
        
        # Calculate maximum possible compound risk reduction
        compound_sim_features = HeartFeatures(**compound_features)
        compound_resp = prediction_service.predict_heart_disease(compound_sim_features)
        max_reduction = max(0.0, round((base_risk - compound_resp.risk_score) * 100.0, 1))
        
        # Fallback if already low risk or no modifiable factor produced reduction
        if not short_goals:
            short_goals.append(PreventionGoal(
                title="Baseline Cardiovascular Maintenance",
                action="Maintain current regular physical activity (minimum 150 min/wk) and balanced heart-healthy diet.",
                clinical_rationale="Your current clinical parameters are within favorable ranges. Routine maintenance preserves vascular elasticity.",
                impact_level="Medium"
            ))
            medium_goals.append(PreventionGoal(
                title="Routine Annual Health Check",
                action="Schedule an annual comprehensive metabolic and lipid panel to ensure markers remain stable over time.",
                clinical_rationale="Early detection of age-related metabolic shifts enables prompt, gentle lifestyle adjustments.",
                impact_level="Medium"
            ))
            long_goals.append(PreventionGoal(
                title="Lifelong Healthy Habits",
                action="Sustain tobacco-free living, stress resilience practices, and continuous cardiovascular activity.",
                clinical_rationale="Guards against cumulative cardiovascular risk as age advances.",
                impact_level="High"
            ))

        return RoadmapResponse(
            disease="heart_disease",
            baseline_risk_score=base_risk,
            baseline_risk_label=base_resp.risk_label,
            modifiable_what_if=what_if_list,
            maximum_possible_risk_reduction_pct=max_reduction,
            staged_goals=StagedRoadmap(
                short_term=short_goals[:3],
                medium_term=medium_goals[:3],
                long_term=long_goals[:3]
            ),
            clinical_disclaimer="HealthGuard AI is an investigative clinical decision support tool designed for preventive education. It is not a substitute for formal diagnostic medical evaluation."
        )

roadmap_service = RoadmapService()
