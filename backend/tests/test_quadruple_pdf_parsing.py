import os
import unittest
from pypdf import PdfReader
from backend.app.services.universal_disease_service import universal_disease_service
from backend.app.services.multi_disease_service import multi_disease_service

class TestQuadrupleDiseaseReport(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pdf_path = "backend/tests/siva_quadruple_disease_report.pdf"
        assert os.path.exists(cls.pdf_path), f"File not found: {cls.pdf_path}"
        reader = PdfReader(cls.pdf_path)
        cls.extracted_text = "\n".join(page.extract_text() or "" for page in reader.pages)
        print(f"\nExtracted {len(cls.extracted_text)} characters from {cls.pdf_path}")

    def test_universal_disease_service_quadruple_branch(self):
        result = universal_disease_service.analyze_clinical_text(self.extracted_text)
        
        # Check routing
        self.assertIn("Multisystem Cardiorenal-Metabolic & Hepatic Syndrome", result.primary_suspected_condition)
        self.assertIn("Multidisciplinary Internal Medicine", result.detected_specialty)
        self.assertEqual(result.ai_evidence_score, 96.0)
        self.assertEqual(result.patient_context.name, "Sivaathithya")
        self.assertEqual(result.patient_context.age, 46)
        
        # Check that parameters span all 4 axes
        param_names = [p.name for p in result.extracted_parameters]
        self.assertTrue(any("blood pressure" in p.lower() or "cholesterol" in p.lower() for p in param_names), "Heart parameters missing")
        self.assertTrue(any("glucose" in p.lower() or "hba1c" in p.lower() for p in param_names), "Diabetes parameters missing")
        self.assertTrue(any("creatinine" in p.lower() or "egfr" in p.lower() or "uacr" in p.lower() for p in param_names), "Kidney parameters missing")
        self.assertTrue(any("alt" in p.lower() or "bilirubin" in p.lower() or "alp" in p.lower() for p in param_names), "Liver parameters missing")

        # Check rubric breakdown & plain language summary
        self.assertIsNotNone(result.rubric_breakdown)
        self.assertGreater(len(result.rubric_breakdown.criteria), 0)
        self.assertIsNotNone(result.plain_language_summary)
        self.assertIn("4-Organ", result.plain_language_summary.urgency_tier)
        print("Universal CDS Quadruple Result Verified Successfully!")

    def test_multi_disease_service_4_disease_screening(self):
        result = multi_disease_service.run_analysis(self.extracted_text)
        
        self.assertIn("heart", result.disease_assessments)
        self.assertIn("diabetes", result.disease_assessments)
        self.assertIn("ckd", result.disease_assessments)
        self.assertIn("liver", result.disease_assessments)
        
        ckd = result.disease_assessments["ckd"]
        liver = result.disease_assessments["liver"]
        diabetes = result.disease_assessments["diabetes"]
        heart = result.disease_assessments["heart"]
        
        print(f"Multi-Disease Screening Results:")
        print(f"  CKD: {ckd['model_score']:.1f}% ({ckd['risk_label']})")
        print(f"  Liver: {liver['model_score']:.1f}% ({liver['risk_label']})")
        print(f"  Diabetes: {diabetes['model_score']:.1f}% ({diabetes['risk_label']})")
        print(f"  Heart: {heart['model_score']:.1f}% ({heart['risk_label']})")
        
        self.assertGreaterEqual(ckd["model_score"], 70.0, "CKD risk should be high")
        self.assertGreaterEqual(liver["model_score"], 70.0, "Liver risk should be high")
        self.assertGreaterEqual(diabetes["model_score"], 50.0, "Diabetes risk should be significant")
        self.assertGreaterEqual(len(result.clinical_followup_pathway), 3, "Should generate comprehensive follow-ups")
        print("Multi-Disease 4-Axis Screening Verified Successfully!")

if __name__ == "__main__":
    unittest.main()
