from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_document_routing_and_abstention():
    # 1. Test Brain MRI
    res_mri = client.post("/api/documents/classify", json={"text": "Brain MRI with IV gadolinium demonstrates T1/T2 infiltrative intra-axial lesion."})
    assert res_mri.status_code == 200
    assert res_mri.json()["document_type"] == "BRAIN_MRI_REPORT"
    assert res_mri.json()["is_supported"] is True

    # 2. Test Blood Lab Report
    res_lab = client.post("/api/documents/classify", json={"text": "Fasting blood glucose 118 mg/dL, HbA1c 6.2%, Total cholesterol 238 mg/dL."})
    assert res_lab.status_code == 200
    assert res_lab.json()["document_type"] == "LAB_REPORT"
    assert res_lab.json()["is_supported"] is True

    # 3. Test Unsupported Modality (ECG) -> Abstention
    res_ecg = client.post("/api/analysis/start", json={"text": "12-Lead Electrocardiogram tracing shows normal sinus rhythm with non-specific ST changes."})
    assert res_ecg.status_code == 200
    d_ecg = res_ecg.json()
    assert d_ecg["document_type"] == "ECG_REPORT"
    assert d_ecg["uncertainty_state"] == "OUT_OF_DISTRIBUTION"
    assert "Abstained" in d_ecg["overall_clinical_summary"]
    assert d_ecg["neuro_oncology"] is None
    assert d_ecg["extracted_biomarkers"] == []

    print("✅ Document routing and abstention test passed!")

if __name__ == "__main__":
    test_document_routing_and_abstention()
