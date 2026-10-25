import os
import sys
import unittest
import numpy as np

# Ensure root directory is on python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from backend.app.services.cnn_service import ImagingCNNService


class TestCNNIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = ImagingCNNService()

    def test_01_bundle_registration(self):
        models = self.service.list_models()
        model_names = [m.name for m in models]
        self.assertIn("ecg_cnn", model_names, "ecg_cnn bundle not found")
        self.assertIn("mri_cnn", model_names, "mri_cnn bundle not found")

        ecg_meta = next(m for m in models if m.name == "ecg_cnn")
        mri_meta = next(m for m in models if m.name == "mri_cnn")

        self.assertFalse(ecg_meta.stub, "ECG model should not be in stub mode")
        self.assertTrue(ecg_meta.sha256_verified, "ECG SHA256 checksum must match")
        self.assertEqual(len(ecg_meta.labels), 5, "ECG should have 5 PTB-XL labels")

        self.assertFalse(mri_meta.stub, "MRI model should not be in stub mode")
        self.assertTrue(mri_meta.sha256_verified, "MRI SHA256 checksum must match")
        self.assertEqual(len(mri_meta.labels), 4, "MRI should have 4 brain tumor labels")

    def test_02_ecg_inference_pipeline(self):
        # Run normal ECG sample
        res_normal = self.service.analyze_sample("ecg", "sample_ecg_normal")
        self.assertEqual(res_normal.modality, "ecg")
        self.assertIn(res_normal.status, ["ok", "uncertain"])
        self.assertEqual(len(res_normal.predictions), 5)
        self.assertTrue(all(0.0 <= p.probability <= 1.0 for p in res_normal.predictions))
        self.assertIsNotNone(res_normal.tier_mapping)
        self.assertTrue(len(res_normal.tier_mapping.level1_observed) > 0)
        self.assertIsNotNone(res_normal.explanation)
        self.assertIsNotNone(res_normal.explanation.signal_preview)

        # Run corrupt sample (gate rejection test)
        res_corrupt = self.service.analyze_sample("ecg", "sample_ecg_corrupt")
        self.assertEqual(res_corrupt.status, "rejected_input")
        self.assertEqual(res_corrupt.top_label, "REJECTED_INPUT")

    def test_03_mri_inference_pipeline(self):
        # Run glioma sample
        res_glioma = self.service.analyze_sample("mri", "sample_mri_glioma")
        self.assertEqual(res_glioma.modality, "mri")
        self.assertIn(res_glioma.status, ["ok", "uncertain"])
        self.assertEqual(len(res_glioma.predictions), 4)
        self.assertTrue(all(0.0 <= p.probability <= 1.0 for p in res_glioma.predictions))
        self.assertIsNotNone(res_glioma.explanation)
        self.assertIsNotNone(res_glioma.explanation.heatmap_png_base64)
        self.assertIsNotNone(res_glioma.tier_mapping)

        # Run corrupt sample
        res_corrupt = self.service.analyze_sample("mri", "sample_mri_corrupt")
        self.assertEqual(res_corrupt.status, "rejected_input")
        self.assertEqual(res_corrupt.top_label, "REJECTED_INPUT")


if __name__ == "__main__":
    unittest.main()
