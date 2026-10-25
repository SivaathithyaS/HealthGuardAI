import os
import sys
import unittest
import io
import json
from fastapi.testclient import TestClient

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.main import app


class TestImagingAPIEndpoints(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_01_get_models(self):
        res = self.client.get("/api/imaging/models")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("models", data)
        models = data["models"]
        names = [m["name"] for m in models]
        self.assertIn("ecg_cnn", names)
        self.assertIn("mri_cnn", names)

        ecg = next(m for m in models if m["name"] == "ecg_cnn")
        self.assertFalse(ecg["stub"])
        self.assertTrue(ecg["sha256_verified"])
        self.assertEqual(len(ecg["labels"]), 5)

        mri = next(m for m in models if m["name"] == "mri_cnn")
        self.assertFalse(mri["stub"])
        self.assertTrue(mri["sha256_verified"])
        self.assertEqual(len(mri["labels"]), 4)

    def test_02_get_samples(self):
        res = self.client.get("/api/imaging/samples")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("samples", data)
        self.assertTrue(len(data["samples"]) >= 5)

    def test_03_sample_inference_ecg(self):
        res = self.client.post("/api/imaging/ecg/sample/sample_ecg_stemi")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["modality"], "ecg")
        self.assertIn(data["status"], ["ok", "uncertain"])
        self.assertEqual(len(data["predictions"]), 5)
        self.assertIn("tier_mapping", data)
        self.assertIn("explanation", data)

    def test_04_sample_inference_mri(self):
        res = self.client.post("/api/imaging/mri/sample/sample_mri_glioma")
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["modality"], "mri")
        self.assertIn(data["status"], ["ok", "uncertain"])
        self.assertEqual(len(data["predictions"]), 4)
        self.assertIn("tier_mapping", data)
        self.assertIn("explanation", data)

    def test_05_ecg_upload_endpoint(self):
        # 500 sinusoidal float values simulating Lead II
        import numpy as np
        t = np.linspace(0, 5, 500)
        sig = (0.5 * np.sin(2 * np.pi * 1.2 * t)).tolist()
        payload = json.dumps({"samples": sig}).encode("utf-8")

        res = self.client.post(
            "/api/imaging/ecg",
            files={"file": ("test_lead2.json", io.BytesIO(payload), "application/json")}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["modality"], "ecg")
        self.assertEqual(len(data["predictions"]), 5)

    def test_06_mri_upload_endpoint(self):
        from PIL import Image, ImageDraw
        img = Image.new("L", (224, 224), 20)
        draw = ImageDraw.Draw(img)
        draw.ellipse((30, 30, 194, 194), fill=120)  # non-zero variance
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)

        res = self.client.post(
            "/api/imaging/mri",
            files={"file": ("test_mri.png", buf, "image/png")}
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data["modality"], "mri")
        self.assertIn(data["status"], ["ok", "uncertain"])
        self.assertEqual(len(data["predictions"]), 4)


if __name__ == "__main__":
    unittest.main()
