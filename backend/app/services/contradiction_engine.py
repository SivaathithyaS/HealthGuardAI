"""
HealthGuard AI - Generalized Clinical Contradiction & Inconsistency Engine
Structured multi-specialty rule engine that evaluates extracted clinical parameters,
symptom presentation, and imaging findings to identify diagnostic discordances
and anatomical / biochemical laterality contradictions.
"""

from typing import Dict, Any, List, Optional
import re
from pydantic import BaseModel

class ContradictionRuleResult(BaseModel):
    rule_id: str
    specialty: str
    severity: str  # "critical", "moderate", "advisory"
    conflict_title: str
    conflicting_elements: List[str]
    clinical_explanation: str
    reconciliation_guidance: str

class ContradictionRule:
    def __init__(
        self,
        rule_id: str,
        specialty: str,
        severity: str,
        condition_fn,
        title_fn,
        elements_fn,
        explanation_fn,
        guidance_fn
    ):
        self.id = rule_id
        self.specialty = specialty
        self.severity = severity
        self.condition_fn = condition_fn
        self.title_fn = title_fn
        self.elements_fn = elements_fn
        self.explanation_fn = explanation_fn
        self.guidance_fn = guidance_fn

    def evaluate(self, ctx: Dict[str, Any]) -> Optional[ContradictionRuleResult]:
        if self.condition_fn(ctx):
            return ContradictionRuleResult(
                rule_id=self.id,
                specialty=self.specialty,
                severity=self.severity,
                conflict_title=self.title_fn(ctx),
                conflicting_elements=self.elements_fn(ctx),
                clinical_explanation=self.explanation_fn(ctx),
                reconciliation_guidance=self.guidance_fn(ctx)
            )
        return None

# =========================================================================
# SPECIALTY RULE DEFINITIONS
# =========================================================================

def _stroke_laterality_condition(ctx: Dict[str, Any]) -> bool:
    t = ctx.get("text_lower", "")
    has_right_mca = any(k in t for k in ["right m1", "right middle cerebral", "right mca", "right hemisphere"])
    has_aphasia = any(k in t for k in [
        "expressive language", "expressive difficulty", "expressive aphasia", 
        "broca", "aphasia", "speech difficulty", "loss of speech"
    ])
    has_left_deficit = any(k in t for k in ["left hemiparesis", "left-sided", "left facial", "left arm", "left leg"])
    return has_right_mca and has_aphasia and has_left_deficit

def _cardiac_biomarker_condition(ctx: Dict[str, Any]) -> bool:
    t = ctx.get("text_lower", "")
    has_ischemic_chest_pain = any(k in t for k in [
        "crushing chest pain", "substernal chest pain", "radiating to jaw", 
        "radiating to left arm", "severe angina", "acute coronary"
    ])
    has_normal_troponin = any(k in t for k in [
        "troponin: normal", "troponin: <0.01", "troponin < 0.04", 
        "negative troponin", "troponin within normal limits", "troponin i: 0.0"
    ]) or ctx.get("troponin_normal", False)
    has_normal_ecg = any(k in t for k in [
        "ecg: normal", "normal sinus rhythm", "no st elevation", "ecg: unremarkable", "normal ecg"
    ])
    return has_ischemic_chest_pain and (has_normal_troponin and has_normal_ecg)

def _diabetes_glycemic_condition(ctx: Dict[str, Any]) -> bool:
    hba1c = ctx.get("hba1c")
    glucose = ctx.get("glucose")
    t = ctx.get("text_lower", "")

    # Look in text if numeric values not directly passed
    if hba1c is None:
        m_a1c = re.search(r"hba1c[:\s]+([0-9.]+)\s*%", t)
        if m_a1c:
            hba1c = float(m_a1c.group(1))

    if glucose is None:
        m_glu = re.search(r"(?:fasting\s+(?:blood\s+|plasma\s+)?glucose|glucose)[:\s]+([0-9.]+)", t)
        if m_glu:
            glucose = float(m_glu.group(1))

    if hba1c is not None and glucose is not None:
        # Severe chronic hyperglycemia (HbA1c >= 8.5%) but acute fasting glucose < 75 mg/dL (hypoglycemia)
        if hba1c >= 8.5 and glucose < 75:
            return True
        # Or acute marked hyperglycemia >= 200 mg/dL with normal HbA1c < 5.6%
        if glucose >= 200 and hba1c < 5.6:
            return True
    return False

def _microcytic_ferritin_condition(ctx: Dict[str, Any]) -> bool:
    mcv = ctx.get("mcv")
    ferritin = ctx.get("ferritin")
    hb = ctx.get("hemoglobin")
    t = ctx.get("text_lower", "")

    if mcv is None:
        m_mcv = re.search(r"mcv[:\s]+([0-9.]+)", t)
        if m_mcv:
            mcv = float(m_mcv.group(1))

    if ferritin is None:
        m_ferr = re.search(r"ferritin[:\s]+([0-9.]+)", t)
        if m_ferr:
            ferritin = float(m_ferr.group(1))

    if hb is None:
        m_hb = re.search(r"hemoglobin[:\s]+([0-9.]+)", t)
        if m_hb:
            hb = float(m_hb.group(1))

    if mcv is not None and ferritin is not None:
        # Microcytic anemia (MCV < 75 fL) but normal or high ferritin (> 150 ng/mL)
        if mcv < 75.0 and ferritin > 150.0 and (hb is not None and hb < 11.0):
            return True
    return False

# Rule registry
RULES: List[ContradictionRule] = [
    ContradictionRule(
        rule_id="stroke-laterality-mismatch",
        specialty="neurology",
        severity="critical",
        condition_fn=_stroke_laterality_condition,
        title_fn=lambda _: "⚠️ Clinical Inconsistency / Laterality Discordance Detected",
        elements_fn=lambda _: [
            "Right Middle Cerebral Artery (M1) Large Vessel Occlusion",
            "Left-sided facial, arm, and leg hemiparesis",
            "Expressive language difficulty (aphasia)"
        ],
        explanation_fn=lambda _: (
            "The Right MCA occlusion anatomically explains the left-sided hemiparesis. "
            "However, expressive language impairment (Broca's aphasia) is predominantly localized to the "
            "dominant cerebral hemisphere (typically left hemisphere in >95% of right-handed individuals and >70% of left-handed individuals)."
        ),
        guidance_fn=lambda _: (
            "Reconcile clinical laterality and language dominance (e.g. assess for non-dominant right-hemisphere language dominance, "
            "severe dysarthria mimicking cortical aphasia, or possible concurrent left-hemisphere / bilateral vascular territory involvement)."
        )
    ),
    ContradictionRule(
        rule_id="cardiac-chest-pain-normal-biomarkers",
        specialty="cardiology",
        severity="moderate",
        condition_fn=_cardiac_biomarker_condition,
        title_fn=lambda _: "⚠️ Diagnostic Discordance: High-Acuity Ischemic Symptoms vs. Normal Biomarkers & ECG",
        elements_fn=lambda _: [
            "Reported acute substernal crushing / radiating chest pain",
            "Initial Cardiac Troponin within reference range (<0.04 ng/mL)",
            "Normal sinus rhythm without ST-segment deviations on resting ECG"
        ],
        explanation_fn=lambda _: (
            "Severe anginal symptoms with negative baseline cardiac enzymes and normal ECG may indicate "
            "a hyperacute presentation within the 2-hour pre-troponin release window, unstable angina without necrosis, "
            "or non-atherosclerotic acute conditions (e.g. acute aortic syndrome, esophageal spasm, costochondritis)."
        ),
        guidance_fn=lambda _: (
            "Obtain serial high-sensitivity Troponin at 1-hour and 3-hour intervals per ESC accelerated diagnostic protocol. "
            "Perform bedside echocardiography to evaluate for regional wall motion abnormalities and maintain continuous 12-lead ECG monitoring."
        )
    ),
    ContradictionRule(
        rule_id="diabetes-glucose-hba1c-discordance",
        specialty="endocrinology",
        severity="moderate",
        condition_fn=_diabetes_glycemic_condition,
        title_fn=lambda _: "⚠️ Glycemic Discordance: Chronic HbA1c vs. Acute Fasting Plasma Glucose",
        elements_fn=lambda ctx: [
            f"Chronic Glycemic Index: HbA1c {ctx.get('hba1c', 'Abnormal')}%",
            f"Point-in-Time Plasma Glucose: {ctx.get('glucose', 'Disparate')} mg/dL"
        ],
        explanation_fn=lambda _: (
            "A wide divergence between HbA1c (reflecting 90-day mean glycemic control) and point-in-time fasting glucose "
            "suggests acute medication-induced hypoglycemia, rapid lifestyle shift, hemoglobinopathy affecting red cell turnover, "
            "or pre-analytical specimen handling latency."
        ),
        guidance_fn=lambda _: (
            "Review concurrent antihyperglycemic pharmacotherapy (insulin or secretagogues) for acute hypoglycemia risk. "
            "Re-check capillary blood glucose, obtain fructosamine or continuous glucose monitoring (CGM) if hemoglobin variant is suspected."
        )
    ),
    ContradictionRule(
        rule_id="hematology-microcytic-ferritin-discordance",
        specialty="hematology",
        severity="moderate",
        condition_fn=_microcytic_ferritin_condition,
        title_fn=lambda _: "⚠️ Hematologic Inconsistency: Severe Microcytosis with Preserved / High Ferritin",
        elements_fn=lambda ctx: [
            f"Depressed MCV ({ctx.get('mcv', 'Low')} fL) with Hemoglobin ({ctx.get('hemoglobin', 'Low')} g/dL)",
            f"Preserved / Elevated Ferritin ({ctx.get('ferritin', 'Elevated')} ng/mL)"
        ],
        explanation_fn=lambda _: (
            "Microcytic hypochromic anemia in the presence of normal or elevated ferritin contradicts uncomplicated absolute iron deficiency. "
            "This constellation strongly suggests Anemia of Chronic Disease / Inflammation (ferritin as an acute-phase reactant), "
            "Thalassemia minor trait, or sideroblastic anemia."
        ),
        guidance_fn=lambda _: (
            "Order systemic inflammatory markers (hs-CRP, ESR) and complete iron panel (Serum Iron, TIBC, Transferrin Saturation). "
            "If transferrin saturation is preserved (>20%), consider hemoglobin electrophoresis for beta-thalassemia screening."
        )
    )
]

class ContradictionEngine:
    def __init__(self, rules: List[ContradictionRule] = None):
        self.rules = rules or RULES

    def add_rule(self, rule: ContradictionRule):
        self.rules.append(rule)

    def evaluate(
        self,
        text: str,
        extracted_params: Optional[List[Dict[str, Any]]] = None,
        patient_data: Optional[Dict[str, Any]] = None
    ) -> Optional[ContradictionRuleResult]:
        t_lower = text.lower() if text else ""
        ctx: Dict[str, Any] = {
            "text": text,
            "text_lower": t_lower,
            "patient": patient_data or {}
        }

        # Populate context with extracted parameters
        if extracted_params:
            for p in extracted_params:
                name_low = str(p.get("name", "")).lower()
                val = p.get("value")
                num_val = p.get("numeric_value")
                if "glucose" in name_low and num_val is not None:
                    ctx["glucose"] = float(num_val)
                elif "hba1c" in name_low and num_val is not None:
                    ctx["hba1c"] = float(num_val)
                elif "mcv" in name_low and num_val is not None:
                    ctx["mcv"] = float(num_val)
                elif "ferritin" in name_low and num_val is not None:
                    ctx["ferritin"] = float(num_val)
                elif "hemoglobin" in name_low and num_val is not None:
                    ctx["hemoglobin"] = float(num_val)
                elif "troponin" in name_low:
                    if "normal" in str(val).lower() or "<" in str(val):
                        ctx["troponin_normal"] = True

        for rule in self.rules:
            result = rule.evaluate(ctx)
            if result is not None:
                return result

        return None

contradiction_engine = ContradictionEngine()
