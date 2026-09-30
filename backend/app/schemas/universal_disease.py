from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class DecisionNodeStep(BaseModel):
    node_id: int
    step_number: int
    node_title: str
    clinical_criterion: str
    patient_observation: str
    split_condition_met: bool
    branch_direction: str
    clinical_significance: str

class ClinicalEvidenceTier(BaseModel):
    tier_number: int
    tier_label: str
    feature_name: str
    observed_finding: str
    clinical_interpretation: str
    clinical_consideration: str

class ConflictingEvidenceAlert(BaseModel):
    conflict_detected: bool = False
    conflict_title: Optional[str] = None
    conflicting_elements: List[str] = []
    clinical_explanation: Optional[str] = None
    reconciliation_guidance: Optional[str] = None

class ModifiableRiskFactorItem(BaseModel):
    risk_factor: str
    observed_value: str
    pathophysiologic_explanation: str
    tailored_prevention_protocol: str

class PreventionRoutineStep(BaseModel):
    timeframe: str  # "Daily (Morning)", "Daily (Evening)", "Week 1-2", "Days 1-30", "Months 1-3", "Months 3-6+"
    title: str
    action: str
    target_goal: str
    clinical_purpose: str

class RubricCriterion(BaseModel):
    criterion: str
    points: float
    max_points: float
    met: bool = True
    evidence: str

class ScoringRubric(BaseModel):
    scoring_method: str = "Weighted Clinical Rubric (Point-Factor System)"
    validation_cohort: str = "Northstar & Riverbend Clinical Validation Suite (N=10)"
    validation_date: str = "September 2026"
    total_score: float
    max_possible: float = 100.0
    methodology_description: str = "Explicit point-factor rubric weighting radiographic evidence, focal deficit match, mimic exclusion, and onset window."
    criteria: List[RubricCriterion] = []

class PlainLanguageSummary(BaseModel):
    urgency_tier: str  # e.g. "🔴 Time-Critical — Suspected Acute Stroke, Escalate Immediately"
    urgency_level: str # "CRITICAL", "MODERATE", "LOW"
    headline: str
    plain_language_bullets: List[str]
    concern_tier: str  # "Low Concern" (0-40), "Moderate — Review Recommended" (41-75), "High — Immediate Review Required" (76-100)
    key_action: str

class UniversalDifferential(BaseModel):
    condition_name: str
    medical_specialty: str
    affected_organs: List[str]
    ai_evidence_score: float
    diagnostic_certainty: str
    severity_category: str
    supporting_evidence: List[str]
    clinical_rationale: str
    rubric_breakdown: Optional[ScoringRubric] = None

class DiagnosticWorkupItem(BaseModel):
    test_name: str
    category: str
    clinical_purpose: str
    urgency: str

class EmergencyActionItem(BaseModel):
    title: str
    action: str
    clinical_rationale: str
    priority: str = "TIME_CRITICAL"
    requires_clinician: bool = True
    evidence_basis: List[str] = []

class LongTermPreventionItem(BaseModel):
    title: str
    action: str
    clinical_rationale: str
    target_metric: str
    evidence_basis: List[str] = []

class ExtractedParameter(BaseModel):
    name: str
    value: str
    numeric_value: Optional[float] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None
    status: str
    source_text: str

class PatientContext(BaseModel):
    name: str
    age: int
    gender: str
    mrn: str
    study_date: str
    ordering_department: str
    calculated_bmi: Optional[str] = None

class UniversalDiseaseAnalysisResult(BaseModel):
    analysis_id: str
    created_at: str
    document_id: str
    detected_modality: str
    detected_specialty: str
    primary_suspected_condition: str
    ai_evidence_score: float
    evidence_score_disclaimer: str = "This score represents model evidence strength and is not a calibrated probability of disease."
    diagnostic_certainty_level: str
    required_confirmation: str
    acuity_level: str
    affected_organ_systems: List[str]
    
    ai_safety_notice: str = "AI Safety Notice: This analysis summarizes extracted findings for educational and decision-support purposes. It does not establish a definitive clinical diagnosis. Critical findings must be verified by a qualified clinician."
    patient_context: PatientContext
    conflicting_evidence_alert: ConflictingEvidenceAlert
    three_tier_evidence: List[ClinicalEvidenceTier]
    modifiable_risk_factors: List[ModifiableRiskFactorItem]
    extracted_parameters: List[ExtractedParameter]
    decision_node_path: List[DecisionNodeStep]
    differential_considerations: List[UniversalDifferential]
    recommended_diagnostic_workup: List[DiagnosticWorkupItem]
    rubric_breakdown: Optional[ScoringRubric] = None
    plain_language_summary: Optional[PlainLanguageSummary] = None
    
    # Actionable Prevention Routines (Short-Term Days 1-30 vs Long-Term Months 1-6+)
    short_term_routine: List[PreventionRoutineStep]
    long_term_routine: List[PreventionRoutineStep]
    
    emergency_actions: List[EmergencyActionItem]
    long_term_prevention: List[LongTermPreventionItem]
    clinical_summary: str
    validation_status: str = "Demonstration Benchmark — Multi-Specialty Clinical Decision Support Evaluation"
