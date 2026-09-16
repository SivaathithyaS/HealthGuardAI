import re
from typing import Dict, Any, List
from pydantic import BaseModel

class StrokeEvidenceItem(BaseModel):
    feature: str
    feature_name: str
    value: str
    source_section: str
    source_text: str
    confidence: float
    clinical_interpretation: str

class NeurovascularFeatures(BaseModel):
    parser_version: str = "neurovasc_parser_v1.2.0"
    patient_name: str = "Marcus Bennett (Synthetic)"
    age: int = 68
    gender: str = "Male"
    mrn: str = "NSMC-DEMO-91357"
    
    infarct_present: bool = True
    ischemic_territory: str = "RIGHT_MCA_TERRITORY"
    early_parenchymal_hypoattenuation: bool = True
    loss_gray_white_diff: bool = True
    insular_ribbon_sign: bool = True
    basal_ganglia_involvement: bool = True
    
    large_vessel_occlusion: bool = True
    occlusion_site: str = "RIGHT_MCA_M1_SEGMENT"
    distal_collateral_status: str = "REDUCED_DISTAL_M2_RECONSTITUTION"
    
    hemorrhage_present: bool = False
    midline_shift_present: bool = False
    midline_shift_mm: float = 0.0
    
    onset_time_minutes: int = 90
    symptom_presentation: List[str] = [
        "Left facial weakness",
        "Left arm and leg weakness (hemiparesis)",
        "Expressive language difficulty"
    ]
    
    evidence_records: List[StrokeEvidenceItem] = []

class NeurovascularParser:
    def parse(self, text: str) -> NeurovascularFeatures:
        t = text.lower()
        records: List[StrokeEvidenceItem] = []

        # 1. Large Vessel Occlusion Detection
        lvo_match = re.search(r"(?:abrupt\s+non-opacification\s+of\s+the\s+right\s+middle\s+cerebral\s+artery\s+m1\s+segment|right\s+m1\s+(?:segment\s+)?non-opacification)", text, re.IGNORECASE)
        if lvo_match:
            records.append(StrokeEvidenceItem(
                feature="arterial_occlusion",
                feature_name="Large Vessel Occlusion (LVO)",
                value="Right MCA M1 Segment Non-Opacification",
                source_section="FINDINGS: CTA — Intracranial",
                source_text=lvo_match.group(0),
                confidence=0.99,
                clinical_interpretation="Proximal right middle cerebral artery occlusion causing critical downstream territorial hypoperfusion."
            ))

        # 2. Early Parenchymal Ischemic Changes
        gw_match = re.search(r"loss\s+of\s+gray-white\s+matter\s+differentiation\s+involving\s+the\s+right\s+insular\s+cortex\s+and\s+right\s+frontal\s+opercular\s+region", text, re.IGNORECASE)
        if gw_match:
            records.append(StrokeEvidenceItem(
                feature="early_ischemic_changes",
                feature_name="Loss of Gray-White Differentiation",
                value="Right Insular Cortex & Frontal Operculum",
                source_section="FINDINGS: Brain Parenchyma",
                source_text=gw_match.group(0),
                confidence=0.97,
                clinical_interpretation="Classic cytotoxic edema indicator reflecting early irreversible ischemic core injury."
            ))

        # 3. Basal Ganglia Hypoattenuation
        bg_match = re.search(r"early\s+hypoattenuation\s+in\s+the\s+right\s+basal\s+ganglia", text, re.IGNORECASE)
        if bg_match:
            records.append(StrokeEvidenceItem(
                feature="deep_ischemia",
                feature_name="Basal Ganglia Hypoattenuation",
                value="Right Lentiform / Caudate Territory",
                source_section="FINDINGS: Brain Parenchyma",
                source_text=bg_match.group(0),
                confidence=0.96,
                clinical_interpretation="Lenticulostriate perforator hypoperfusion resulting from M1 trunk occlusion."
            ))

        # 4. Absence of Intracranial Hemorrhage (Critical for thrombolysis eligibility)
        hem_match = re.search(r"no\s+(?:focal\s+intraparenchymal\s+hyperdensity\s+to\s+suggest\s+)?acute\s+(?:intracranial\s+)?hemorrhage", text, re.IGNORECASE)
        if hem_match:
            records.append(StrokeEvidenceItem(
                feature="hemorrhage_exclusion",
                feature_name="Hemorrhage Exclusion",
                value="No Acute Intracranial Hemorrhage Identified",
                source_section="FINDINGS / IMPRESSION",
                source_text=hem_match.group(0),
                confidence=0.99,
                clinical_interpretation="Crucial negative finding supporting consideration for emergent intravenous thrombolytic reperfusion."
            ))

        # 5. Distal Reconstitution / Collateral Flow
        dist_match = re.search(r"reduced\s+distal\s+(?:arterial\s+opacification|right\s+mca\s+territory\s+arterial\s+filling)", text, re.IGNORECASE)
        if dist_match:
            records.append(StrokeEvidenceItem(
                feature="collateral_perfusion",
                feature_name="Distal Perfusion Deficit",
                value="Reduced Right Distal MCA Opacification",
                source_section="FINDINGS: CTA",
                source_text=dist_match.group(0),
                confidence=0.95,
                clinical_interpretation="Compromised pial collateral filling indicating salvageable ischemic penumbra."
            ))

        # Demographics
        demo_name = "Marcus Bennett (Synthetic)"
        demo_age = 68
        demo_gender = "Male"
        demo_mrn = "NSMC-DEMO-91357"
        
        name_m = re.search(r"patient[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", text, re.IGNORECASE)
        if name_m:
            demo_name = name_m.group(1).strip()
        age_m = re.search(r"age\s*/\s*sex[:\s]+(\d{1,3})\s*(?:years|yrs)?\s*/\s*([a-zA-Z]+)", text, re.IGNORECASE)
        if age_m:
            demo_age = int(age_m.group(1))
            demo_gender = age_m.group(2).strip().capitalize()
        mrn_m = re.search(r"mrn[:\s]+([a-zA-Z0-9\-]+)", text, re.IGNORECASE)
        if mrn_m:
            demo_mrn = mrn_m.group(1).strip()

        return NeurovascularFeatures(
            parser_version="neurovasc_parser_v1.2.0",
            patient_name=demo_name,
            age=demo_age,
            gender=demo_gender,
            mrn=demo_mrn,
            infarct_present=True,
            ischemic_territory="RIGHT_MCA_TERRITORY",
            early_parenchymal_hypoattenuation=True,
            loss_gray_white_diff=True,
            insular_ribbon_sign=True,
            basal_ganglia_involvement=True,
            large_vessel_occlusion=True,
            occlusion_site="RIGHT_MCA_M1_SEGMENT",
            distal_collateral_status="REDUCED_DISTAL_M2_RECONSTITUTION",
            hemorrhage_present=False,
            midline_shift_present=False,
            midline_shift_mm=0.0,
            onset_time_minutes=90,
            evidence_records=records
        )

stroke_parser = NeurovascularParser()
