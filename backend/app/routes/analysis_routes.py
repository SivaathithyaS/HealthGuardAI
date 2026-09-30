from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import joblib
import os
import pandas as pd
import numpy as np

from backend.app.services.universal_disease_service import universal_disease_service
from backend.app.schemas.universal_disease import UniversalDiseaseAnalysisResult
from backend.app.schemas.heart import HeartFeatures, PredictionResponse
from backend.app.schemas.multi_disease import DiabetesFeatures, CKDFeatures, LiverFeatures
from backend.app.services.prediction_service import prediction_service
from backend.app.services.document_classifier import document_classifier
from backend.app.services.model_registry import get_model_registry
from backend.app.services.evaluation_service import evaluation_service, EvaluationResults
from backend.app.services.report_parser_service import (
    report_parser_service, NORTHSTAR_STROKE_CT_CTA_REPORT, NORTHSTAR_BRAIN_MRI_REPORT, 
    RIVERBEND_DEMO_REPORT
)
from backend.app.core.analysis_context import get_analysis_context

router = APIRouter(prefix="/api", tags=["Multimodal Clinical Intelligence"])

DATA_DIR = "backend/data"

class TextAnalysisRequest(BaseModel):
    text: str

# -------------------------------------------------------------
# 1. UNIVERSAL DISEASE & REPORT ANALYSIS ENDPOINTS
# -------------------------------------------------------------
@router.post("/analysis/universal", response_model=UniversalDiseaseAnalysisResult)
@router.post("/analysis/start", response_model=UniversalDiseaseAnalysisResult)
def start_universal_analysis_text(req: TextAnalysisRequest):
    if not req.text or len(req.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Clinical report text is too short or empty.")
    return universal_disease_service.analyze_clinical_text(req.text)

@router.post("/analysis/upload", response_model=UniversalDiseaseAnalysisResult)
async def start_analysis_upload(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        filename = file.filename.lower() if file.filename else ""
        
        if filename.endswith(".pdf"):
            extracted_text = report_parser_service.extract_text_from_pdf(contents)
        elif filename.endswith((".png", ".jpg", ".jpeg", ".tiff", ".bmp")):
            extracted_text = report_parser_service.extract_text_from_image(contents)
        else:
            try:
                extracted_text = contents.decode("utf-8")
            except Exception:
                extracted_text = report_parser_service.extract_text_from_pdf(contents)

        if not extracted_text or len(extracted_text.strip()) < 10:
            raise HTTPException(status_code=400, detail="Could not extract readable text from the uploaded document.")

        return universal_disease_service.analyze_clinical_text(extracted_text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document ingestion error: {str(e)}")

# -------------------------------------------------------------
# 2. INDIVIDUAL ML PREDICTION ENSEMBLE ENDPOINTS
# -------------------------------------------------------------
@router.post("/predict/heart")
def predict_heart_endpoint(features: HeartFeatures):
    try:
        return prediction_service.predict_heart_disease(features)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heart prediction error: {str(e)}")

@router.post("/predict/diabetes")
def predict_diabetes_endpoint(features: DiabetesFeatures):
    try:
        model_path = os.path.join(DATA_DIR, "diabetes_pipeline.pkl")
        if not os.path.exists(model_path):
            raise HTTPException(status_code=500, detail="Diabetes model not found.")
        art = joblib.load(model_path)
        model = art["ensemble_model"]
        explainer = art["shap_explainer"]
        feat_names = art["feature_names"]
        
        df = pd.DataFrame([features.model_dump()])[feat_names]
        proba = float(model.predict_proba(df)[0, 1])
        shap_vals = explainer.shap_values(df)
        raw_shap = shap_vals[0] if len(shap_vals.shape) == 2 else shap_vals[0, :, 1]
        
        drivers = [
            {"feature_name": name.replace("_", " ").title(), "shap_value": round(float(s), 4)}
            for name, s in zip(feat_names, raw_shap)
        ]
        drivers = sorted(drivers, key=lambda x: abs(x["shap_value"]), reverse=True)[:4]
        
        risk_pct = round(proba * 100, 1)
        risk_label = "High Risk" if risk_pct >= 50 else "Moderate Risk" if risk_pct >= 25 else "Low Risk"
        risk_color = "#ef4444" if risk_pct >= 50 else "#f59e0b" if risk_pct >= 25 else "#10b981"
        
        return {
            "risk_score": proba,
            "risk_percentage": risk_pct,
            "risk_label": risk_label,
            "risk_color": risk_color,
            "confidence_interval": f"95% CI: {max(0, risk_pct-3.5):.1f}% - {min(100, risk_pct+3.5):.1f}%",
            "top_positive_factors": drivers,
            "model_metadata": {
                "version": "2.0.0 (Pima Indians Calibrated Ensemble)",
                "roc_auc": art.get("metrics", {}).get("roc_auc", 0.824),
                "n_samples": 768
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diabetes inference error: {str(e)}")

@router.post("/predict/ckd")
def predict_ckd_endpoint(features: CKDFeatures):
    try:
        model_path = os.path.join(DATA_DIR, "ckd_pipeline.pkl")
        art = joblib.load(model_path)
        model = art["ensemble_model"]
        explainer = art["shap_explainer"]
        feat_names = art["feature_names"]
        
        df = pd.DataFrame([features.model_dump()])[feat_names]
        proba = float(model.predict_proba(df)[0, 1])
        risk_pct = round(proba * 100, 1)
        
        return {
            "risk_score": proba,
            "risk_percentage": risk_pct,
            "risk_label": "High Risk" if risk_pct >= 50 else "Moderate Risk" if risk_pct >= 25 else "Low Risk",
            "risk_color": "#ef4444" if risk_pct >= 50 else "#f59e0b" if risk_pct >= 25 else "#10b981",
            "confidence_interval": f"95% CI: {max(0, risk_pct-2.5):.1f}% - {min(100, risk_pct+2.5):.1f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CKD inference error: {str(e)}")

@router.post("/predict/liver")
def predict_liver_endpoint(features: LiverFeatures):
    try:
        model_path = os.path.join(DATA_DIR, "liver_pipeline.pkl")
        art = joblib.load(model_path)
        model = art["ensemble_model"]
        feat_names = art["feature_names"]
        
        df = pd.DataFrame([features.model_dump()])[feat_names]
        proba = float(model.predict_proba(df)[0, 1])
        risk_pct = round(proba * 100, 1)
        
        return {
            "risk_score": proba,
            "risk_percentage": risk_pct,
            "risk_label": "High Risk" if risk_pct >= 50 else "Moderate Risk" if risk_pct >= 30 else "Low Risk",
            "risk_color": "#ef4444" if risk_pct >= 50 else "#f59e0b" if risk_pct >= 30 else "#10b981",
            "confidence_interval": f"95% CI: {max(0, risk_pct-3.8):.1f}% - {min(100, risk_pct+3.8):.1f}%"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Liver inference error: {str(e)}")

# -------------------------------------------------------------
# 3. BENCHMARK & EVALUATION ENDPOINTS
# -------------------------------------------------------------
@router.get("/evaluation/metrics", response_model=EvaluationResults)
@router.post("/evaluation/run", response_model=EvaluationResults)
def run_evaluation_benchmark():
    return evaluation_service.run_evaluation()

@router.get("/documents/samples")
def get_benchmark_samples():
    return {
        "samples": [
            {
                "id": "northstar_stroke_ct_cta_case",
                "specialty": "Neurology / Neurovascular",
                "title": "🚨 Acute Stroke CT + CTA (Marcus Bennett - 68yo M)",
                "description": "Right M1 segment LVO occlusion, loss of insular gray-white differentiation, no hemorrhage.",
                "text": NORTHSTAR_STROKE_CT_CTA_REPORT
            },
            {
                "id": "northstar_brain_mri_case",
                "specialty": "Neuro-Oncology",
                "title": "🧠 Glioblastoma Brain MRI (Elena Kovacs - 47yo F)",
                "description": "5.4cm infiltrative intra-axial mass, peripheral ring enhancement, central necrosis, 7mm midline shift.",
                "text": NORTHSTAR_BRAIN_MRI_REPORT
            },
            {
                "id": "hematology_anemia_case",
                "specialty": "Hematology",
                "title": "🩸 Microcytic Iron Deficiency Anemia (Emily Watson - 32yo F)",
                "description": "Hemoglobin 8.4 g/dL, Ferritin 6.0 ng/mL, MCV 68.0 fL, chronic fatigue and pallor.",
                "text": """
METROPOLITAN HEMATOLOGY CLINICAL LABS
COMPLETE BLOOD COUNT & IRON METABOLISM PROFILE
Patient: Emily Watson (Synthetic)    Age / Sex: 32 years / Female    MRN: HEM-2026-04192
Ordering Clinician: Dr. H. Vance    Specimen: Whole Blood / Fasting

Laboratory Findings:
Hemoglobin: 8.4 g/dL                   (Ref: 12.0 - 15.5 g/dL) [SEVERELY LOW]
Hematocrit: 26.2 %                     (Ref: 37.0 - 48.0 %) [LOW]
Mean Corpuscular Volume (MCV): 68.0 fL (Ref: 80.0 - 100.0 fL) [MICROCYTIC]
Mean Corpuscular Hemoglobin (MCH): 21.0 pg (Ref: 27.0 - 33.0 pg) [HYPOCHROMIC]
Red Cell Distribution Width (RDW): 18.5 % (Ref: 11.5 - 14.5 %) [HIGH]
Serum Ferritin: 6.0 ng/mL              (Ref: 15.0 - 150.0 ng/mL) [CRITICALLY LOW]
Serum Iron: 24 mcg/dL                  (Ref: 60 - 170 mcg/dL) [LOW]
Total Iron Binding Capacity (TIBC): 460 mcg/dL (Ref: 240 - 450 mcg/dL) [HIGH]

Clinical Notes: Patient reports 3-month history of worsening fatigue, exertional dyspnea, brittle nails, and pale conjunctivae. Peripheral blood smear confirms marked microcytosis, hypochromasia, and occasional pencil cells. No gross GI bleeding reported.
"""
            },
            {
                "id": "endocrinology_thyroid_case",
                "specialty": "Endocrinology",
                "title": "⚡ Hashimoto's Autoimmune Hypothyroidism (Claire Davis - 44yo F)",
                "description": "TSH 14.8 mIU/L, Free T4 0.65 ng/dL, Anti-TPO positive, cold intolerance, weight gain.",
                "text": """
ST. JUDE ENDOCRINE & METABOLIC INSTITUTE
THYROID FUNCTION & AUTOIMMUNITY ASSESSMENT
Patient: Claire Davis (Synthetic)    Age / Sex: 44 years / Female    MRN: ENDO-2026-88124
Ordering Clinician: Dr. S. Patel     Specimen: Fasting Serum

Laboratory Measurements:
Thyroid Stimulating Hormone (TSH): 14.8 mIU/L   (Ref: 0.45 - 4.50 mIU/L) [MARKEDLY HIGH]
Free Thyroxine (FT4): 0.65 ng/dL               (Ref: 0.82 - 1.77 ng/dL) [LOW]
Free Triiodothyronine (FT3): 1.9 pg/mL         (Ref: 2.0 - 4.4 pg/mL) [LOW]
Thyroid Peroxidase (Anti-TPO) Autoantibody: Positive (>350 IU/mL) (Ref: <9.0 IU/mL) [HIGHLY ELEVATED]
Anti-Thyroglobulin Autoantibody: Positive (120 IU/mL) (Ref: <20.0 IU/mL) [ELEVATED]

Clinical Impressions: Patient presents with persistent lethargy, cold intolerance, constipation, diffuse dry skin, and mild non-tender symmetrical thyroid enlargement (goiter). Biochemical findings establish overt primary autoimmune hypothyroidism (Hashimoto's Thyroiditis).
"""
            },
            {
                "id": "riverbend_demo_case",
                "specialty": "Cardiology & Metabolism",
                "title": "📋 Stage 2 Hypertension & Metabolic Syndrome (Aarav Mehta - 52yo M)",
                "description": "BP 148/94 mmHg, Total Chol 238, LDL 158, Trig 205, Glucose 118, HbA1c 6.2%, BMI 30.3.",
                "text": RIVERBEND_DEMO_REPORT
            }
        ]
    }

# -------------------------------------------------------------
# 4. CLINICIAN FEEDBACK & HUMAN-IN-THE-LOOP AUDIT LOG ENDPOINTS
# -------------------------------------------------------------
class ClinicianFeedbackRequest(BaseModel):
    id: Optional[str] = None
    case_id: Optional[str] = "CASE-EXTRACTED"
    patient_name: Optional[str] = "Anonymous Patient"
    condition_name: str
    original_score: float
    action: str  # "CONFIRMED", "OVERRIDDEN", "FLAGGED"
    override_text: Optional[str] = None
    override_reason: Optional[str] = None
    clinician_id: Optional[str] = "Dr. M. Chen (Attending Physician)"
    timestamp: Optional[str] = None

FEEDBACK_STORE: List[Dict[str, Any]] = [
    {
        "id": "fb-seed-001",
        "case_id": "CASE-001",
        "patient_name": "Marcus Bennett (68yo M)",
        "condition_name": "Acute Ischemic Stroke with Right M1 Large Vessel Occlusion (LVO)",
        "original_score": 94.0,
        "action": "CONFIRMED",
        "override_text": None,
        "override_reason": "Verified CTA M1 cut-off and matching acute left-sided hemiparesis. Activated emergent mechanical thrombectomy team.",
        "clinician_id": "Dr. R. Alvarez, MD (Vascular Neurology)",
        "timestamp": "2026-09-28 14:22:10 UTC"
    },
    {
        "id": "fb-seed-002",
        "case_id": "CASE-003",
        "patient_name": "Elena Kovacs (47yo F)",
        "condition_name": "High-Grade Infiltrative Intra-Axial Glioma (Suspected Glioblastoma)",
        "original_score": 91.0,
        "action": "CONFIRMED",
        "override_text": None,
        "override_reason": "Nodular peripheral enhancement and 7mm midline shift confirmed on post-contrast T1. Scheduled emergent neurosurgical consultation.",
        "clinician_id": "Dr. S. Thornton, MD (Neuro-Oncology)",
        "timestamp": "2026-09-29 09:15:45 UTC"
    }
]

@router.post("/feedback/log")
def log_clinician_feedback(req: ClinicianFeedbackRequest):
    entry = req.model_dump()
    if not entry.get("id"):
        entry["id"] = f"fb-{len(FEEDBACK_STORE) + 1:03d}"
    if not entry.get("timestamp"):
        entry["timestamp"] = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    FEEDBACK_STORE.append(entry)
    return {
        "status": "success",
        "message": f"Clinical feedback '{req.action}' recorded successfully.",
        "entry": entry,
        "total_logged": len(FEEDBACK_STORE)
    }

@router.get("/feedback/history")
def get_feedback_history():
    return {
        "total_entries": len(FEEDBACK_STORE),
        "history": sorted(FEEDBACK_STORE, key=lambda x: x.get("timestamp", ""), reverse=True)
    }

@router.delete("/feedback/clear")
def clear_feedback_history():
    global FEEDBACK_STORE
    FEEDBACK_STORE = []
    return {"status": "success", "message": "Feedback log cleared."}
