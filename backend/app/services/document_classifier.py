import re
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel

class ClassificationResult(BaseModel):
    document_type: str
    document_type_display: str
    routing_target: str
    confidence: float
    evidence_terms: List[str]
    is_supported: bool
    unsupported_message: str = ""

DOCUMENT_TAXONOMY = {
    "CT_CTA_STROKE_REPORT": {
        "display": "Head Noncontrast CT + CT Angiography (Head & Neck)",
        "routing": "NEUROVASCULAR_STROKE",
        "keywords": [
            "ct angiography", "cta", "noncontrast ct head", "noncontrast axial ct", 
            "ct of the head was obtained", "m1 segment", "m2 branches", 
            "middle cerebral artery", "arterial non-opacification", "occlusion", 
            "ischemic stroke", "hypoattenuation", "gray-white matter differentiation", 
            "sylvian fissure", "carotid bifurcations", "emergency / stat", "last known well"
        ]
    },
    "BRAIN_MRI_REPORT": {
        "display": "Brain MRI & Neuroradiology Scan",
        "routing": "NEURO_ONCOLOGY",
        "keywords": [
            "mri brain", "brain mri", "neuroradiology", "brain parenchyma", 
            "flair", "t1", "t2", "diffusion-weighted", "dwi", "adc map", 
            "gadolinium", "intra-axial mass", "extra-axial mass", "sulcal effacement", 
            "midline shift", "subfalcine", "intracranial mass", "intracranial neoplasm", 
            "peripheral enhancement", "nonenhancing component"
        ]
    },
    "LAB_REPORT": {
        "display": "Clinical Laboratory Bloodwork & Metabolic Panel",
        "routing": "CARDIOMETABOLIC_MULTI_ORGAN",
        "keywords": [
            "fasting blood glucose", "fasting plasma glucose", "serum cholesterol", 
            "lipid panel", "hba1c", "serum creatinine", "blood urea", "bun", 
            "sgpt", "alt", "sgot", "ast", "total bilirubin", "serum albumin", 
            "egfr", "hemoglobin", "complete blood count", "cbc", "triglycerides", 
            "ldl cholesterol", "hdl cholesterol"
        ]
    },
    "ECG_REPORT": {
        "display": "12-Lead Electrocardiogram (ECG)",
        "routing": "ELECTROPHYSIOLOGY",
        "keywords": ["12-lead ecg", "electrocardiogram", "sinus rhythm", "st elevation", "qrs duration", "pr interval", "qtc"]
    },
    "CHEST_IMAGING_REPORT": {
        "display": "Chest Radiograph / Thoracic Imaging",
        "routing": "PULMONOLOGY",
        "keywords": ["chest x-ray", "chest radiograph", "ct chest", "pulmonary parenchyma", "pleural effusion", "consolidation"]
    },
    "PATHOLOGY_REPORT": {
        "display": "Surgical Pathology & Histopathology",
        "routing": "HISTOPATHOLOGY",
        "keywords": ["histopathology", "biopsy specimen", "immunohistochemistry", "hematoxylin and eosin", "mitotic count", "resection margins"]
    }
}

class DocumentClassifier:
    def classify(self, text: str) -> ClassificationResult:
        t = text.lower()
        
        # Priority check for CT/CTA
        if ("ct angiography" in t or "cta" in t or "noncontrast ct" in t) and ("m1 segment" in t or "middle cerebral artery" in t or "arterial" in t or "head and neck" in t):
            matched = [k for k in DOCUMENT_TAXONOMY["CT_CTA_STROKE_REPORT"]["keywords"] if k in t]
            return ClassificationResult(
                document_type="CT_CTA_STROKE_REPORT",
                document_type_display=DOCUMENT_TAXONOMY["CT_CTA_STROKE_REPORT"]["display"],
                routing_target=DOCUMENT_TAXONOMY["CT_CTA_STROKE_REPORT"]["routing"],
                confidence=0.98,
                evidence_terms=matched,
                is_supported=True,
                unsupported_message=""
            )
        
        scores: Dict[str, Tuple[int, List[str]]] = {}
        for doc_class, info in DOCUMENT_TAXONOMY.items():
            matched_terms = [k for k in info["keywords"] if k in t]
            score = len(matched_terms)
            if score > 0:
                scores[doc_class] = (score, matched_terms)
                
        if not scores:
            return ClassificationResult(
                document_type="UNKNOWN",
                document_type_display="Unrecognized Clinical Document",
                routing_target="NONE",
                confidence=0.0,
                evidence_terms=[],
                is_supported=False,
                unsupported_message="The uploaded document does not match any recognized clinical modality. Please upload a Brain MRI, Stroke CT/CTA report, or Laboratory Bloodwork panel."
            )
            
        best_class = max(scores.keys(), key=lambda k: scores[k][0])
        match_count, matched_terms = scores[best_class]
        confidence = min(0.99, max(0.65, round(match_count / 5.0 * 0.95, 2)))
        
        is_supported = best_class in ["CT_CTA_STROKE_REPORT", "BRAIN_MRI_REPORT", "LAB_REPORT"]
        unsupported_msg = ""
        if not is_supported:
            unsupported_msg = f"Document classified as {DOCUMENT_TAXONOMY[best_class]['display']}. Automated risk models for this specific modality are in clinical development."

        return ClassificationResult(
            document_type=best_class,
            document_type_display=DOCUMENT_TAXONOMY[best_class]["display"],
            routing_target=DOCUMENT_TAXONOMY[best_class]["routing"],
            confidence=confidence,
            evidence_terms=matched_terms,
            is_supported=is_supported,
            unsupported_message=unsupported_msg
        )

document_classifier = DocumentClassifier()
