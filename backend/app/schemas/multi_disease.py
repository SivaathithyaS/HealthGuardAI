from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.heart import HeartFeatures, ShapFactor, WhatIfSimulation, PreventionGoal, StagedRoadmap

class DiabetesFeatures(BaseModel):
    pregnancies: float = Field(0.0, ge=0.0, le=20.0)
    glucose: float = Field(120.0, ge=40.0, le=400.0)
    blood_pressure: float = Field(75.0, ge=40.0, le=200.0)
    skin_thickness: float = Field(25.0, ge=5.0, le=100.0)
    insulin: float = Field(80.0, ge=5.0, le=900.0)
    bmi: float = Field(28.0, ge=14.0, le=70.0)
    diabetes_pedigree: float = Field(0.47, ge=0.05, le=3.0)
    age: float = Field(45.0, ge=18.0, le=100.0)

class CKDFeatures(BaseModel):
    age: float = Field(50.0, ge=12.0, le=95.0)
    bp: float = Field(80.0, ge=50.0, le=180.0)
    sg: float = Field(1.015, ge=1.005, le=1.030)
    al: float = Field(0.0, ge=0.0, le=5.0)
    su: float = Field(0.0, ge=0.0, le=5.0)
    bgr: float = Field(120.0, ge=60.0, le=500.0)
    bu: float = Field(40.0, ge=10.0, le=400.0)
    sc: float = Field(1.1, ge=0.4, le=50.0)
    sod: float = Field(138.0, ge=100.0, le=170.0)
    pot: float = Field(4.4, ge=2.0, le=10.0)
    hemo: float = Field(13.5, ge=3.0, le=19.0)
    pcv: float = Field(40.0, ge=9.0, le=60.0)
    wbcc: float = Field(8000.0, ge=2000.0, le=30000.0)
    rbcc: float = Field(4.8, ge=2.0, le=9.0)

class LiverFeatures(BaseModel):
    age: float = Field(45.0, ge=4.0, le=90.0)
    gender: int = Field(1, ge=0, le=1)
    total_bilirubin: float = Field(0.9, ge=0.3, le=80.0)
    direct_bilirubin: float = Field(0.2, ge=0.1, le=25.0)
    alkaline_phosphotase: float = Field(190.0, ge=50.0, le=2200.0)
    alamine_aminotransferase: float = Field(35.0, ge=5.0, le=2000.0)
    aspartate_aminotransferase: float = Field(38.0, ge=5.0, le=5000.0)
    total_protiens: float = Field(6.8, ge=2.5, le=10.0)
    albumin: float = Field(3.4, ge=0.8, le=6.0)
    albumin_and_globulin_ratio: float = Field(1.0, ge=0.2, le=3.0)

class DiseaseRiskResult(BaseModel):
    disease_key: str
    disease_name: str
    risk_score: float
    risk_percentage: float
    risk_label: str
    risk_color: str
    model_accuracy: float
    roc_auc: float
    top_drivers: List[ShapFactor]
    summary_message: str

class ExtractedBiomarker(BaseModel):
    name: str
    key: str
    value: float
    unit: str
    reference_range: str
    status: str
    status_color: str
    clinical_explanation: str

# Neuro-Oncology & Imaging Specific Schemas
class ImagingFinding(BaseModel):
    category: str
    observation: str
    significance: str
    severity: str  # "Critical", "Moderate", "Normal"

class DifferentialDiagnosis(BaseModel):
    condition_name: str
    probability_percentage: float
    who_grade: str
    rationale: str

class NeuroOncologyAssessment(BaseModel):
    primary_diagnosis: str
    malignancy_risk_score: float
    malignancy_risk_percentage: float
    acuity_level: str  # "🚨 Critical Neurosurgical Priority", "Urgent", "Routine"
    confidence_score: float
    mass_dimensions: str
    midline_shift_mm: float
    key_imaging_hallmarks: List[str]
    differential_ranking: List[DifferentialDiagnosis]
    critical_imaging_findings: List[ImagingFinding]
    recommended_clinical_pathway: List[PreventionGoal]

class ReportAnalysisResponse(BaseModel):
    document_type: str  # "brain_mri", "laboratory_bloodwork", "cardiopulmonary_report"
    document_type_display: str
    analysis_pathway: str  # "neuro_oncology", "cardiometabolic_multi_organ", etc.
    report_title: str
    patient_demographics: Dict[str, Any]
    detected_panels: List[str]
    overall_health_verdict: str
    
    # Pathway 1: Laboratory Bloodwork
    extracted_biomarkers: Optional[List[ExtractedBiomarker]] = []
    disease_assessments: Optional[Dict[str, DiseaseRiskResult]] = {}
    priority_prevention_goals: Optional[List[PreventionGoal]] = []
    
    # Pathway 2: Neuro-Oncology & Brain Imaging
    neuro_oncology: Optional[NeuroOncologyAssessment] = None
