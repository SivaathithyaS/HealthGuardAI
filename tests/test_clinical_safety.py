import unittest
from backend.app.services.universal_disease_service import universal_disease_service
from backend.app.services.report_parser_service import (
    RIVERBEND_DEMO_REPORT, NORTHSTAR_BRAIN_MRI_REPORT, NORTHSTAR_STROKE_CT_CTA_REPORT
)

class TestClinicalSafety(unittest.TestCase):
    def test_sample_1_cardiometabolic_safety(self):
        res = universal_disease_service.analyze_clinical_text(RIVERBEND_DEMO_REPORT)
        
        # 1. Honest AI Evidence Score
        self.assertGreater(res.ai_evidence_score, 0)
        self.assertIn("not a calibrated probability", res.evidence_score_disclaimer)
        
        # 2. Patient Demographics & BMI
        self.assertEqual(res.patient_context.name, "Aarav Mehta (Synthetic)")
        self.assertEqual(res.patient_context.age, 52)
        self.assertIn("30.3", res.patient_context.calculated_bmi or "")
        
        # 3. BP Confirmation Qualification
        self.assertIn("confirmation", res.diagnostic_certainty_level.lower())
        
        # 4. 3-Tier Finding-to-Diagnosis Hierarchy
        self.assertGreaterEqual(len(res.three_tier_evidence), 3)
        tier_labels = [t.tier_label for t in res.three_tier_evidence]
        self.assertTrue(all("Observed" in l for l in tier_labels))
        
        # 5. Modifiable Risk Factors Table
        self.assertGreaterEqual(len(res.modifiable_risk_factors), 4)
        rf_names = [rf.risk_factor for rf in res.modifiable_risk_factors]
        self.assertTrue(any("Blood Pressure" in n for n in rf_names))
        self.assertTrue(any("LDL" in n for n in rf_names))
        self.assertTrue(any("Body Mass Index" in n for n in rf_names))
        
        # 6. Long-Term Prevention vs Emergency Actions
        self.assertGreaterEqual(len(res.long_term_prevention), 2)
        self.assertEqual(len(res.emergency_actions), 0)

    def test_sample_2_brain_tumor_safety(self):
        res = universal_disease_service.analyze_clinical_text(NORTHSTAR_BRAIN_MRI_REPORT)
        
        # 1. Non-Definitive Framing
        self.assertTrue("Suspected" in res.primary_suspected_condition or "neoplasm" in res.primary_suspected_condition.lower())
        self.assertTrue("tissue" in res.required_confirmation.lower() or "histopathol" in res.required_confirmation.lower())
        
        # 2. 3-Tier Hierarchy
        self.assertGreaterEqual(len(res.three_tier_evidence), 3)
        self.assertTrue("Glioblastoma" in res.three_tier_evidence[0].clinical_consideration or "Glioma" in res.three_tier_evidence[0].clinical_consideration)
        
        # 3. Emergency Actions vs Long-Term
        self.assertGreaterEqual(len(res.emergency_actions), 1)
        self.assertIn("Neurosurgical", res.emergency_actions[0].title)

    def test_sample_3_stroke_conflicting_evidence_detection(self):
        res = universal_disease_service.analyze_clinical_text(NORTHSTAR_STROKE_CT_CTA_REPORT)
        
        # 1. Conflicting Evidence Alert Detected
        self.assertTrue(res.conflicting_evidence_alert.conflict_detected)
        self.assertTrue("Inconsistency" in res.conflicting_evidence_alert.conflict_title or "Discordance" in res.conflicting_evidence_alert.conflict_title)
        self.assertIn("dominant hemisphere", res.conflicting_evidence_alert.clinical_explanation.lower())
        
        # 2. Emergency Actions
        self.assertGreaterEqual(len(res.emergency_actions), 1)
        self.assertIn("Thrombectomy", res.emergency_actions[0].title)

if __name__ == "__main__":
    unittest.main()
