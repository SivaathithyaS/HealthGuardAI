import re
from typing import Dict, Any, List, Tuple
from pydantic import BaseModel

class LabBiomarkerProvenance(BaseModel):
    key: str
    name: str
    category: str
    raw_value: str
    numeric_value: float
    unit: str
    reference_range: str
    reference_low: float
    reference_high: float
    abnormality: str  # "NORMAL", "ELEVATED", "CRITICAL", "LOW"
    source_section: str
    source_text: str
    confidence: float
    clinical_interpretation: str

LAB_PATTERNS = [
    {
        "key": "glucose",
        "name": "Fasting Plasma Glucose",
        "category": "Metabolic & Glycemic",
        "pattern": r"(?:fasting\s+plasma\s+glucose|fasting\s+blood\s+glucose|fasting\s+glucose|fbs|bgr)[:\s]+(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
        "unit": "mg/dL", "low": 70.0, "high": 99.0, "crit": 125.0,
        "explain_high": "Elevated fasting blood sugar indicates impaired fasting glucose / insulin resistance.",
        "explain_normal": "Healthy fasting glycemic control within standard reference intervals."
    },
    {
        "key": "hba1c",
        "name": "Glycated Hemoglobin (HbA1c)",
        "category": "Metabolic & Glycemic",
        "pattern": r"hba1c[:\s]+(\d+(?:\.\d+)?)\s*%?",
        "unit": "%", "low": 4.0, "high": 5.6, "crit": 6.4,
        "explain_high": "HbA1c 5.7 - 6.4% reflects sustained pre-diabetic glycemic burden over 3 months.",
        "explain_normal": "Normal average 3-month blood glucose saturation."
    },
    {
        "key": "cholesterol",
        "name": "Total Serum Cholesterol",
        "category": "Lipid Profile",
        "pattern": r"(?:total\s+cholesterol|serum\s+cholesterol|chol)[:\s]+(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
        "unit": "mg/dL", "low": 125.0, "high": 199.0, "crit": 240.0,
        "explain_high": "Total cholesterol >200 mg/dL promotes subendothelial atherogenesis and arterial narrowing.",
        "explain_normal": "Circulating total cholesterol is within desirable physiological limits."
    },
    {
        "key": "ldl",
        "name": "LDL Cholesterol (Atherogenic)",
        "category": "Lipid Profile",
        "pattern": r"ldl(?:\s+cholesterol)?[:\s]+(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
        "unit": "mg/dL", "low": 50.0, "high": 99.0, "crit": 160.0,
        "explain_high": "Elevated LDL particles directly infiltrate coronary intima, forming atheroma.",
        "explain_normal": "Optimal low-density lipoprotein levels."
    },
    {
        "key": "hdl",
        "name": "HDL Cholesterol (Cardioprotective)",
        "category": "Lipid Profile",
        "pattern": r"hdl(?:\s+cholesterol)?[:\s]+(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
        "unit": "mg/dL", "low": 40.0, "high": 80.0, "crit": 90.0,
        "explain_high": "Cardioprotective HDL concentration.",
        "explain_normal": "Adequate reverse cholesterol transport capacity."
    },
    {
        "key": "triglycerides",
        "name": "Serum Triglycerides",
        "category": "Lipid Profile",
        "pattern": r"triglycerides[:\s]+(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
        "unit": "mg/dL", "low": 50.0, "high": 149.0, "crit": 200.0,
        "explain_high": "Elevated triglycerides (>150 mg/dL) signal metabolic syndrome and vascular risk.",
        "explain_normal": "Normal circulating neutral fat concentrations."
    },
    {
        "key": "bp_systolic",
        "name": "Systolic Blood Pressure",
        "category": "Hemodynamics",
        "pattern": r"(?:blood\s+pressure|bp)[:\s]+(\d{2,3})\s*(?:/|\s)\s*\d{2,3}",
        "unit": "mm Hg", "low": 90.0, "high": 120.0, "crit": 140.0,
        "explain_high": "Systolic BP ≥130-140 mm Hg represents hypertension, straining myocardial afterload.",
        "explain_normal": "Optimal vascular systolic pressure."
    },
    {
        "key": "bp_diastolic",
        "name": "Diastolic Blood Pressure",
        "category": "Hemodynamics",
        "pattern": r"(?:blood\s+pressure|bp)[:\s]+\d{2,3}\s*(?:/|\s)\s*(\d{2,3})",
        "unit": "mm Hg", "low": 60.0, "high": 80.0, "crit": 90.0,
        "explain_high": "Diastolic BP ≥85-90 mm Hg reflects elevated systemic vascular resistance.",
        "explain_normal": "Normal resting diastolic baseline."
    },
    {
        "key": "creatinine",
        "name": "Serum Creatinine",
        "category": "Renal Function",
        "pattern": r"(?:serum\s+creatinine|creatinine)[:\s]+(\d+(?:\.\d+)?)\s*(?:mg/dl)?",
        "unit": "mg/dL", "low": 0.6, "high": 1.2, "crit": 1.5,
        "explain_high": "Elevated creatinine indicates impaired nephron waste filtration.",
        "explain_normal": "Adequate glomerular filtration and waste excretion."
    },
    {
        "key": "egfr",
        "name": "Estimated GFR (eGFR)",
        "category": "Renal Function",
        "pattern": r"egfr[:\s]+(\d+(?:\.\d+)?)\s*(?:ml/min)?",
        "unit": "mL/min/1.73m²", "low": 60.0, "high": 120.0, "crit": 45.0,
        "explain_high": "Normal renal filtration.",
        "explain_normal": "Healthy renal filtration rate."
    },
    {
        "key": "sgpt_alt",
        "name": "ALT / SGPT (Liver Transaminase)",
        "category": "Liver Function",
        "pattern": r"(?:alt|sgpt)[:\s]+(\d+(?:\.\d+)?)\s*(?:u/l|iu/l)?",
        "unit": "U/L", "low": 7.0, "high": 56.0, "crit": 80.0,
        "explain_high": "Elevated ALT reflects hepatocyte membrane stress or fatty liver infiltration.",
        "explain_normal": "Healthy hepatic enzyme level."
    },
    {
        "key": "sgot_ast",
        "name": "AST / SGOT (Liver Transaminase)",
        "category": "Liver Function",
        "pattern": r"(?:ast|sgot)[:\s]+(\d+(?:\.\d+)?)\s*(?:u/l|iu/l)?",
        "unit": "U/L", "low": 10.0, "high": 40.0, "crit": 75.0,
        "explain_high": "Elevated AST reflects hepatic or muscle cellular stress.",
        "explain_normal": "Normal hepatic enzyme baseline."
    }
]

class LabReportParser:
    def parse(self, text: str) -> Tuple[List[LabBiomarkerProvenance], Dict[str, float]]:
        clean = re.sub(r"[ \t]+", " ", text)
        provenance_list: List[LabBiomarkerProvenance] = []
        raw_values: Dict[str, float] = {}

        # 1. Height and Weight extraction for derived BMI
        ht_m = re.search(r"height[:\s]+(\d+(?:\.\d+)?)\s*(?:cm)?", clean, re.IGNORECASE)
        wt_m = re.search(r"weight[:\s]+(\d+(?:\.\d+)?)\s*(?:kg)?", clean, re.IGNORECASE)
        if ht_m and wt_m:
            try:
                ht_val = float(ht_m.group(1))
                wt_val = float(wt_m.group(1))
                if ht_val > 50:
                    bmi_calc = round(wt_val / ((ht_val / 100.0) ** 2), 1)
                    raw_values["bmi"] = bmi_calc
                    provenance_list.append(LabBiomarkerProvenance(
                        key="bmi",
                        name="Body Mass Index (BMI)",
                        category="Anthropometrics",
                        raw_value=f"{bmi_calc} kg/m²",
                        numeric_value=bmi_calc,
                        unit="kg/m²",
                        reference_range="18.5 - 24.9 kg/m²",
                        reference_low=18.5,
                        reference_high=24.9,
                        abnormality="ELEVATED" if bmi_calc > 29.9 else "HIGH" if bmi_calc > 24.9 else "NORMAL",
                        source_section="CLINICAL MEASUREMENTS",
                        source_text=f"Height: {ht_val} cm, Weight: {wt_val} kg",
                        confidence=0.99,
                        clinical_interpretation=f"Calculated from Height ({ht_val} cm) and Weight ({wt_val} kg). BMI >30 indicates Class 1 Obesity."
                    ))
            except Exception:
                pass

        # 2. Extract standard biomarkers with exact source snippets
        for item in LAB_PATTERNS:
            match = re.search(item["pattern"], clean, re.IGNORECASE)
            if match:
                try:
                    num_val = float(match.group(1))
                    raw_values[item["key"]] = num_val
                    
                    if item["key"] == "hdl":
                        abnormality = "LOW" if num_val < 40.0 else "NORMAL"
                        interpretation = "Reduced cardioprotective HDL clearance." if abnormality == "LOW" else "Cardioprotective concentration."
                    elif item["key"] == "egfr":
                        abnormality = "LOW" if num_val < 60.0 else "NORMAL"
                        interpretation = "eGFR <60 indicates compromised renal filtration." if abnormality == "LOW" else "Healthy renal filtration rate."
                    else:
                        if num_val > item["crit"]:
                            abnormality = "CRITICAL"
                            interpretation = item["explain_high"]
                        elif num_val > item["high"]:
                            abnormality = "ELEVATED"
                            interpretation = item["explain_high"]
                        elif num_val < item["low"]:
                            abnormality = "LOW"
                            interpretation = "Below standard physiological baseline."
                        else:
                            abnormality = "NORMAL"
                            interpretation = item["explain_normal"]

                    provenance_list.append(LabBiomarkerProvenance(
                        key=item["key"],
                        name=item["name"],
                        category=item["category"],
                        raw_value=f"{num_val} {item['unit']}",
                        numeric_value=num_val,
                        unit=item["unit"],
                        reference_range=f"{item['low']} - {item['high']} {item['unit']}",
                        reference_low=item["low"],
                        reference_high=item["high"],
                        abnormality=abnormality,
                        source_section="LABORATORY MEASUREMENTS",
                        source_text=match.group(0),
                        confidence=0.98,
                        clinical_interpretation=interpretation
                    ))
                except Exception:
                    continue

        return provenance_list, raw_values

lab_parser = LabReportParser()
