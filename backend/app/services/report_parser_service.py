import re
import io
from typing import Dict, Any, List, Tuple
from pypdf import PdfReader
from PIL import Image
import pytesseract
from backend.app.schemas.multi_disease import ExtractedBiomarker

BIOMARKER_DICTIONARY = [
    {
        "key": "age",
        "name": "Patient Age",
        "category": "Demographics",
        "patterns": [
            r"age\s*/\s*sex[:\s]+(\d{1,3})\s*(?:years|yrs|yo)?",
            r"age[:\s]+(\d{1,3})",
            r"(\d{1,3})\s*(?:years\s+old|yrs\s+old|years|yrs)\s*/\s*(?:male|female|m|f)",
        ],
        "unit": "years",
        "ref_min": 18.0,
        "ref_max": 75.0,
        "crit_max": 85.0,
        "ref_str": "Adult (18-75)",
        "explain_high": "Advancing age increases cumulative metabolic and cardiovascular disease susceptibility.",
        "explain_normal": "Adult demographic profile."
    },
    {
        "key": "glucose",
        "name": "Fasting Blood Glucose",
        "category": "Metabolic & Glycemic",
        "patterns": [
            r"(?:fasting\s+plasma\s+glucose|fasting\s+blood\s+glucose|fasting\s+glucose|fbs|bgr)[:\s]+(\d+(?:\.\d+)?)",
            r"glucose[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mg/dL",
        "ref_min": 70.0,
        "ref_max": 99.0,
        "crit_max": 125.0,
        "ref_str": "70 - 99 mg/dL",
        "explain_high": "Elevated fasting blood sugar reflects insulin resistance or impaired glucose tolerance.",
        "explain_normal": "Optimal fasting glycemic control."
    },
    {
        "key": "hba1c",
        "name": "Glycated Hemoglobin (HbA1c)",
        "category": "Metabolic & Glycemic",
        "patterns": [
            r"hba1c[:\s]+(\d+(?:\.\d+)?)",
            r"glycated\s+hemoglobin[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "%",
        "ref_min": 4.0,
        "ref_max": 5.6,
        "crit_max": 6.4,
        "ref_str": "< 5.7 %",
        "explain_high": "HbA1c 5.7 - 6.4% indicates pre-diabetes; ≥6.5% indicates Type 2 Diabetes.",
        "explain_normal": "Normal average 3-month blood glucose saturation."
    },
    {
        "key": "cholesterol",
        "name": "Total Cholesterol",
        "category": "Lipid Profile",
        "patterns": [
            r"total\s+cholesterol[:\s]+(\d+(?:\.\d+)?)",
            r"serum\s+cholesterol[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mg/dL",
        "ref_min": 125.0,
        "ref_max": 199.0,
        "crit_max": 240.0,
        "ref_str": "< 200 mg/dL",
        "explain_high": "Total cholesterol >200 mg/dL promotes atherogenesis and coronary plaque progression.",
        "explain_normal": "Circulating total cholesterol is within desirable limits."
    },
    {
        "key": "ldl",
        "name": "LDL Cholesterol (Atherogenic)",
        "category": "Lipid Profile",
        "patterns": [
            r"ldl(?:\s+cholesterol)?[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mg/dL",
        "ref_min": 50.0,
        "ref_max": 99.0,
        "crit_max": 160.0,
        "ref_str": "< 100 mg/dL",
        "explain_high": "High LDL particles directly infiltrate the arterial wall, accelerating atherosclerosis.",
        "explain_normal": "Optimal low-density lipoprotein levels."
    },
    {
        "key": "hdl",
        "name": "HDL Cholesterol (Cardioprotective)",
        "category": "Lipid Profile",
        "patterns": [
            r"hdl(?:\s+cholesterol)?[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mg/dL",
        "ref_min": 40.0,
        "ref_max": 80.0,
        "crit_max": 90.0,
        "ref_str": "≥ 40 mg/dL",
        "explain_high": "High HDL is cardioprotective.",
        "explain_normal": "Adequate reverse cholesterol transport capacity."
    },
    {
        "key": "triglycerides",
        "name": "Serum Triglycerides",
        "category": "Lipid Profile",
        "patterns": [
            r"triglycerides[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mg/dL",
        "ref_min": 50.0,
        "ref_max": 149.0,
        "crit_max": 200.0,
        "ref_str": "< 150 mg/dL",
        "explain_high": "Elevated triglycerides (>150 mg/dL) signal metabolic syndrome and cardiovascular risk.",
        "explain_normal": "Normal circulating neutral fat concentrations."
    },
    {
        "key": "bp_systolic",
        "name": "Systolic Blood Pressure",
        "category": "Hemodynamics",
        "patterns": [
            r"blood\s+pressure[:\s]+(\d{2,3})\s*(?:/|\s)\s*\d{2,3}",
            r"bp[:\s]+(\d{2,3})\s*(?:/|\s)\s*\d{2,3}"
        ],
        "unit": "mm Hg",
        "ref_min": 90.0,
        "ref_max": 120.0,
        "crit_max": 140.0,
        "ref_str": "< 120 mm Hg",
        "explain_high": "Systolic BP ≥130-140 mm Hg indicates hypertension, straining arterial vasculature.",
        "explain_normal": "Optimal vascular systolic baseline."
    },
    {
        "key": "bp_diastolic",
        "name": "Diastolic Blood Pressure",
        "category": "Hemodynamics",
        "patterns": [
            r"blood\s+pressure[:\s]+\d{2,3}\s*(?:/|\s)\s*(\d{2,3})",
            r"bp[:\s]+\d{2,3}\s*(?:/|\s)\s*(\d{2,3})"
        ],
        "unit": "mm Hg",
        "ref_min": 60.0,
        "ref_max": 80.0,
        "crit_max": 90.0,
        "ref_str": "< 80 mm Hg",
        "explain_high": "Diastolic BP ≥85-90 mm Hg reflects elevated systemic vascular resistance.",
        "explain_normal": "Healthy resting diastolic arterial pressure."
    },
    {
        "key": "bmi",
        "name": "Body Mass Index (BMI)",
        "category": "Anthropometrics",
        "patterns": [
            r"bmi[:\s]+(\d+(?:\.\d+)?)",
            r"body\s+mass\s+index[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "kg/m²",
        "ref_min": 18.5,
        "ref_max": 24.9,
        "crit_max": 29.9,
        "ref_str": "18.5 - 24.9 kg/m²",
        "explain_high": "BMI ≥30 kg/m² indicates obesity, elevating metabolic and cardiorespiratory strain.",
        "explain_normal": "Healthy body mass composition."
    },
    {
        "key": "creatinine",
        "name": "Serum Creatinine",
        "category": "Renal Function",
        "patterns": [
            r"serum\s+creatinine[:\s]+(\d+(?:\.\d+)?)",
            r"creatinine[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mg/dL",
        "ref_min": 0.6,
        "ref_max": 1.2,
        "crit_max": 1.5,
        "ref_str": "0.7 - 1.3 mg/dL",
        "explain_high": "Elevated creatinine indicates impaired nephron waste filtration.",
        "explain_normal": "Adequate glomerular filtration and waste excretion."
    },
    {
        "key": "egfr",
        "name": "Estimated GFR (eGFR)",
        "category": "Renal Function",
        "patterns": [
            r"egfr[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "mL/min/1.73m²",
        "ref_min": 60.0,
        "ref_max": 120.0,
        "crit_max": 45.0,
        "ref_str": "≥ 60 mL/min/1.73m²",
        "explain_high": "Normal renal filtration.",
        "explain_normal": "Healthy renal filtration rate."
    },
    {
        "key": "sgpt_alt",
        "name": "ALT / SGPT (Liver Transaminase)",
        "category": "Liver Function",
        "patterns": [
            r"alt[:\s]+(\d+(?:\.\d+)?)",
            r"sgpt[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "U/L",
        "ref_min": 7.0,
        "ref_max": 56.0,
        "crit_max": 80.0,
        "ref_str": "7 - 56 U/L",
        "explain_high": "Elevated ALT reflects hepatocyte membrane stress or fatty liver infiltration.",
        "explain_normal": "Healthy hepatic enzyme level."
    },
    {
        "key": "sgot_ast",
        "name": "AST / SGOT (Liver Transaminase)",
        "category": "Liver Function",
        "patterns": [
            r"ast[:\s]+(\d+(?:\.\d+)?)",
            r"sgot[:\s]+(\d+(?:\.\d+)?)"
        ],
        "unit": "U/L",
        "ref_min": 10.0,
        "ref_max": 40.0,
        "crit_max": 75.0,
        "ref_str": "10 - 40 U/L",
        "explain_high": "Elevated AST reflects liver or muscle tissue cellular stress.",
        "explain_normal": "Normal hepatic enzyme baseline."
    }
]

NORTHSTAR_BRAIN_MRI_REPORT = """
NORTHSTAR UNIVERSITY MEDICAL CENTER
Department of Radiology • Neuroradiology Service
SYNTHETIC / AI DEMONSTRATION REPORT
Fabricated patient and fabricated imaging findings. Not a real hospital record and not for clinical use.

Patient: Elena Kovacs (Synthetic)     MRN: NSMC-DEMO-82641
Age / Sex: 47 years / Female           Study Date: 16 Aug 2026
Accession: MRI-26-0816-119             Ordering Service: Neurology
Exam: MRI Brain with and without IV contrast   Status: Final / Synthetic

Clinical History / Indication
---------------------------------------------------------------------------------
Six-week history of progressively worsening morning headaches with intermittent nausea. 
Two recent episodes of transient left facial twitching and difficulty finding words lasting approximately 1–2 minutes. 
No known prior intracranial neoplasm. MRI requested for further evaluation of new focal neurologic symptoms.

Technique
---------------------------------------------------------------------------------
Multiplanar, multisequence MRI of the brain was performed before and after intravenous gadolinium-based contrast. 
Sequences include axial T1, T2, FLAIR, diffusion-weighted imaging with ADC maps, susceptibility-weighted imaging, 
and post-contrast T1-weighted imaging in axial and multiplanar planes.

Findings
---------------------------------------------------------------------------------
Brain Parenchyma: There is an approximately 5.4 x 4.7 x 4.2 cm infiltrative intra-axial mass centered in the right frontal opercular and anterior insular region. The lesion demonstrates heterogeneous T2/FLAIR hyperintensity with irregular peripheral enhancement and a central nonenhancing component. Surrounding extensive vasogenic and infiltrative edema extends into the adjacent frontal and temporal white matter.
Diffusion: Areas of restricted diffusion are present along portions of the enhancing rim. No separate acute territorial infarction is identified.
Susceptibility: Scattered small foci of susceptibility are present within the lesion, compatible with intralesional blood-product or mineralization-related susceptibility in this synthetic case.
Mass Effect: Local sulcal effacement with compression of the right lateral ventricle. Approximately 7 mm leftward midline shift at the level of the septum pellucidum. Mild right-to-left subfalcine displacement.
Ventricles / CSF: No hydrocephalus. Basal cisterns remain patent.
Posterior Fossa: Cerebellum and brainstem are without focal abnormal enhancement.
Vascular Flow Voids: Major intracranial arterial flow voids are maintained.
Calvarium / Soft Tissues: No destructive calvarial lesion identified.

Impression
---------------------------------------------------------------------------------
1. Large infiltrative right fronto-insular intra-axial mass (5.4 x 4.7 x 4.2 cm) with heterogeneous signal, irregular peripheral enhancement, central nonenhancing necrotic component, and extensive surrounding vasogenic edema.
2. Associated local mass effect with approximately 7 mm leftward midline shift.
3. Imaging characteristics are concerning for an aggressive primary intracranial neoplastic process (High-Grade Glioma / Glioblastoma). Histopathologic confirmation is required for definitive classification.
4. Urgent neurosurgical / neuro-oncology consultation and tissue diagnosis recommended.
"""

RIVERBEND_DEMO_REPORT = """
RIVERBEND GENERAL HOSPITAL
Department of Internal Medicine • Health Assessment Unit
SYNTHETIC / DEMONSTRATION MEDICAL REPORT
Not a real patient record • Created for AI health-risk-analysis testing only

Patient ID: RBH-DEMO-04721            Report No.: IM-2026-0816-04721
Patient Name: Aarav Mehta (Synthetic) Age / Sex: 52 years / Male
Date of Assessment: 16 Aug 2026       Department: Internal Medicine
Ordering Clinician: Dr. N. Rao        Specimen Status: Fasting / Routine

Clinical Measurements
---------------------------------------------------------------------------------
Height: 174 cm
Weight: 91.8 kg
Blood Pressure: 148 / 94 mmHg          (Ref: <120 / <80 mmHg) [STAGE 2 HYPERTENSION]
Resting Heart Rate: 86 bpm             (Ref: 60–100 bpm) [NORMAL]
Fasting Plasma Glucose: 118 mg/dL      (Ref: 70–99 mg/dL) [ELEVATED / PRE-DIABETIC]
HbA1c: 6.2 %                           (Ref: <5.7 %) [ELEVATED / PRE-DIABETIC]
Total Cholesterol: 238 mg/dL           (Ref: <200 mg/dL) [HIGH]
LDL Cholesterol: 158 mg/dL             (Ref: <100 mg/dL) [HIGH]
HDL Cholesterol: 39 mg/dL              (Ref: >=40 mg/dL) [BORDERLINE LOW]
Triglycerides: 205 mg/dL               (Ref: <150 mg/dL) [HIGH]
ALT: 31 U/L                            (Ref: 7–56 U/L) [NORMAL]
AST: 27 U/L                            (Ref: 10–40 U/L) [NORMAL]
Creatinine: 1.0 mg/dL                  (Ref: 0.7–1.3 mg/dL) [NORMAL]
eGFR: 88 mL/min/1.73m2                 (Ref: >=60 mL/min) [NORMAL]

Clinical Notes & Observations
---------------------------------------------------------------------------------
General appearance: Alert, oriented, ambulatory; no acute distress noted.
Cardiovascular: Regular rhythm on routine examination.
Respiratory: Breath sounds clear bilaterally; oxygen saturation 97% on room air.
Symptoms reported: Intermittent fatigue; occasional exertional breathlessness.
12-lead ECG: Sinus rhythm; no acute ischemic changes.
"""

SAMPLE_LAB_REPORTS = {
    "metabolic_renal_case": """
METROPOLITAN CLINICAL LABORATORIES
PATIENT COMPREHENSIVE HEALTH REPORT
Patient Name: John Doe    Age: 58 yrs    Gender: Male
Date of Collection: 2026-07-14

==================================================
1. COMPREHENSIVE METABOLIC & LIPID PANEL
Fasting Blood Glucose: 168 mg/dL        (Ref: 70 - 99 mg/dL) [HIGH]
Serum Cholesterol: 248 mg/dL           (Ref: 125 - 200 mg/dL) [HIGH]
Blood Pressure: 145/92 mm Hg           (Ref: 90 - 120 mm Hg) [HIGH]
Body Mass Index (BMI): 31.4 kg/m2      (Ref: 18.5 - 24.9 kg/m2) [HIGH]

2. RENAL FUNCTION TEST (KFT / RFT)
Serum Creatinine: 1.85 mg/dL           (Ref: 0.6 - 1.2 mg/dL) [HIGH]
Blood Urea Nitrogen (BUN): 52 mg/dL    (Ref: 10 - 45 mg/dL) [HIGH]
Hemoglobin: 11.2 g/dL                  (Ref: 12.0 - 17.5 g/dL) [LOW]

3. LIVER ENZYME PROFILE (LFT)
SGPT / ALT: 48 IU/L                    (Ref: 7 - 45 IU/L) [BORDERLINE HIGH]
SGOT / AST: 42 IU/L                    (Ref: 8 - 40 IU/L) [BORDERLINE HIGH]
Total Bilirubin: 1.1 mg/dL             (Ref: 0.2 - 1.2 mg/dL) [NORMAL]
Serum Albumin: 3.8 g/dL                (Ref: 3.5 - 5.2 g/dL) [NORMAL]
==================================================
CLINICAL NOTES: Patient presents with uncontrolled hyperglycemia, elevated arterial BP, hypercholesterolemia, and early diabetic nephropathy signs.
""",
    "hepatic_fatty_liver_case": """
APOLLO ADVANCED DIAGNOSTICS
LIVER & METABOLIC FUNCTION SCREENING
Patient Name: Robert Smith    Age: 52 yrs    Gender: Male
Date of Examination: 2026-08-02

==================================================
1. LIVER FUNCTION TEST (LFT)
SGPT / ALT: 88 IU/L                    (Ref: 7 - 45 IU/L) [ELEVATED]
SGOT / AST: 76 IU/L                    (Ref: 8 - 40 IU/L) [ELEVATED]
Total Bilirubin: 2.1 mg/dL             (Ref: 0.2 - 1.2 mg/dL) [ELEVATED]
Serum Albumin: 3.2 g/dL                (Ref: 3.5 - 5.2 g/dL) [LOW]
Alkaline Phosphatase: 260 IU/L         (Ref: 50 - 220 IU/L) [ELEVATED]

2. METABOLIC & CARDIOVASCULAR
Fasting Blood Glucose: 132 mg/dL        (Ref: 70 - 99 mg/dL) [HIGH]
Serum Cholesterol: 215 mg/dL           (Ref: 125 - 200 mg/dL) [ELEVATED]
Blood Pressure: 138/86 mm Hg           (Ref: 90 - 120 mm Hg) [ELEVATED]
Body Mass Index (BMI): 29.8 kg/m2      (Ref: 18.5 - 24.9 kg/m2) [ELEVATED]

3. RENAL PROFILE
Serum Creatinine: 1.0 mg/dL            (Ref: 0.6 - 1.2 mg/dL) [NORMAL]
Blood Urea: 32 mg/dL                   (Ref: 10 - 45 mg/dL) [NORMAL]
==================================================
IMPRESSION: Findings suggestive of non-alcoholic steatohepatitis (NASH / Fatty Liver) with secondary metabolic syndrome.
""",
    "healthy_checkup_case": """
WELLNESS PREVENTIVE HEALTHCARE LABS
ANNUAL EXECUTIVE HEALTH ASSESSMENT
Patient Name: Emily Clark    Age: 42 yrs    Gender: Female
Date of Test: 2026-08-10

==================================================
1. COMPLETE METABOLIC & LIPID PANEL
Fasting Blood Glucose: 86 mg/dL         (Ref: 70 - 99 mg/dL) [OPTIMAL]
Serum Cholesterol: 168 mg/dL           (Ref: 125 - 200 mg/dL) [OPTIMAL]
Blood Pressure: 114/74 mm Hg           (Ref: 90 - 120 mm Hg) [OPTIMAL]
Body Mass Index (BMI): 22.4 kg/m2      (Ref: 18.5 - 24.9 kg/m2) [NORMAL]

2. RENAL & HEMATOLOGY
Serum Creatinine: 0.85 mg/dL           (Ref: 0.6 - 1.2 mg/dL) [NORMAL]
Blood Urea: 24 mg/dL                   (Ref: 10 - 45 mg/dL) [NORMAL]
Hemoglobin: 13.8 g/dL                  (Ref: 12.0 - 17.5 g/dL) [NORMAL]

3. LIVER ENZYMES
SGPT / ALT: 22 IU/L                    (Ref: 7 - 45 IU/L) [NORMAL]
SGOT / AST: 20 IU/L                    (Ref: 8 - 40 IU/L) [NORMAL]
Total Bilirubin: 0.7 mg/dL             (Ref: 0.2 - 1.2 mg/dL) [NORMAL]
Serum Albumin: 4.4 g/dL                (Ref: 3.5 - 5.2 g/dL) [OPTIMAL]
==================================================
IMPRESSION: All evaluated metabolic, cardiovascular, hepatic, and renal biomarkers are well within optimal reference limits.
"""
}

class ReportParserService:
    def extract_text_from_pdf(self, pdf_bytes: bytes) -> str:
        try:
            reader = PdfReader(io.BytesIO(pdf_bytes))
            text = "\n".join([page.extract_text() or "" for page in reader.pages])
            return text
        except Exception as e:
            return f"PDF Extraction Error: {str(e)}"

    def extract_text_from_image(self, image_bytes: bytes) -> str:
        try:
            image = Image.open(io.BytesIO(image_bytes))
            return pytesseract.image_to_string(image)
        except Exception as e:
            return f"Image OCR Error: {str(e)}"

    def classify_document(self, text: str) -> Tuple[str, str, str]:
        t = text.lower()
        
        # Neuro-imaging / Brain MRI detection
        if any(k in t for k in [
            "mri brain", "brain parenchyma", "neuroradiology", "flair", 
            "diffusion-weighted", "intra-axial mass", "midline shift", 
            "sulcal effacement", "gadolinium", "intracranial neoplasm"
        ]):
            return "brain_mri", "Brain MRI & Neuroradiology Scan", "neuro_oncology"
            
        # Standard laboratory bloodwork
        return "laboratory_bloodwork", "Clinical Laboratory Bloodwork & Metabolic Panel", "cardiometabolic_multi_organ"

    def extract_demographics(self, text: str) -> Dict[str, Any]:
        demo = {
            "name": "Patient",
            "age": 50,
            "gender": "Unknown",
            "mrn": "N/A"
        }
        
        name_match = re.search(r"patient(?:\s+name)?[:\s]+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+)", text)
        if name_match:
            demo["name"] = name_match.group(1).strip()
            
        age_match = re.search(r"age\s*/\s*sex[:\s]+(\d{1,3})\s*(?:years|yrs)?\s*/\s*([a-zA-Z]+)", text, re.IGNORECASE)
        if age_match:
            demo["age"] = int(age_match.group(1))
            demo["gender"] = age_match.group(2).strip().capitalize()
        else:
            a_match = re.search(r"age[:\s]+(\d{1,3})", text, re.IGNORECASE)
            if a_match and int(a_match.group(1)) < 110:
                demo["age"] = int(a_match.group(1))
                
        mrn_match = re.search(r"(?:mrn|patient\s+id)[:\s]+([a-zA-Z0-9\-]+)", text, re.IGNORECASE)
        if mrn_match:
            demo["mrn"] = mrn_match.group(1).strip()

        return demo

    def parse_report_text(self, text: str) -> Tuple[List[ExtractedBiomarker], Dict[str, float]]:
        clean_text = re.sub(r"[ \t]+", " ", text)
        extracted: List[ExtractedBiomarker] = []
        raw: Dict[str, float] = {}

        # 1. Height and Weight extraction for derived BMI
        ht_match = re.search(r"height[:\s]+(\d+(?:\.\d+)?)\s*(?:cm)?", clean_text, re.IGNORECASE)
        wt_match = re.search(r"weight[:\s]+(\d+(?:\.\d+)?)\s*(?:kg)?", clean_text, re.IGNORECASE)
        
        if ht_match and wt_match:
            try:
                ht_cm = float(ht_match.group(1))
                wt_kg = float(wt_match.group(1))
                if ht_cm > 50:
                    bmi_val = round(wt_kg / ((ht_cm / 100.0) ** 2), 1)
                    raw["bmi"] = bmi_val
            except Exception:
                pass

        # 2. Extract standard biomarkers
        for bio in BIOMARKER_DICTIONARY:
            val_found = None
            for pat in bio["patterns"]:
                match = re.search(pat, clean_text, re.IGNORECASE)
                if match:
                    try:
                        candidate = float(match.group(1))
                        if bio["key"] == "age" and (candidate < 10 or candidate > 115):
                            continue
                        val_found = candidate
                        break
                    except ValueError:
                        continue

            if val_found is not None:
                raw[bio["key"]] = val_found

        if "bmi" in raw:
            bmi_v = raw["bmi"]
            status = "Elevated" if bmi_v > 29.9 else "High" if bmi_v > 24.9 else "Normal"
            extracted.append(ExtractedBiomarker(
                name="Body Mass Index (BMI)",
                key="bmi",
                value=bmi_v,
                unit="kg/m²",
                reference_range="18.5 - 24.9 kg/m²",
                status=status,
                status_color="#ef4444" if status == "Elevated" else "#f59e0b" if status == "High" else "#10b981",
                clinical_explanation="Calculated from patient height and weight."
            ))

        for bio in BIOMARKER_DICTIONARY:
            if bio["key"] in raw and bio["key"] != "bmi":
                val = raw[bio["key"]]
                
                if bio["key"] == "hdl":
                    status = "Low" if val < 40.0 else "Optimal"
                    status_color = "#f59e0b" if status == "Low" else "#10b981"
                    explain = "Reduced cardioprotective HDL reverse-cholesterol clearance." if status == "Low" else "Cardioprotective HDL concentration."
                elif bio["key"] == "egfr":
                    status = "Low" if val < 60.0 else "Normal"
                    status_color = "#ef4444" if status == "Low" else "#10b981"
                    explain = "eGFR <60 indicates compromised renal filtration capacity." if status == "Low" else "Healthy renal filtration rate."
                else:
                    if val > bio["crit_max"]:
                        status = "Critical"
                        status_color = "#ef4444"
                        explain = bio["explain_high"]
                    elif val > bio["ref_max"]:
                        status = "Elevated"
                        status_color = "#f59e0b"
                        explain = bio["explain_high"]
                    elif val < bio["ref_min"]:
                        status = "Low"
                        status_color = "#38bdf8"
                        explain = "Below standard physiological baseline."
                    else:
                        status = "Normal"
                        status_color = "#10b981"
                        explain = bio["explain_normal"]

                extracted.append(ExtractedBiomarker(
                    name=bio["name"],
                    key=bio["key"],
                    value=val,
                    unit=bio["unit"],
                    reference_range=bio["ref_str"],
                    status=status,
                    status_color=status_color,
                    clinical_explanation=explain
                ))

        return extracted, raw

report_parser_service = ReportParserService()

NORTHSTAR_STROKE_CT_CTA_REPORT = """
NORTHSTAR UNIVERSITY MEDICAL CENTER
Department of Radiology • Emergency Neuroradiology Service
SYNTHETIC / AI EVALUATION REPORT
Fabricated patient and fabricated imaging findings. Not a real hospital record and not for clinical use.

Patient: Marcus Bennett (Synthetic)   MRN: NSMC-DEMO-91357
Age / Sex: 68 years / Male            Study Date: 16 Aug 2026
Accession: CT-CTA-26-0816-204          Priority: Emergency / STAT
Exam: Noncontrast CT Head + CT Angiography Head/Neck Status: Final / Synthetic

Clinical History / Indication
---------------------------------------------------------------------------------
Sudden onset left facial weakness, left arm and leg weakness, and expressive language difficulty. 
Last known well approximately 90 minutes before imaging. Emergency neurologic evaluation requested.

Technique
---------------------------------------------------------------------------------
Noncontrast axial CT of the head was obtained from skull base through vertex. 
CT angiography of the head and neck was performed following intravenous iodinated contrast administration 
with multiplanar and maximum-intensity-projection reformations. Images were reviewed using brain, soft-tissue, 
and angiographic windows.

Comparison
---------------------------------------------------------------------------------
No prior neuroimaging is available for comparison.

Findings
---------------------------------------------------------------------------------
Brain Parenchyma: Subtle loss of gray-white matter differentiation involving the right insular cortex and right frontal opercular region, with additional early hypoattenuation in the right basal ganglia. No focal intraparenchymal hyperdensity to suggest acute hemorrhage.
Mass Effect: Mild effacement of the right sylvian fissure and adjacent cortical sulci. No significant midline shift or downward herniation.
Ventricles / Extra-axial Spaces: Ventricular size and configuration are within expected limits. No extra-axial hemorrhage or collection.
CTA — Intracranial: Abrupt non-opacification of the right middle cerebral artery M1 segment with distal reconstitution of a limited number of M2 branches. Reduced distal arterial opacification is present in the right MCA territory.
CTA — Cervical Vessels: Mild atherosclerotic plaque at the carotid bifurcations without hemodynamically significant cervical internal carotid stenosis. Vertebral arteries are patent.
Posterior Circulation: Basilar artery and posterior cerebral arteries are patent without focal large-vessel occlusion.
Calvarium / Soft Tissues: No acute osseous abnormality identified.

Impression
---------------------------------------------------------------------------------
1. Early parenchymal attenuation and gray-white differentiation abnormality in the right insular, frontal opercular, and basal ganglia regions.
2. Abrupt right M1 segment non-opacification with reduced distal right MCA territory arterial filling.
3. No acute intracranial hemorrhage or significant midline shift identified on this examination.
4. Findings are highly concerning for an acute vascular neurologic event (Acute Ischemic Stroke with Right M1 Large Vessel Occlusion). Correlate immediately with neurologic examination and time of symptom onset.
"""
