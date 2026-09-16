from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_universal_multi_specialty_engine():
    # 1. TEST HEMATOLOGY: Iron Deficiency Anemia
    anemia_text = "Patient with severe fatigue. Hemoglobin: 8.4 g/dL, Ferritin: 6.0 ng/mL, MCV: 68.0 fL, TIBC: 460 mcg/dL."
    res_hem = client.post("/api/analysis/universal", json={"text": anemia_text})
    assert res_hem.status_code == 200
    d_hem = res_hem.json()
    assert d_hem["detected_specialty"] == "Hematology"
    assert "Iron Deficiency Anemia" in d_hem["primary_suspected_condition"]
    assert len(d_hem["decision_node_path"]) >= 3
    assert d_hem["decision_node_path"][0]["node_title"] == "Hemoglobin Red Blood Cell Threshold"

    # 2. TEST ENDOCRINOLOGY: Hashimoto's Hypothyroidism
    thyroid_text = "Thyroid lab results: TSH: 14.8 mIU/L, Free T4: 0.65 ng/dL, Anti-TPO autoantibody: Positive."
    res_endo = client.post("/api/analysis/universal", json={"text": thyroid_text})
    assert res_endo.status_code == 200
    d_endo = res_endo.json()
    assert d_endo["detected_specialty"] == "Endocrinology"
    assert "Hashimoto" in d_endo["primary_suspected_condition"]
    assert len(d_endo["decision_node_path"]) >= 2
    assert "TSH" in d_endo["decision_node_path"][0]["node_title"]

    # 3. TEST RHEUMATOLOGY: Systemic Lupus Erythematosus
    lupus_text = "Immunology panel: ANA positive 1:640, Anti-dsDNA positive 142 IU/mL, Anti-Smith positive, malar rash."
    res_lup = client.post("/api/analysis/universal", json={"text": lupus_text})
    assert res_lup.status_code == 200
    d_lup = res_lup.json()
    assert d_lup["detected_specialty"] == "Rheumatology"
    assert "Lupus" in d_lup["primary_suspected_condition"]
    assert len(d_lup["decision_node_path"]) >= 3

    # 4. TEST PULMONOLOGY: Bacterial Pneumonia
    pneumo_text = "Chest radiograph shows dense lobar consolidation with air bronchograms in right lower lobe. WBC 16,800/uL, fever 38.8C."
    res_pulm = client.post("/api/analysis/universal", json={"text": pneumo_text})
    assert res_pulm.status_code == 200
    d_pulm = res_pulm.json()
    assert d_pulm["detected_specialty"] == "Pulmonology"
    assert "Pneumonia" in d_pulm["primary_suspected_condition"]
    assert len(d_pulm["decision_node_path"]) >= 3

    print("✅ Universal Multi-Specialty Clinical Engine passed all tests with valid Decision Node Paths!")

if __name__ == "__main__":
    test_universal_multi_specialty_engine()
