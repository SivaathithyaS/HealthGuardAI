import os
import unittest
import pypdf
from backend.app.services.universal_disease_service import universal_disease_service

class TestCKDLiverAnalysis(unittest.TestCase):
    def test_siva_kidney_report(self):
        pdf_path = "backend/tests/siva_kidney_report.pdf"
        self.assertTrue(os.path.exists(pdf_path), "Test report must exist")
        reader = pypdf.PdfReader(pdf_path)
        text = "".join([p.extract_text() for p in reader.pages])
        
        res = universal_disease_service.analyze_clinical_text(text)
        self.assertEqual(res.patient_context.name, "Sivaathithya")
        self.assertEqual(res.detected_specialty, "Nephrology & Renal Medicine")
        self.assertIn("Chronic Kidney Disease", res.primary_suspected_condition)
        self.assertIn("G3b", res.primary_suspected_condition)
        self.assertIn("Renal Glomeruli", res.affected_organ_systems)
        self.assertGreaterEqual(res.ai_evidence_score, 85.0)

    def test_ckd_probable_report(self):
        pdf_path = "backend/tests/ckd_probable_sivaathithya.pdf"
        self.assertTrue(os.path.exists(pdf_path), "Test report must exist")
        reader = pypdf.PdfReader(pdf_path)
        text = "".join([p.extract_text() for p in reader.pages])
        
        res = universal_disease_service.analyze_clinical_text(text)
        self.assertEqual(res.patient_context.name, "Sivaathithya")
        self.assertEqual(res.detected_specialty, "Nephrology & Renal Medicine")
        self.assertIn("Chronic Kidney Disease", res.primary_suspected_condition)
        self.assertIn("G3a", res.primary_suspected_condition)

    def test_dual_organ_kidney_liver_report(self):
        pdf_path = "backend/tests/siva_kidney_liver_report.pdf"
        self.assertTrue(os.path.exists(pdf_path), "Test report must exist")
        reader = pypdf.PdfReader(pdf_path)
        text = "".join([p.extract_text() for p in reader.pages])
        
        res = universal_disease_service.analyze_clinical_text(text)
        self.assertEqual(res.patient_context.name, "Sivaathithya")
        self.assertIn("Nephrology & Hepatology", res.detected_specialty)
        self.assertIn("Chronic Kidney Disease", res.primary_suspected_condition)
        self.assertIn("Hepatic Dysfunction", res.primary_suspected_condition)
        self.assertIn("Renal Glomeruli & Tubules", res.affected_organ_systems)
        self.assertIn("Hepatic Parenchyma (Hepatocytes)", res.affected_organ_systems)

if __name__ == "__main__":
    unittest.main()
