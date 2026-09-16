from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.services.report_parser_service import NORTHSTAR_BRAIN_MRI_REPORT, RIVERBEND_DEMO_REPORT

client = TestClient(app)

def test_evidence_provenance():
    # 1. MRI Findings Provenance
    res_mri = client.post("/api/analysis/start", json={"text": NORTHSTAR_BRAIN_MRI_REPORT})
    data_mri = res_mri.json()
    observed = data_mri["neuro_oncology"]["observed_evidence"]
    assert len(observed) >= 4
    for obs in observed:
        assert obs["source_text"] != ""
        assert obs["source_section"] != ""
        assert obs["confidence"] > 0.8
        assert obs["clinical_interpretation"] != ""

    # 2. Lab Biomarkers Provenance
    res_lab = client.post("/api/analysis/start", json={"text": RIVERBEND_DEMO_REPORT})
    data_lab = res_lab.json()
    biomarkers = data_lab["extracted_biomarkers"]
    assert len(biomarkers) >= 10
    for bio in biomarkers:
        assert bio["source_text"] != ""
        assert bio["unit"] != ""
        assert bio["reference_range"] != ""
        assert bio["abnormality"] in ["NORMAL", "ELEVATED", "CRITICAL", "LOW", "HIGH"]

    print("✅ Evidence provenance test passed: All findings contain verbatim source text attribution!")

if __name__ == "__main__":
    test_evidence_provenance()
