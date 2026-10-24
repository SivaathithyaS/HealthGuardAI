import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import io
import json
from fastapi.testclient import TestClient
from PIL import Image

from backend.app.main import app

client = TestClient(app)

def test_imaging_models_and_samples_registry():
    # 1. Test Models Endpoint
    res_models = client.get("/api/imaging/models")
    assert res_models.status_code == 200
    models_data = res_models.json()
    assert "models" in models_data
    models = models_data["models"]
    assert len(models) >= 2

    ecg_m = next((m for m in models if m["modality"] == "ecg"), None)
    mri_m = next((m for m in models if m["modality"] == "mri"), None)

    assert ecg_m is not None
    assert ecg_m["stub"] is True
    assert "stub" in ecg_m["model_version"].lower()
    assert ecg_m["sha256_verified"] is True
    assert ecg_m["threshold"] == 0.6

    assert mri_m is not None
    assert mri_m["stub"] is True
    assert "stub" in mri_m["model_version"].lower()
    assert mri_m["sha256_verified"] is True

    # 2. Test Samples Endpoint
    res_samples = client.get("/api/imaging/samples")
    assert res_samples.status_code == 200
    samples_data = res_samples.json()
    assert "samples" in samples_data
    samples = samples_data["samples"]
    assert len(samples) >= 6

    ecg_samples = [s for s in samples if s["modality"] == "ecg"]
    mri_samples = [s for s in samples if s["modality"] == "mri"]
    assert len(ecg_samples) >= 3
    assert len(mri_samples) >= 3

def test_ecg_sample_cases():
    # A. OK Case
    res_ok = client.post("/api/imaging/ecg/sample/sample_ecg_stemi")
    assert res_ok.status_code == 200
    data_ok = res_ok.json()
    assert data_ok["status"] == "ok"
    assert data_ok["modality"] == "ecg"
    assert data_ok["uncertainty"]["max_prob"] >= data_ok["uncertainty"]["threshold"]
    assert data_ok["explanation"]["signal_preview"] is not None
    assert len(data_ok["explanation"]["signal_preview"]["samples"]) > 0
    assert data_ok["explanation"]["saliency"] is not None
    assert "ST Elevation" in data_ok["top_label"]

    # B. Uncertain Case (max_prob < threshold)
    res_unc = client.post("/api/imaging/ecg/sample/sample_ecg_uncertain")
    assert res_unc.status_code == 200
    data_unc = res_unc.json()
    assert data_unc["status"] == "uncertain"
    assert data_unc["uncertainty"]["max_prob"] < data_unc["uncertainty"]["threshold"]
    assert data_unc["reason"] is not None
    assert "below clinical confidence threshold" in data_unc["reason"]

    # C. Rejected Case
    res_rej = client.post("/api/imaging/ecg/sample/sample_ecg_corrupt")
    assert res_rej.status_code == 200
    data_rej = res_rej.json()
    assert data_rej["status"] == "rejected_input"
    assert data_rej["reason"] is not None
    assert "checksum" in data_rej["reason"].lower() or "corrupt" in data_rej["reason"].lower()

def test_mri_sample_cases():
    # A. OK Case
    res_ok = client.post("/api/imaging/mri/sample/sample_mri_glioma")
    assert res_ok.status_code == 200
    data_ok = res_ok.json()
    assert data_ok["status"] == "ok"
    assert data_ok["modality"] == "mri"
    assert data_ok["uncertainty"]["max_prob"] >= data_ok["uncertainty"]["threshold"]
    assert data_ok["explanation"]["heatmap_png_base64"] is not None
    assert len(data_ok["explanation"]["heatmap_png_base64"]) > 100
    assert "Glioma" in data_ok["top_label"]

    # B. Uncertain Case
    res_unc = client.post("/api/imaging/mri/sample/sample_mri_uncertain")
    assert res_unc.status_code == 200
    data_unc = res_unc.json()
    assert data_unc["status"] == "uncertain"
    assert data_unc["uncertainty"]["max_prob"] < data_unc["uncertainty"]["threshold"]
    assert data_unc["reason"] is not None

    # C. Rejected Case
    res_rej = client.post("/api/imaging/mri/sample/sample_mri_corrupt")
    assert res_rej.status_code == 200
    data_rej = res_rej.json()
    assert data_rej["status"] == "rejected_input"
    assert data_rej["reason"] is not None

def test_file_upload_endpoints():
    # 1. Test Valid ECG Upload
    sample_signal = [0.12, 0.15, -0.2, 1.4, -0.3, 0.1, 0.2] * 40
    ecg_bytes = json.dumps({"samples": sample_signal}).encode("utf-8")
    files_ecg = {"file": ("patient_strip.json", io.BytesIO(ecg_bytes), "application/json")}
    res_ecg = client.post("/api/imaging/ecg", files=files_ecg)
    assert res_ecg.status_code == 200
    d_ecg = res_ecg.json()
    assert d_ecg["status"] in ["ok", "uncertain"]
    assert d_ecg["modality"] == "ecg"

    # 2. Test Rejected ECG Upload (empty)
    files_empty = {"file": ("empty.dat", io.BytesIO(b""), "application/octet-stream")}
    res_empty = client.post("/api/imaging/ecg", files=files_empty)
    assert res_empty.status_code == 200
    d_empty = res_empty.json()
    assert d_empty["status"] == "rejected_input"

    # 3. Test Valid MRI Upload
    from PIL import ImageDraw
    img = Image.new("L", (100, 100), 20)
    draw = ImageDraw.Draw(img)
    draw.ellipse((15, 15, 85, 85), fill=120, outline=200)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    files_mri = {"file": ("slice_t1.png", buf, "image/png")}
    res_mri = client.post("/api/imaging/mri", files=files_mri)
    assert res_mri.status_code == 200
    d_mri = res_mri.json()
    assert d_mri["status"] in ["ok", "uncertain"]
    assert d_mri["explanation"]["heatmap_png_base64"] is not None

    # 4. Test Rejected MRI Upload (not an image)
    bad_bytes = b"NOT_A_VALID_IMAGE_JUST_RANDOM_TEXT"
    files_bad = {"file": ("corrupt.png", io.BytesIO(bad_bytes), "image/png")}
    res_bad = client.post("/api/imaging/mri", files=files_bad)
    assert res_bad.status_code == 200
    d_bad = res_bad.json()
    assert d_bad["status"] == "rejected_input"

if __name__ == "__main__":
    test_imaging_models_and_samples_registry()
    test_ecg_sample_cases()
    test_mri_sample_cases()
    test_file_upload_endpoints()
    print("All imaging tests passed!")
