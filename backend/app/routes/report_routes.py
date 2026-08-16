from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
from backend.app.schemas.multi_disease import ReportAnalysisResponse
from backend.app.services.report_parser_service import (
    report_parser_service, SAMPLE_LAB_REPORTS, RIVERBEND_DEMO_REPORT, NORTHSTAR_BRAIN_MRI_REPORT
)
from backend.app.services.multi_disease_service import multi_disease_service

router = APIRouter(prefix="/report", tags=["Medical Report Analysis"])

class TextReportRequest(BaseModel):
    text: str

@router.post("/analyze-file", response_model=ReportAnalysisResponse)
async def analyze_report_file(file: UploadFile = File(...)):
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
            raise HTTPException(status_code=400, detail="Could not extract readable clinical text from the uploaded document.")

        return multi_disease_service.analyze_report(extracted_text)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Report parsing error: {str(e)}")

@router.post("/analyze-text", response_model=ReportAnalysisResponse)
def analyze_report_text(req: TextReportRequest):
    if not req.text or len(req.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Report text is too short or empty.")
    return multi_disease_service.analyze_report(req.text)

@router.get("/samples")
def get_sample_reports():
    return {
        "samples": [
            {
                "id": "northstar_brain_mri_case",
                "title": "🧠 Northstar Brain MRI (Elena Kovacs - 47yo Glioblastoma Case)",
                "description": "5.4cm right fronto-insular mass, ring enhancement, central necrosis, 7mm midline shift, facial twitching.",
                "text": NORTHSTAR_BRAIN_MRI_REPORT
            },
            {
                "id": "riverbend_demo_case",
                "title": "📋 Riverbend Comprehensive Report (Aarav Mehta - 52yo Male)",
                "description": "Stage 2 BP 148/94, Total Chol 238, LDL 158, Trig 205, Glucose 118, HbA1c 6.2%, BMI 30.3 kg/m².",
                "text": RIVERBEND_DEMO_REPORT
            },
            {
                "id": "metabolic_renal_case",
                "title": "🚨 Severe Metabolic & Early Renal Case (High Glucose 168, Chol 248, Creatinine 1.85)",
                "description": "Patient with diabetic nephropathy indicators and hypertensive strain.",
                "text": SAMPLE_LAB_REPORTS["metabolic_renal_case"]
            },
            {
                "id": "hepatic_fatty_liver_case",
                "title": "⚠️ Hepatic Steatosis / Fatty Liver Profile (Elevated SGPT 88, SGOT 76, Bilirubin 2.1)",
                "description": "Elevated liver transaminases and metabolic risk markers.",
                "text": SAMPLE_LAB_REPORTS["hepatic_fatty_liver_case"]
            },
            {
                "id": "healthy_checkup_case",
                "title": "✅ Optimal Annual Checkup (Normal Biomarkers Across All Panels)",
                "description": "Healthy patient with all metrics within optimal reference ranges.",
                "text": SAMPLE_LAB_REPORTS["healthy_checkup_case"]
            }
        ]
    }
