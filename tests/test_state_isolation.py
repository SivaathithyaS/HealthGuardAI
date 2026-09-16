from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.report_parser_service import (
    NORTHSTAR_STROKE_CT_CTA_REPORT, NORTHSTAR_BRAIN_MRI_REPORT, RIVERBEND_DEMO_REPORT
)

client = TestClient(app)

NORMAL_MRI_TEXT = """
NORTHSTAR UNIVERSITY MEDICAL CENTER
Department of Radiology • Neuroradiology Service
Patient: Sarah Jenkins    Age / Sex: 35 years / Female
Exam: MRI Brain with and without IV contrast
Findings: Normal gray-white differentiation. No focal mass lesion. No abnormal enhancement. No midline shift.
Impression: Normal non-contrast and contrast-enhanced brain MRI. No intracranial neoplasm.
"""

def test_full_regression_sequence_a_b_c_d_e():
    print("\n--- STEP A: GLIOBLASTOMA REPORT ---")
    res_a = client.post("/api/analysis/start", json={"text": NORTHSTAR_BRAIN_MRI_REPORT})
    assert res_a.status_code == 200
    d_a = res_a.json()
    assert d_a["document_type"] == "BRAIN_MRI_REPORT"
    assert d_a["analysis_pathway"] == "NEURO_ONCOLOGY"
    assert d_a["patient_context"]["name"] == "Elena Kovacs (Synthetic)"
    assert d_a["patient_context"]["age"] == 47
    assert d_a["neuro_oncology"]["model_score"] == 88.5
    assert d_a["stroke_assessment"] is None
    assert d_a["extracted_biomarkers"] == []
    id_a = d_a["analysis_id"]

    print("--- STEP B: STROKE CT + CTA REPORT ---")
    res_b = client.post("/api/analysis/start", json={"text": NORTHSTAR_STROKE_CT_CTA_REPORT})
    assert res_b.status_code == 200
    d_b = res_b.json()
    assert d_b["document_type"] == "CT_CTA_STROKE_REPORT"
    assert d_b["analysis_pathway"] == "NEUROVASCULAR_STROKE"
    assert d_b["patient_context"]["name"] == "Marcus Bennett (Synthetic)"
    assert d_b["patient_context"]["age"] == 68
    assert d_b["stroke_assessment"]["model_score"] == 94.0
    # Strict isolation assertions:
    assert d_b["neuro_oncology"] is None
    assert d_b["extracted_biomarkers"] == []
    assert d_b["disease_assessments"] == {}
    assert "Glioblastoma" not in str(d_b["stroke_assessment"])
    assert "Elena Kovacs" not in str(d_b)
    id_b = d_b["analysis_id"]
    assert id_a != id_b

    print("--- STEP C: NORMAL BRAIN MRI (HARD NEGATIVE) ---")
    res_c = client.post("/api/analysis/start", json={"text": NORMAL_MRI_TEXT})
    assert res_c.status_code == 200
    d_c = res_c.json()
    assert d_c["document_type"] == "BRAIN_MRI_REPORT"
    # Strict isolation assertions:
    assert d_c["patient_context"]["name"] != "Marcus Bennett"
    assert d_c["stroke_assessment"] is None
    assert d_c["extracted_biomarkers"] == []
    id_c = d_c["analysis_id"]
    assert id_b != id_c

    print("--- STEP D: METABOLIC LAB REPORT ---")
    res_d = client.post("/api/analysis/start", json={"text": RIVERBEND_DEMO_REPORT})
    assert res_d.status_code == 200
    d_d = res_d.json()
    assert d_d["document_type"] == "LAB_REPORT"
    assert d_d["analysis_pathway"] == "CARDIOMETABOLIC_MULTI_ORGAN"
    assert d_d["patient_context"]["name"] == "Aarav Mehta (Synthetic)"
    assert len(d_d["extracted_biomarkers"]) >= 10
    # Strict isolation assertions:
    assert d_d["neuro_oncology"] is None
    assert d_d["stroke_assessment"] is None
    assert "Stroke" not in str(d_d["clinical_followup_pathway"])
    assert "Elena" not in str(d_d)
    assert "Marcus" not in str(d_d)
    id_d = d_d["analysis_id"]
    assert id_c != id_d

    print("--- STEP E: STROKE REPORT AGAIN ---")
    res_e = client.post("/api/analysis/start", json={"text": NORTHSTAR_STROKE_CT_CTA_REPORT})
    assert res_e.status_code == 200
    d_e = res_e.json()
    assert d_e["document_type"] == "CT_CTA_STROKE_REPORT"
    assert d_e["patient_context"]["name"] == "Marcus Bennett (Synthetic)"
    assert d_e["stroke_assessment"]["model_score"] == 94.0
    # Strict isolation assertions:
    assert d_e["neuro_oncology"] is None
    assert d_e["extracted_biomarkers"] == []
    assert d_e["disease_assessments"] == {}
    assert "Cholesterol" not in str(d_e["clinical_followup_pathway"])
    assert "Aarav Mehta" not in str(d_e)
    id_e = d_e["analysis_id"]
    assert id_d != id_e

    print("\n✅ FULL REGRESSION SEQUENCE A -> B -> C -> D -> E PASSED: ZERO STATE CONTAMINATION VERIFIED!")

if __name__ == "__main__":
    test_full_regression_sequence_a_b_c_d_e()
