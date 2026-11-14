"""
generate_samples.py
===================
Generates realistic clinical follow-up PDF test reports designed to test
HealthGuard AI's visit-over-visit comparison engine and LLM narration.

Outputs:
  1. 4_followup_diabetes_recovery_northgate.pdf
     - Pairs with: 3_discharge_summary_diabetes_northgate.pdf
     - Result: FAVORABLE_TRAJECTORY (HbA1c 11.2% -> 6.6%, Glucose 142 -> 96, BP 120/78, LDL 96)
  2. 5_followup_dengue_recovery_halcyon.pdf
     - Pairs with: 1_lab_report_dengue_halcyon_care.pdf
     - Result: Platelet & Liver Recovery (Platelets 68k -> 235k, SGOT/SGPT normalized)
  3. 6_followup_diabetes_relapse_northgate.pdf
     - Pairs with: 3_discharge_summary_diabetes_northgate.pdf
     - Result: ATTENTION_REQUIRED (HbA1c rising to 10.4%, BP 156/96, Creatinine 1.6, LDL 174)
  4. 7_followup_pneumonia_resolution_veridian.pdf
     - Pairs with: 2_radiology_report_pneumonia_veridian.pdf
     - Result: Complete radiological resolution of pneumonia & pleural effusion
"""

import os
import shutil
from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

OUTPUT_DIR = Path(__file__).resolve().parent
DOWNLOADS_DIR = Path(r"c:\Users\sivaa\Downloads")

styles = getSampleStyleSheet()

# Custom styles
style_title = ParagraphStyle(
    "HospitalTitle",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=17,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#7F1D1D")  # Dark maroon
)
style_sub = ParagraphStyle(
    "HospitalSub",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=10,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#4B5563")
)
style_banner = ParagraphStyle(
    "Banner",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=12,
    leading=14,
    alignment=TA_CENTER,
    textColor=colors.HexColor("#1F2937")
)
style_sec_header = ParagraphStyle(
    "SecHeader",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8.5,
    leading=11,
    textColor=colors.white
)
style_cell = ParagraphStyle(
    "Cell",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor("#1F2937")
)
style_cell_bold = ParagraphStyle(
    "CellBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor("#1F2937")
)
style_cell_alert = ParagraphStyle(
    "CellAlert",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor("#B91C1C")
)
style_body = ParagraphStyle(
    "Body",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=8,
    leading=11,
    textColor=colors.HexColor("#1F2937")
)
style_body_bold = ParagraphStyle(
    "BodyBold",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=8,
    leading=11,
    textColor=colors.HexColor("#1F2937")
)


def create_header(hospital_name, address_info, color_hex="#7F1D1D"):
    title_p = Paragraph(f"<font color='{color_hex}'><b>{hospital_name}</b></font>", style_title)
    sub_p = Paragraph(address_info, style_sub)
    watermark_p = Paragraph(
        "<font color='#9CA3AF' size='6'>SYNTHETIC SAMPLE - fictional patient, hospital and clinicians. Not a medical record. For software testing only.</font>",
        style_sub
    )
    return [title_p, Spacer(1, 2), sub_p, Spacer(1, 2), watermark_p, Spacer(1, 6), HRFlowable(width="100%", thickness=1, color=colors.HexColor(color_hex)), Spacer(1, 8)]


# ─────────────────────────────────────────────────────────────────────────────
# REPORT 1: Northgate Follow-Up Diabetes (Recovery / FAVORABLE)
# ─────────────────────────────────────────────────────────────────────────────
def generate_northgate_recovery(filepath):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=28, bottomMargin=28
    )
    story = []

    story.extend(create_header(
        "NORTHGATE MULTISPECIALITY HOSPITAL",
        "22/B, Placeholder Marg, Sample Vihar, New Delhi - 110000 | Ph: 011-0000 0000 | NABH Accredited (sample)",
        "#7F1D1D"
    ))

    story.append(Paragraph("<b>OUTPATIENT COMPREHENSIVE FOLLOW-UP & METABOLIC EVALUATION</b>", style_banner))
    story.append(Spacer(1, 8))

    # Patient info table
    pat_data = [
        [
            Paragraph("<b>Patient Name:</b> Mr. ARJUN MEHTA", style_cell),
            Paragraph("<b>UHID / MRN:</b> NG-0098731", style_cell),
            Paragraph("<b>Evaluation Date:</b> 19/01/2027", style_cell)
        ],
        [
            Paragraph("<b>Age / Sex:</b> 58 Years / Male", style_cell),
            Paragraph("<b>IPD Ref:</b> IP/2026/045512 (Discharged 19/10/2026)", style_cell),
            Paragraph("<b>Follow-up Interval:</b> 3 Months Post-Discharge", style_cell)
        ],
        [
            Paragraph("<b>Consultant:</b> Dr. Neha Example, MD, DM (Endocrinology)", style_cell),
            Paragraph("<b>Clinic:</b> Endocrinology & Diabetes Care OPD", style_cell),
            Paragraph("<b>Vitals:</b> BP 120/78 mmHg, BMI 26.2 kg/m²", style_cell_bold)
        ]
    ]
    t_pat = Table(pat_data, colWidths=[200, 180, 160])
    t_pat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9FAFB")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#D1D5DB")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pat)
    story.append(Spacer(1, 10))

    # Clinical Note
    story.append(Table([[Paragraph("CLINICAL INTERVAL HISTORY & ASSESSMENT", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7F1D1D")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 4))
    hist_text = (
        "58-year-old male returns for scheduled 3-month review following October 2026 hospitalisation for severe hyperglycaemia with ketosis. "
        "Patient reports full adherence to prescribed metformin (500mg BID), titrated insulin regimen, and lifestyle modifications (daily 35-min brisk walking, DASH dietary protocol). "
        "Reports zero hypoglycaemic episodes. Fatigue, polyuria, and polydipsia have completely resolved. Weight stable at 75 kg (BMI reduced from 27.8 to 26.2 kg/m²). "
        "Blood pressure on home monitoring averages 120/78 mmHg (on telmisartan 40mg). Dilated fundus examination negative for retinopathy."
    )
    story.append(Paragraph(hist_text, style_body))
    story.append(Spacer(1, 10))

    # Investigation comparison table
    story.append(Table([[Paragraph("LABORATORY MEASUREMENTS (VISIT-OVER-VISIT COMPARISON)", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7F1D1D")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))

    lab_headers = [
        Paragraph("<b>Biomarker / Investigation</b>", style_cell_bold),
        Paragraph("<b>Oct 2026 (Baseline)</b>", style_cell_bold),
        Paragraph("<b>Jan 2027 (Current)</b>", style_cell_bold),
        Paragraph("<b>Trajectory / Delta</b>", style_cell_bold),
        Paragraph("<b>Reference Interval</b>", style_cell_bold),
    ]
    lab_rows = [
        lab_headers,
        [Paragraph("Fasting Plasma Glucose", style_cell_bold), Paragraph("142.0 mg/dL", style_cell_alert), Paragraph("96.0 mg/dL", style_cell_bold), Paragraph("Improved (-46.0 mg/dL)", style_cell_bold), Paragraph("70.0 - 99.0 mg/dL", style_cell)],
        [Paragraph("Glycated Hemoglobin (HbA1c)", style_cell_bold), Paragraph("11.2 %", style_cell_alert), Paragraph("6.6 %", style_cell_bold), Paragraph("Marked Improvement (-4.6 %)", style_cell_bold), Paragraph("< 5.7 % (non-diabetic)", style_cell)],
        [Paragraph("Blood Pressure (Systolic / Diastolic)", style_cell_bold), Paragraph("148/92 mmHg", style_cell_alert), Paragraph("120/78 mmHg", style_cell_bold), Paragraph("Normalized (-28/-14 mmHg)", style_cell_bold), Paragraph("< 120 / < 80 mmHg", style_cell)],
        [Paragraph("Total Cholesterol", style_cell_bold), Paragraph("238.0 mg/dL", style_cell_alert), Paragraph("184.0 mg/dL", style_cell_bold), Paragraph("Optimal (-54.0 mg/dL)", style_cell_bold), Paragraph("< 200.0 mg/dL", style_cell)],
        [Paragraph("LDL Cholesterol (Atherogenic)", style_cell_bold), Paragraph("152.0 mg/dL", style_cell_alert), Paragraph("96.0 mg/dL", style_cell_bold), Paragraph("Target Achieved (-56.0 mg/dL)", style_cell_bold), Paragraph("< 100.0 mg/dL", style_cell)],
        [Paragraph("Serum Creatinine (Preserved)", style_cell_bold), Paragraph("1.0 mg/dL", style_cell), Paragraph("0.9 mg/dL", style_cell_bold), Paragraph("Stable Renal Function", style_cell), Paragraph("0.7 - 1.3 mg/dL", style_cell)],
        [Paragraph("Calculated BMI", style_cell_bold), Paragraph("27.8 kg/m²", style_cell_alert), Paragraph("26.2 kg/m²", style_cell_bold), Paragraph("Reduced (-1.6 kg/m²)", style_cell_bold), Paragraph("18.5 - 24.9 kg/m²", style_cell)],
        [Paragraph("Urine Albumin:Creatinine Ratio", style_cell_bold), Paragraph("84.0 mg/g", style_cell_alert), Paragraph("22.0 mg/g", style_cell_bold), Paragraph("Resolved (<30 mg/g)", style_cell_bold), Paragraph("< 30.0 mg/g", style_cell)],
    ]
    t_lab = Table(lab_rows, colWidths=[170, 95, 95, 105, 75])
    t_lab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_lab)
    story.append(Spacer(1, 10))

    # Recommendations
    story.append(Table([[Paragraph("TREATMENT PLAN & CLINICAL RECOMMENDATIONS", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#7F1D1D")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 4))
    rec_text = (
        "1. Outstanding therapeutic response: Patient has successfully transitioned from severe ketotic decompensation to near-target glycaemic control.<br/>"
        "2. Step-down insulin therapy: Reduce bedtime Glargine to 12 units. Discontinue pre-meal Aspart; continue Metformin SR 500mg BID.<br/>"
        "3. Cardiovascular risk protection: Continue Telmisartan 40mg OD and Atorvastatin 20mg OD (LDL now <100 mg/dL target met).<br/>"
        "4. Follow-up: Repeat HbA1c and renal function panel in 3 months (April 2027)."
    )
    story.append(Paragraph(rec_text, style_body))
    story.append(Spacer(1, 14))

    # Sign-off
    story.append(Paragraph("<b>Dr. Neha Example, MD, DM (Endocrinology)</b><br/><font size='7' color='#6B7280'>Senior Consultant Endocrinologist | Reg No: DMC-000000</font>", style_body))

    doc.build(story)
    print(f"Generated: {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# REPORT 2: Halcyon Care Dengue Recovery (Hematology & Hepatic)
# ─────────────────────────────────────────────────────────────────────────────
def generate_halcyon_recovery(filepath):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=28, bottomMargin=28
    )
    story = []

    story.extend(create_header(
        "HALCYON CARE HOSPITAL",
        "14, Example Road, Sample Nagar, Pune - 411000 | Ph: +91 00000 00000 | lab@halcyon.example | NABL Accredited",
        "#0D9488"  # Teal
    ))

    story.append(Paragraph("<b>DEPARTMENT OF LABORATORY MEDICINE — POST-ACUTE RECOVERY REPORT</b>", style_banner))
    story.append(Spacer(1, 8))

    pat_data = [
        [
            Paragraph("<b>Patient Name:</b> Mr. RAHUL VERMA", style_cell),
            Paragraph("<b>Lab No:</b> HC-24-0219482", style_cell),
            Paragraph("<b>Collected:</b> 28-Oct-2026 09:15 AM", style_cell)
        ],
        [
            Paragraph("<b>Age / Sex:</b> 38 Years / Male", style_cell),
            Paragraph("<b>UHID:</b> HCH0045812", style_cell),
            Paragraph("<b>Report Released:</b> 28-Oct-2026 01:00 PM", style_cell)
        ],
        [
            Paragraph("<b>Referred By:</b> Dr. S. K. Rane (MD Medicine)", style_cell),
            Paragraph("<b>Clinical Phase:</b> Convalescent / Day 8 Post-Fever", style_cell),
            Paragraph("<b>Sample Type:</b> Whole Blood (EDTA), Serum", style_cell)
        ]
    ]
    t_pat = Table(pat_data, colWidths=[200, 170, 170])
    t_pat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F0FDFA")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#5EEAD4")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pat)
    story.append(Spacer(1, 10))

    # Complete Blood Count Table
    story.append(Table([[Paragraph("HAEMATOLOGY: COMPLETE BLOOD COUNT (CBC) — RECOVERY COMPARISON", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0D9488")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))

    cbc_headers = [
        Paragraph("<b>Test Name</b>", style_cell_bold),
        Paragraph("<b>21-Oct-2026 (Acute)</b>", style_cell_bold),
        Paragraph("<b>28-Oct-2026 (Recovery)</b>", style_cell_bold),
        Paragraph("<b>Unit</b>", style_cell_bold),
        Paragraph("<b>Biological Reference Interval</b>", style_cell_bold),
    ]
    cbc_rows = [
        cbc_headers,
        [Paragraph("Platelet Count", style_cell_bold), Paragraph("68,000 [LOW]", style_cell_alert), Paragraph("235,000 [NORMAL]", style_cell_bold), Paragraph("cells/uL", style_cell), Paragraph("150,000 - 410,000", style_cell)],
        [Paragraph("Total Leucocyte Count (TLC)", style_cell_bold), Paragraph("2,900 [LOW]", style_cell_alert), Paragraph("6,400 [NORMAL]", style_cell_bold), Paragraph("cells/uL", style_cell), Paragraph("4,000 - 10,000", style_cell)],
        [Paragraph("Hemoglobin (Hb)", style_cell_bold), Paragraph("15.4", style_cell), Paragraph("14.6", style_cell_bold), Paragraph("g/dL", style_cell), Paragraph("13.0 - 17.0", style_cell)],
        [Paragraph("Packed Cell Volume (PCV / Hct)", style_cell_bold), Paragraph("47.6 [HIGH]", style_cell_alert), Paragraph("43.0 [NORMAL]", style_cell_bold), Paragraph("%", style_cell), Paragraph("40.0 - 50.0", style_cell)],
        [Paragraph("Mean Corpuscular Volume (MCV)", style_cell_bold), Paragraph("89.6", style_cell), Paragraph("88.4", style_cell_bold), Paragraph("fL", style_cell), Paragraph("83.0 - 101.0", style_cell)],
        [Paragraph("Neutrophils / Lymphocytes", style_cell), Paragraph("48% / 41%", style_cell), Paragraph("62% / 30%", style_cell_bold), Paragraph("%", style_cell), Paragraph("40-80% / 20-40%", style_cell)],
    ]
    t_cbc = Table(cbc_rows, colWidths=[170, 105, 110, 55, 100])
    t_cbc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_cbc)
    story.append(Spacer(1, 10))

    # Biochemistry Table
    story.append(Table([[Paragraph("BIOCHEMISTRY: LIVER FUNCTION PROFILE (RESOLVED)", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#0D9488")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))

    lft_rows = [
        [Paragraph("<b>Test Name</b>", style_cell_bold), Paragraph("<b>21-Oct (Acute)</b>", style_cell_bold), Paragraph("<b>28-Oct (Recovery)</b>", style_cell_bold), Paragraph("<b>Unit</b>", style_cell_bold), Paragraph("<b>Reference Interval</b>", style_cell_bold)],
        [Paragraph("SGOT (AST)", style_cell_bold), Paragraph("96.0 [HIGH]", style_cell_alert), Paragraph("32.0 [NORMAL]", style_cell_bold), Paragraph("U/L", style_cell), Paragraph("< 40.0", style_cell)],
        [Paragraph("SGPT (ALT)", style_cell_bold), Paragraph("78.0 [HIGH]", style_cell_alert), Paragraph("35.0 [NORMAL]", style_cell_bold), Paragraph("U/L", style_cell), Paragraph("< 41.0", style_cell)],
        [Paragraph("Serum Bilirubin (Total)", style_cell), Paragraph("0.9", style_cell), Paragraph("0.7", style_cell_bold), Paragraph("mg/dL", style_cell), Paragraph("0.3 - 1.2", style_cell)],
        [Paragraph("Serum Albumin", style_cell), Paragraph("3.9", style_cell), Paragraph("4.2", style_cell_bold), Paragraph("g/dL", style_cell), Paragraph("3.5 - 5.2", style_cell)],
    ]
    t_lft = Table(lft_rows, colWidths=[170, 105, 110, 55, 100])
    t_lft.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#F3F4F6")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F9FAFB")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_lft)
    story.append(Spacer(1, 8))

    # Serology & Impression
    serology_note = (
        "<b>SEROLOGY:</b> Dengue NS1 Antigen: <b>NEGATIVE</b> | Dengue IgM Antibody: <b>POSITIVE</b> (Convalescent titre) | Dengue IgG: Low Reactive.<br/>"
        "<b>CLINICAL IMPRESSION:</b> Complete haematological and biochemical recovery from acute Dengue illness. Thrombocytopenia and transaminitis have fully resolved. "
        "Patient is clinically afebrile, asymptomatic, and discharged from daily outpatient haematology surveillance."
    )
    story.append(Paragraph(serology_note, style_body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Dr. Anita Example, MD (Pathology)</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Dr. Vikram Sample, MD (Microbiology)</b><br/><font size='7' color='#6B7280'>Consultant Pathologist (MMC-000000) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Consultant Microbiologist (MMC-000001)</font>", style_body))

    doc.build(story)
    print(f"Generated: {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# REPORT 3: Northgate Follow-Up Diabetes (Worsening / Relapse / ATTENTION REQUIRED)
# ─────────────────────────────────────────────────────────────────────────────
def generate_northgate_relapse(filepath):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=28, bottomMargin=28
    )
    story = []

    story.extend(create_header(
        "NORTHGATE MULTISPECIALITY HOSPITAL",
        "22/B, Placeholder Marg, Sample Vihar, New Delhi - 110000 | Ph: 011-0000 0000 | NABH Accredited (sample)",
        "#991B1B"
    ))

    story.append(Paragraph("<b>DIABETES CLINICAL REVIEW — METABOLIC DECOMPENSATION WARNING</b>", style_banner))
    story.append(Spacer(1, 8))

    pat_data = [
        [
            Paragraph("<b>Patient Name:</b> Mr. ARJUN MEHTA", style_cell),
            Paragraph("<b>UHID / MRN:</b> NG-0098731", style_cell),
            Paragraph("<b>Evaluation Date:</b> 25/04/2027", style_cell)
        ],
        [
            Paragraph("<b>Age / Sex:</b> 58 Years / Male", style_cell),
            Paragraph("<b>Prior Review Date:</b> 19/01/2027", style_cell),
            Paragraph("<b>Acuity Status:</b> ATTENTION REQUIRED", style_cell_alert)
        ],
        [
            Paragraph("<b>Consultant:</b> Dr. Neha Example, MD, DM", style_cell),
            Paragraph("<b>Clinic:</b> Urgent Endocrinology Review OPD", style_cell),
            Paragraph("<b>Vitals:</b> BP 156/96 mmHg, BMI 28.9 kg/m²", style_cell_alert)
        ]
    ]
    t_pat = Table(pat_data, colWidths=[200, 180, 160])
    t_pat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#FEF2F2")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#FCA5A5")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pat)
    story.append(Spacer(1, 10))

    # History
    story.append(Table([[Paragraph("CLINICAL PRESENTATION & NON-COMPLIANCE HISTORY", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#991B1B")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 4))
    hist_text = (
        "Patient presents with 4-week recurrence of exertional fatigue, bilateral lower limb oedema, nocturia (3-4 times/night), and blurred vision. "
        "Advises cessation of insulin injections 6 weeks ago due to needle anxiety; admits irregular intake of oral metformin and antihypertensive medication. "
        "Significant dietary lapse reported. Weight has rebounded to 81 kg (+6 kg gain, BMI 28.9 kg/m²). Blood pressure elevated at 156/96 mmHg in Stage 2 hypertensive range."
    )
    story.append(Paragraph(hist_text, style_body))
    story.append(Spacer(1, 10))

    # Lab table showing deterioration
    story.append(Table([[Paragraph("LABORATORY MEASUREMENTS — TRAJECTORY WORSENING (COMPARED TO PRIOR VISIT)", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#991B1B")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))

    lab_headers = [
        Paragraph("<b>Biomarker / Investigation</b>", style_cell_bold),
        Paragraph("<b>Jan 2027 (Prior)</b>", style_cell_bold),
        Paragraph("<b>Apr 2027 (Current)</b>", style_cell_bold),
        Paragraph("<b>Trajectory / Delta</b>", style_cell_bold),
        Paragraph("<b>Target Reference</b>", style_cell_bold),
    ]
    lab_rows = [
        lab_headers,
        [Paragraph("Fasting Plasma Glucose", style_cell_bold), Paragraph("96.0 mg/dL", style_cell), Paragraph("218.0 mg/dL", style_cell_alert), Paragraph("Worsened (+122.0 mg/dL)", style_cell_alert), Paragraph("70.0 - 99.0 mg/dL", style_cell)],
        [Paragraph("Glycated Hemoglobin (HbA1c)", style_cell_bold), Paragraph("6.6 %", style_cell), Paragraph("10.4 %", style_cell_alert), Paragraph("Severe Upward Drift (+3.8 %)", style_cell_alert), Paragraph("< 5.7 %", style_cell)],
        [Paragraph("Blood Pressure (Systolic / Diastolic)", style_cell_bold), Paragraph("120/78 mmHg", style_cell), Paragraph("156/96 mmHg", style_cell_alert), Paragraph("Uncontrolled (+36/+18 mmHg)", style_cell_alert), Paragraph("< 120 / < 80 mmHg", style_cell)],
        [Paragraph("Total Cholesterol", style_cell_bold), Paragraph("184.0 mg/dL", style_cell), Paragraph("265.0 mg/dL", style_cell_alert), Paragraph("Elevated (+81.0 mg/dL)", style_cell_alert), Paragraph("< 200.0 mg/dL", style_cell)],
        [Paragraph("LDL Cholesterol (Atherogenic)", style_cell_bold), Paragraph("96.0 mg/dL", style_cell), Paragraph("174.0 mg/dL", style_cell_alert), Paragraph("Atherogenic Surge (+78.0 mg/dL)", style_cell_alert), Paragraph("< 100.0 mg/dL", style_cell)],
        [Paragraph("Serum Creatinine (Preserved)", style_cell_bold), Paragraph("0.9 mg/dL", style_cell), Paragraph("1.6 mg/dL", style_cell_alert), Paragraph("Renal Impairment (+0.7 mg/dL)", style_cell_alert), Paragraph("0.7 - 1.3 mg/dL", style_cell)],
        [Paragraph("Calculated BMI", style_cell_bold), Paragraph("26.2 kg/m²", style_cell), Paragraph("28.9 kg/m²", style_cell_alert), Paragraph("Weight Rebound (+2.7 kg/m²)", style_cell_alert), Paragraph("18.5 - 24.9 kg/m²", style_cell)],
    ]
    t_lab = Table(lab_rows, colWidths=[170, 95, 95, 105, 75])
    t_lab.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#FEE2E2")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#FCA5A5")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#FEF2F2")]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_lab)
    story.append(Spacer(1, 10))

    # Urgent action
    story.append(Table([[Paragraph("URGENT CLINICAL INTERVENTION & ACTION REQUIRED", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#991B1B")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 4))
    action_text = (
        "1. <b>Acute Glycaemic & Renal Deterioration:</b> Markedly elevated HbA1c 10.4% and creatinine rise to 1.6 mg/dL indicate rapid loss of cardiometabolic control.<br/>"
        "2. <b>Immediate Pharmacotherapy Re-initiation:</b> Resume subcutaneous basal-bolus insulin immediately. Metformin dose withheld pending eGFR repeat due to creatinine elevation.<br/>"
        "3. <b>Cardiovascular & Nephroprotection:</b> Escalate Telmisartan to 80mg daily; add Amlodipine 5mg for Stage 2 hypertension. Resume high-intensity Atorvastatin 40mg.<br/>"
        "4. <b>Nephrology & Retinal Referral:</b> Emergent spot urine ACR and renal ultrasonography scheduled within 72 hours."
    )
    story.append(Paragraph(action_text, style_body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Dr. Neha Example, MD, DM (Endocrinology)</b><br/><font size='7' color='#6B7280'>Senior Consultant Endocrinologist | Reg No: DMC-000000</font>", style_body))

    doc.build(story)
    print(f"Generated: {filepath}")


# ─────────────────────────────────────────────────────────────────────────────
# REPORT 4: Veridian Follow-Up CT Thorax (Resolution)
# ─────────────────────────────────────────────────────────────────────────────
def generate_veridian_resolution(filepath):
    doc = SimpleDocTemplate(
        str(filepath),
        pagesize=letter,
        rightMargin=36, leftMargin=36, topMargin=28, bottomMargin=28
    )
    story = []

    story.extend(create_header(
        "VERIDIAN INSTITUTE OF MEDICAL SCIENCES",
        "Department of Radiodiagnosis & Imaging Sciences | 7, Sample Avenue, Example City - 500000 | radiology@veridian.example",
        "#1E3A8A"  # Dark navy blue
    ))

    story.append(Paragraph("<b>FOLLOW-UP RADIOLOGY REPORT — CT THORAX (HRCT) & CHEST X-RAY PA</b>", style_banner))
    story.append(Spacer(1, 8))

    pat_data = [
        [
            Paragraph("<b>Patient Name:</b> Mrs. SUNITA KAPOOR", style_cell),
            Paragraph("<b>MRN / PID:</b> VIMS-RD-7731902", style_cell),
            Paragraph("<b>Accession No:</b> ACC-20261203-0891", style_cell)
        ],
        [
            Paragraph("<b>Age / Gender:</b> 54 Y / Female", style_cell),
            Paragraph("<b>Referring Clinician:</b> Dr. R. Menon (Pulmonology)", style_cell),
            Paragraph("<b>Exam Date / Time:</b> 03-Dec-2026 / 11:20 AM", style_cell)
        ],
        [
            Paragraph("<b>Modality:</b> DX (X-Ray), Low-Dose CT Thorax", style_cell),
            Paragraph("<b>Contrast:</b> Non-contrast volumetric", style_cell),
            Paragraph("<b>Prior Exam Date:</b> 22-Oct-2026 (6-Week Interval)", style_cell)
        ]
    ]
    t_pat = Table(pat_data, colWidths=[200, 180, 160])
    t_pat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EFF6FF")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#93C5FD")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pat)
    story.append(Spacer(1, 10))

    # Clinical History
    story.append(Table([[Paragraph("CLINICAL INDICATION & COMPARISON", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))
    comp_text = (
        "<b>CLINICAL INDICATION:</b> 54-year-old female with known Type 2 Diabetes completed a 14-day antimicrobial course for right lower lobe community-acquired lobar pneumonia and small parapneumonic effusion. "
        "Patient is currently afebrile, asymptomatic with complete resolution of cough, dyspnoea, and pleuritic pain. SpO2 99% on ambient air.<br/>"
        "<b>COMPARISON:</b> Compared with prior volumetric HRCT Thorax and PA chest radiograph dated 22-Oct-2026 (ACC-20261022-0457)."
    )
    story.append(Paragraph(comp_text, style_body))
    story.append(Spacer(1, 10))

    # Findings
    story.append(Table([[Paragraph("FINDINGS & INTERVAL EVOLUTION", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))
    find_text = (
        "<b>Lungs & Airways:</b> Complete resolution of previously visualised dense lobar consolidation and prominent air bronchograms in the posterior and lateral basal segments of the right lower lobe. "
        "Centrilobular tree-in-bud nodules and adjacent ground-glass opacities in the right middle lobe have cleared entirely. No residual scarring, cavitation, or architectural distortion. Left lung remains clear.<br/><br/>"
        "<b>Pleura:</b> The previously noted 14 mm right-sided parapneumonic pleural effusion has resolved completely. Costophrenic angles are acute and clear bilaterally. No pleural thickening or loculation.<br/><br/>"
        "<b>Mediastinum & Lymph Nodes:</b> Previously reactive right hilar and subcarinal lymph nodes (largest was 12 x 9 mm) have regressed to normal sub-centimetre dimensions. Cardiac size and great vessels are normal.<br/><br/>"
        "<b>Chest Radiograph PA:</b> Confirms fully expanded lung fields, clear right costophrenic sulcus, and normal cardiothoracic ratio (CTR 0.44)."
    )
    story.append(Paragraph(find_text, style_body))
    story.append(Spacer(1, 10))

    # Impression
    story.append(Table([[Paragraph("RADIOLOGICAL IMPRESSION (VISIT-OVER-VISIT EVOLUTION)", style_sec_header)]],
                       colWidths=[540], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#1E3A8A")),
                                               ('TOPPADDING', (0,0), (-1,-1), 3), ('BOTTOMPADDING', (0,0), (-1,-1), 3)]))
    story.append(Spacer(1, 3))
    imp_text = (
        "<b>1. COMPLETE RESOLUTION</b> of right lower lobe lobar pneumonia and associated 14 mm parapneumonic effusion compared to prior study of 22-Oct-2026.<br/>"
        "<b>2. Regression of reactive lymphadenopathy;</b> clear parenchyma and normal pleural spaces bilaterally.<br/>"
        "<b>3. No further radiological surveillance required</b> in the absence of recurrent clinical symptoms."
    )
    story.append(Paragraph(imp_text, style_body))
    story.append(Spacer(1, 14))

    story.append(Paragraph("<b>Dr. Kiran Example, MD, DNB (Radiodiagnosis)</b> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; <b>Dr. Meera Sample, MD, FRCR</b><br/><font size='7' color='#6B7280'>Consultant Radiologist (Reg No: 00000-X) &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; Senior Consultant & HOD (Reg No: 00001-Y)</font>", style_body))

    doc.build(story)
    print(f"Generated: {filepath}")


def main():
    print(f"Generating clinical test sample PDFs in {OUTPUT_DIR}...")
    f1 = OUTPUT_DIR / "4_followup_diabetes_recovery_northgate.pdf"
    f2 = OUTPUT_DIR / "5_followup_dengue_recovery_halcyon.pdf"
    f3 = OUTPUT_DIR / "6_followup_diabetes_relapse_northgate.pdf"
    f4 = OUTPUT_DIR / "7_followup_pneumonia_resolution_veridian.pdf"

    generate_northgate_recovery(f1)
    generate_halcyon_recovery(f2)
    generate_northgate_relapse(f3)
    generate_veridian_resolution(f4)

    # Copy to Downloads if accessible
    print(f"Copying to {DOWNLOADS_DIR}...")
    for f in [f1, f2, f3, f4]:
        dest = DOWNLOADS_DIR / f.name
        try:
            shutil.copy2(f, dest)
            print(f"  Copied to {dest}")
        except Exception as e:
            print(f"  Could not copy to {dest}: {e}")

    print("\nAll sample generation complete!")


if __name__ == "__main__":
    main()

