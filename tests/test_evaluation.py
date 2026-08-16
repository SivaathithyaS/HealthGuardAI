from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_evaluation_metrics():
    res = client.get("/api/evaluation/metrics")
    assert res.status_code == 200
    data = res.json()
    
    assert data["total_cases"] == 10
    assert data["accuracy"] >= 0.90
    assert data["sensitivity_recall"] >= 0.85
    assert data["specificity"] >= 0.85
    assert "confusion_matrix" in data
    assert data["confusion_matrix"]["true_positive"] > 0
    assert data["confusion_matrix"]["true_negative"] > 0
    assert data["brier_score"] < 0.25
    assert len(data["evaluated_cases"]) == 10

    print(f"✅ Evaluation benchmark test passed: Accuracy={data['accuracy']*100:.1f}%, Sensitivity={data['sensitivity_recall']*100:.1f}%, Specificity={data['specificity']*100:.1f}%, Brier={data['brier_score']:.4f}")

if __name__ == "__main__":
    test_evaluation_metrics()
