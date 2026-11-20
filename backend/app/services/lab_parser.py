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

        # 3. Dynamic multi-line and tabular backfill
        try:
            from backend.app.services.universal_disease_service import extract_all_clinical_parameters_dynamic
            dyn = extract_all_clinical_parameters_dynamic(text)
            
            mapping = [
                ("creatinine", "creatinine", "Serum Creatinine", "Renal Function", "mg/dL", 0.6, 1.2, 1.5, "Elevated creatinine indicates impaired nephron waste filtration.", "Adequate glomerular filtration."),
                ("egfr", "egfr", "Estimated GFR (eGFR)", "Renal Function", "mL/min/1.73m²", 60.0, 120.0, 45.0, "eGFR <60 indicates compromised renal filtration.", "Healthy renal filtration rate."),
                ("glucose", "glucose", "Fasting Plasma Glucose", "Metabolic & Glycemic", "mg/dL", 70.0, 99.0, 125.0, "Elevated fasting blood sugar.", "Healthy fasting glycemic control."),
                ("hba1c", "hba1c", "Glycated Hemoglobin (HbA1c)", "Metabolic & Glycemic", "%", 4.0, 5.6, 6.4, "Elevated HbA1c.", "Normal glycemic control."),
                ("cholesterol", "cholesterol", "Total Serum Cholesterol", "Lipid Profile", "mg/dL", 125.0, 199.0, 240.0, "Elevated cholesterol.", "Desirable cholesterol limits."),
                ("ldl", "ldl", "LDL Cholesterol", "Lipid Profile", "mg/dL", 50.0, 99.0, 160.0, "Elevated atherogenic LDL.", "Optimal low-density lipoprotein."),
                ("hdl", "hdl", "HDL Cholesterol", "Lipid Profile", "mg/dL", 40.0, 80.0, 90.0, "Reduced cardioprotective HDL.", "Cardioprotective concentration."),
                ("triglycerides", "triglycerides", "Serum Triglycerides", "Lipid Profile", "mg/dL", 50.0, 149.0, 200.0, "Elevated triglycerides.", "Normal neutral fat levels."),
                ("bp_sys", "bp_systolic", "Systolic Blood Pressure", "Hemodynamics", "mmHg", 90.0, 120.0, 140.0, "Systolic BP elevation.", "Optimal systolic pressure."),
                ("bp_dia", "bp_diastolic", "Diastolic Blood Pressure", "Hemodynamics", "mmHg", 60.0, 80.0, 90.0, "Diastolic BP elevation.", "Normal diastolic baseline."),
                ("alt", "sgpt_alt", "ALT / SGPT (Liver Transaminase)", "Liver Function", "U/L", 7.0, 56.0, 80.0, "Elevated ALT reflects hepatocyte injury.", "Healthy hepatic enzyme level."),
                ("ast", "sgot_ast", "AST / SGOT (Liver Transaminase)", "Liver Function", "U/L", 10.0, 40.0, 75.0, "Elevated AST reflects hepatocellular stress.", "Normal hepatic enzyme baseline."),
                ("total_bilirubin", "total_bilirubin", "Total Bilirubin", "Liver Function", "mg/dL", 0.2, 1.2, 2.0, "Hyperbilirubinemia indicates impaired excretory clearance.", "Normal biliary excretion."),
                ("direct_bilirubin", "direct_bilirubin", "Direct Bilirubin", "Liver Function", "mg/dL", 0.0, 0.3, 0.8, "Elevated conjugated bilirubin fraction.", "Normal conjugated bilirubin."),
                ("alp", "alkaline_phosphotase", "Alkaline Phosphatase (ALP)", "Liver Function", "U/L", 44.0, 147.0, 200.0, "Elevated alkaline phosphatase / cholestatic pattern.", "Normal biliary enzyme levels."),
                ("serum_albumin", "serum_albumin", "Serum Albumin", "Liver & Renal Function", "g/dL", 3.5, 5.0, 2.8, "Low serum albumin.", "Healthy serum albumin level.")
            ]

            for dyn_k, raw_k, name, cat, unit, low, high, crit, exp_h, exp_n in mapping:
                if dyn_k in dyn and raw_k not in raw_values:
                    val = float(dyn[dyn_k])
                    raw_values[raw_k] = val
                    if raw_k == "hdl":
                        abn = "LOW" if val < 40.0 else "NORMAL"
                    elif raw_k == "egfr":
                        abn = "LOW" if val < 60.0 else "NORMAL"
                    elif raw_k == "serum_albumin":
                        abn = "LOW" if val < 3.5 else "NORMAL"
                    else:
                        abn = "CRITICAL" if val > crit else "ELEVATED" if val > high else "LOW" if val < low else "NORMAL"

                    provenance_list.append(LabBiomarkerProvenance(
                        key=raw_k,
                        name=name,
                        category=cat,
                        raw_value=f"{val} {unit}",
                        numeric_value=val,
                        unit=unit,
                        reference_range=f"{low} - {high} {unit}",
                        reference_low=low,
                        reference_high=high,
                        abnormality=abn,
                        source_section="LABORATORY MEASUREMENTS",
                        source_text=f"{name}: {val} {unit}",
                        confidence=0.98,
                        clinical_interpretation=exp_h if abn in ["CRITICAL", "ELEVATED", "LOW"] else exp_n
                    ))
        except Exception:
            pass

        return provenance_list, raw_values

lab_parser = LabReportParser()
