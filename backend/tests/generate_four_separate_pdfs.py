import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def get_base_styles():
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1, # Center
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=4
    )

    banner_style = ParagraphStyle(
        'Banner',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#b91c1c'),
        alignment=1,
        spaceAfter=5
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=5,
        spaceAfter=3,
        borderPadding=(1, 3, 1, 3)
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
        textColor=colors.HexColor('#334155')
    )

    cell_abnormal = ParagraphStyle(
        'CellAbnormal',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=9.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#b91c1c')
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10.5,
        textColor=colors.HexColor('#1e293b')
    )

    return {
        'title': title_style,
        'subtitle': subtitle_style,
        'banner': banner_style,
        'heading': section_heading,
        'cell_bold': cell_bold,
        'cell_normal': cell_normal,
        'cell_abnormal': cell_abnormal,
        'body': body_style
    }

def build_patient_table(uhid, dept, acuity_text, s):
    pt_data = [
        [
            Paragraph("<b>Patient Name:</b> Sivaathithya", s['cell_normal']),
            Paragraph("<b>Age / Sex:</b> 46 Years / Male", s['cell_normal']),
            Paragraph(f"<b>UHID / MRN:</b> {uhid}", s['cell_normal'])
        ],
        [
            Paragraph("<b>Evaluation Date:</b> 20/02/2027", s['cell_normal']),
            Paragraph(f"<b>Clinic / Department:</b> {dept}", s['cell_normal']),
            Paragraph(f"<b>Acuity Status:</b> <font color='#b91c1c'><b>{acuity_text}</b></font>", s['cell_normal'])
        ],
        [
            Paragraph("<b>Specimen:</b> Fasting Venous Serum", s['cell_normal']),
            Paragraph("<b>Fasting Status:</b> 12-Hour Overnight Fasting", s['cell_normal']),
            Paragraph("<b>Clinical Verification:</b> Automated CDS Screened", s['cell_normal'])
        ]
    ]
    t_pt = Table(pt_data, colWidths=[180, 190, 170])
    t_pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    return t_pt

table_style_common = TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
    ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
    ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ('TOPPADDING', (0,0), (-1,-1), 2.5),
    ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
    ('LEFTPADDING', (0,0), (-1,-1), 5),
    ('RIGHTPADDING', (0,0), (-1,-1), 5),
])

# =========================================================================
# 1. HEART DISEASE PDF
# =========================================================================
def generate_heart_report(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=32, bottomMargin=32)
    s = get_base_styles()
    story = []

    story.append(Paragraph("SYNTHETIC CLINICAL DEMONSTRATION RECORD — HEALTHGUARDAI CAPSTONE PROJECT — NOT REAL MEDICAL DATA", s['banner']))
    story.append(Paragraph("METROPOLITAN CARDIOLOGY & VASCULAR INSTITUTES", s['title']))
    story.append(Paragraph("NABH & NABL ACCREDITED TERTIARY CENTER | DIVISION OF CLINICAL CARDIOLOGY & LIPIDOLOGY<br/>28/A Medical Square, Metro Vihar, New Delhi - 110001 | Phone: 011-2098-7654 | www.metro-cardio-cds.org", s['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=5))

    story.append(Paragraph("PATIENT & CLINICAL REVIEW DETAILS", s['heading']))
    story.append(build_patient_table("METRO-CARD-1042", "Department of Cardiology & Vascular Medicine", "HIGH CARDIAC RISK (STAGE 2 HTN & DYSLIPIDEMIA)", s))
    story.append(Spacer(1, 4))

    story.append(Paragraph("CLINICAL PRESENTATION & CARDIAC HISTORY", s['heading']))
    story.append(Paragraph(
        "Patient presents with a 3-month history of exertional substernal chest discomfort, breathlessness on moderate exertion, "
        "and persistent occipital headaches upon waking. Physical examination confirms elevated arterial blood pressure. "
        "Comprehensive cardiovascular hemodynamic profile and fasting lipid electrophoresis requested to evaluate coronary artery disease risk.",
        s['body']
    ))
    story.append(Spacer(1, 4))

    headers = [
        Paragraph("<b>Biomarker / Investigation</b>", s['cell_bold']),
        Paragraph("<b>Observed Result</b>", s['cell_bold']),
        Paragraph("<b>Target Reference Range</b>", s['cell_bold']),
        Paragraph("<b>Clinical Flag / Interpretation</b>", s['cell_bold'])
    ]

    cardio_rows = [
        headers,
        [Paragraph("Blood Pressure (Resting Arterial)", s['cell_normal']), Paragraph("<b>164 / 102 mmHg</b>", s['cell_abnormal']), Paragraph("< 120 / < 80 mmHg", s['cell_normal']), Paragraph("<font color='#b91c1c'>Stage 2 Severe Hypertension</font>", s['cell_normal'])],
        [Paragraph("Resting Heart Rate", s['cell_normal']), Paragraph("<b>92 bpm</b>", s['cell_abnormal']), Paragraph("60 - 100 bpm", s['cell_normal']), Paragraph("<font color='#d97706'>Borderline resting tachycardia</font>", s['cell_normal'])],
        [Paragraph("Total Cholesterol", s['cell_normal']), Paragraph("<b>268 mg/dL</b>", s['cell_abnormal']), Paragraph("< 200 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Elevated / Severe Hypercholesterolemia</font>", s['cell_normal'])],
        [Paragraph("LDL Cholesterol (Atherogenic)", s['cell_normal']), Paragraph("<b>184 mg/dL</b>", s['cell_abnormal']), Paragraph("< 100 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Very High / Accelerated Plaque Risk</font>", s['cell_normal'])],
        [Paragraph("HDL Cholesterol (Cardioprotective)", s['cell_normal']), Paragraph("<b>32 mg/dL</b>", s['cell_abnormal']), Paragraph("> 40 mg/dL (Male)", s['cell_normal']), Paragraph("<font color='#b91c1c'>Low / Subnormal Cardioprotection</font>", s['cell_normal'])],
        [Paragraph("Serum Triglycerides", s['cell_normal']), Paragraph("<b>286 mg/dL</b>", s['cell_abnormal']), Paragraph("< 150 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Marked Hypertriglyceridemia</font>", s['cell_normal'])],
        [Paragraph("hs-CRP (High-Sensitivity C-Reactive Protein)", s['cell_normal']), Paragraph("<b>4.8 mg/L</b>", s['cell_abnormal']), Paragraph("< 1.0 mg/L", s['cell_normal']), Paragraph("<font color='#b91c1c'>High Vascular Atherogenic Inflammation</font>", s['cell_normal'])],
        [Paragraph("Resting 12-Lead ECG Findings", s['cell_normal']), Paragraph("<b>ST Depression 1.8 mm (V4-V6)</b>", s['cell_abnormal']), Paragraph("Normal sinus, no ST-T change", s['cell_normal']), Paragraph("<font color='#b91c1c'>Subendocardial myocardial ischemia</font>", s['cell_normal'])],
        [Paragraph("10-Year ASCVD Risk Score", s['cell_normal']), Paragraph("<b>24.8 %</b>", s['cell_abnormal']), Paragraph("< 7.5 % (Low Risk)", s['cell_normal']), Paragraph("<font color='#b91c1c'>High Atherosclerotic Cardiovascular Risk</font>", s['cell_normal'])]
    ]
    t_cardio = Table(cardio_rows, colWidths=[170, 100, 120, 150])
    t_cardio.setStyle(table_style_common)
    story.append(t_cardio)
    story.append(Spacer(1, 4))

    story.append(Paragraph("CARDIOLOGY ASSESSMENT & CLINICAL MANAGEMENT PLAN", s['heading']))
    story.append(Paragraph(
        "<b>Clinical Impression:</b> Primary Cardiovascular Disease Profile: <b>Stage 2 Essential Hypertension (164/102 mmHg)</b> "
        "concomitant with <b>Severe Mixed Atherogenic Dyslipidemia (Total Chol 268 mg/dL, LDL 184 mg/dL, Triglycerides 286 mg/dL)</b> and ECG evidence of subendocardial strain.<br/><br/>"
        "<b>Recommended Clinical Interventions:</b><br/>"
        "1. Immediate initiation of combination antihypertensive therapy (e.g. ARB + DHP-CCB) to achieve target BP &lt; 130/80 mmHg.<br/>"
        "2. High-intensity statin therapy (Atorvastatin 40-80 mg or Rosuvastatin 20-40 mg) targeting &gt;50% LDL reduction.<br/>"
        "3. Transthoracic echocardiogram and treadmill exercise stress testing (TMT) to evaluate functional coronary reserve.<br/>"
        "4. Strict dietary sodium restriction (&lt;1,500 mg/day), regular aerobic exercise, and smoking/alcohol cessation.",
        s['body']
    ))
    story.append(Spacer(1, 6))

    sig_data = [
        [
            Paragraph("<b>Dr. Vikram Menon, MD, DM</b><br/>Senior Consultant Cardiologist<br/>Reg No: DMC-55102", s['cell_normal']),
            Paragraph("<b>Dr. Rajiv Khurana, MD, DNB</b><br/>Director of Interventional Cardiology<br/>Reg No: DMC-48291", s['cell_normal']),
            Paragraph("<b>Dr. R. K. Sharma, MD</b><br/>Head of Diagnostic Pathology<br/>Reg No: DMC-41203", s['cell_normal'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94a3b8')), ('TOPPADDING', (0,0), (-1,-1), 3)]))
    story.append(t_sig)

    doc.build(story)
    print(f"Generated: {output_path}")

# =========================================================================
# 2. CHRONIC KIDNEY DISEASE (CKD) PDF
# =========================================================================
def generate_kidney_report(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=32, bottomMargin=32)
    s = get_base_styles()
    story = []

    story.append(Paragraph("SYNTHETIC CLINICAL DEMONSTRATION RECORD — HEALTHGUARDAI CAPSTONE PROJECT — NOT REAL MEDICAL DATA", s['banner']))
    story.append(Paragraph("METROPOLITAN NEPHROLOGY & RENAL RESEARCH INSTITUTE", s['title']))
    story.append(Paragraph("NABH & NABL ACCREDITED TERTIARY CENTER | DIVISION OF CLINICAL NEPHROLOGY & DIALYSIS<br/>28/A Medical Square, Metro Vihar, New Delhi - 110001 | Phone: 011-2098-7654 | www.metro-nephro-cds.org", s['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=5))

    story.append(Paragraph("PATIENT & CLINICAL REVIEW DETAILS", s['heading']))
    story.append(build_patient_table("METRO-NEPH-2081", "Department of Nephrology & Renal Medicine", "CRITICAL RENAL DECLINE (CKD STAGE G4 A3)", s))
    story.append(Spacer(1, 4))

    story.append(Paragraph("CLINICAL PRESENTATION & RENAL HISTORY", s['heading']))
    story.append(Paragraph(
        "Patient presents with a 4-month history of progressive bilateral lower extremity edema, foamy urine, anorexia, "
        "morning nausea, and profound fatigue. No gross hematuria or flank colic. Clinical examination reveals 2+ pitting pedal edema. "
        "Comprehensive renal function panel and spot urine albumin-to-creatinine ratio ordered to stage chronic kidney disease.",
        s['body']
    ))
    story.append(Spacer(1, 4))

    headers = [
        Paragraph("<b>Biomarker / Investigation</b>", s['cell_bold']),
        Paragraph("<b>Observed Result</b>", s['cell_bold']),
        Paragraph("<b>Target Reference Range</b>", s['cell_bold']),
        Paragraph("<b>Clinical Flag / Interpretation</b>", s['cell_bold'])
    ]

    renal_rows = [
        headers,
        [Paragraph("Serum Creatinine", s['cell_normal']), Paragraph("<b>2.60 mg/dL</b>", s['cell_abnormal']), Paragraph("0.70 - 1.30 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Markedly elevated / Severe azotemia</font>", s['cell_normal'])],
        [Paragraph("Estimated GFR (eGFR, CKD-EPI 2021)", s['cell_normal']), Paragraph("<b>28 mL/min/1.73m²</b>", s['cell_abnormal']), Paragraph("> 90 mL/min/1.73m²", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severely Decreased (CKD Stage G4)</font>", s['cell_normal'])],
        [Paragraph("Blood Urea Nitrogen (BUN)", s['cell_normal']), Paragraph("<b>48 mg/dL</b>", s['cell_abnormal']), Paragraph("7 - 20 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severe azotemic waste retention</font>", s['cell_normal'])],
        [Paragraph("Urine Albumin-Creatinine Ratio (uACR)", s['cell_normal']), Paragraph("<b>580 mg/g</b>", s['cell_abnormal']), Paragraph("< 30 mg/g", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severely Increased / A3 Macroalbuminuria</font>", s['cell_normal'])],
        [Paragraph("Urine Protein (Dipstick)", s['cell_normal']), Paragraph("<b>3+</b>", s['cell_abnormal']), Paragraph("Negative", s['cell_normal']), Paragraph("<font color='#b91c1c'>Heavy Glomerular Protein Leakage</font>", s['cell_normal'])],
        [Paragraph("Serum Potassium", s['cell_normal']), Paragraph("<b>5.4 mmol/L</b>", s['cell_abnormal']), Paragraph("3.5 - 5.0 mmol/L", s['cell_normal']), Paragraph("<font color='#b91c1c'>Hyperkalemia / Impaired excretion</font>", s['cell_normal'])],
        [Paragraph("Serum Phosphorus", s['cell_normal']), Paragraph("<b>5.2 mg/dL</b>", s['cell_abnormal']), Paragraph("2.5 - 4.5 mg/dL", s['cell_normal']), Paragraph("<font color='#d97706'>Hyperphosphatemia (CKD-MBD)</font>", s['cell_normal'])],
        [Paragraph("Serum Bicarbonate", s['cell_normal']), Paragraph("<b>18 mmol/L</b>", s['cell_abnormal']), Paragraph("22 - 29 mmol/L", s['cell_normal']), Paragraph("<font color='#d97706'>Metabolic Acidosis</font>", s['cell_normal'])],
        [Paragraph("Blood Pressure (Renal Hemodynamics)", s['cell_normal']), Paragraph("<b>138 / 86 mmHg</b>", s['cell_abnormal']), Paragraph("< 120 / < 80 mmHg", s['cell_normal']), Paragraph("<font color='#d97706'>Secondary renal hypertension</font>", s['cell_normal'])]
    ]
    t_renal = Table(renal_rows, colWidths=[170, 100, 120, 150])
    t_renal.setStyle(table_style_common)
    story.append(t_renal)
    story.append(Spacer(1, 4))

    story.append(Paragraph("NEPHROLOGY ASSESSMENT & CLINICAL MANAGEMENT PLAN", s['heading']))
    story.append(Paragraph(
        "<b>Clinical Impression:</b> <b>Chronic Kidney Disease, KDIGO Stage G4 with Severely Increased Albuminuria (Stage G4 A3)</b>. "
        "Severe decline in glomerular filtration rate (eGFR 28 mL/min/1.73m²) accompanied by azotemia, hyperkalemia, and metabolic acidosis.<br/><br/>"
        "<b>Recommended Clinical Interventions:</b><br/>"
        "1. Immediate medication reconciliation: strictly avoid all NSAIDs (ibuprofen, diclofenac) and nephrotoxic contrast agents.<br/>"
        "2. Dietary potassium restriction (&lt;2,000 mg/day) and low-sodium protocol (&lt;1,800 mg/day); start oral sodium bicarbonate for acidosis.<br/>"
        "3. Bilateral renal duplex ultrasound to evaluate parenchymal thickness and exclude bilateral renal artery stenosis or urinary tract obstruction.<br/>"
        "4. Urgent outpatient Nephrology consultation for renal replacement therapy (RRT) education and arteriovenous fistula (AVF) vascular planning.",
        s['body']
    ))
    story.append(Spacer(1, 6))

    sig_data = [
        [
            Paragraph("<b>Dr. Arvind Deshmukh, MD, DM</b><br/>Senior Consultant Nephrologist<br/>Reg No: DMC-68421", s['cell_normal']),
            Paragraph("<b>Dr. Meera Nambiar, MD, DNB</b><br/>Consultant Nephrologist & Transplant Physician<br/>Reg No: DMC-72109", s['cell_normal']),
            Paragraph("<b>Dr. R. K. Sharma, MD</b><br/>Head of Diagnostic Pathology<br/>Reg No: DMC-41203", s['cell_normal'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94a3b8')), ('TOPPADDING', (0,0), (-1,-1), 3)]))
    story.append(t_sig)

    doc.build(story)
    print(f"Generated: {output_path}")

# =========================================================================
# 3. HEPATIC / LIVER DISEASE PDF
# =========================================================================
def generate_liver_report(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=32, bottomMargin=32)
    s = get_base_styles()
    story = []

    story.append(Paragraph("SYNTHETIC CLINICAL DEMONSTRATION RECORD — HEALTHGUARDAI CAPSTONE PROJECT — NOT REAL MEDICAL DATA", s['banner']))
    story.append(Paragraph("METROPOLITAN INSTITUTE OF HEPATOLOGY & DIGESTIVE SCIENCES", s['title']))
    story.append(Paragraph("NABH & NABL ACCREDITED TERTIARY CENTER | DEPARTMENT OF CLINICAL HEPATOLOGY<br/>28/A Medical Square, Metro Vihar, New Delhi - 110001 | Phone: 011-2098-7654 | www.metro-liver-cds.org", s['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=5))

    story.append(Paragraph("PATIENT & CLINICAL REVIEW DETAILS", s['heading']))
    story.append(build_patient_table("METRO-HEP-3094", "Department of Hepatology & Gastroenterology", "CRITICAL HEPATIC STRESS (MARKED TRANSAMINITIS & CHOLESTASIS)", s))
    story.append(Spacer(1, 4))

    story.append(Paragraph("CLINICAL PRESENTATION & HEPATOLOGY HISTORY", s['heading']))
    story.append(Paragraph(
        "Patient presents with a 3-week history of mild scleral icterus, dark amber urine, right upper quadrant heaviness, "
        "generalized pruritus, and unexplained lethargy. No history of chronic heavy alcohol use, intravenous drug abuse, or acute viral exposure. "
        "Clinical examination reveals mild icteric sclerae and right hypochondriac tenderness without overt ascites. Comprehensive liver function panel ordered.",
        s['body']
    ))
    story.append(Spacer(1, 4))

    headers = [
        Paragraph("<b>Biomarker / Investigation</b>", s['cell_bold']),
        Paragraph("<b>Observed Result</b>", s['cell_bold']),
        Paragraph("<b>Target Reference Range</b>", s['cell_bold']),
        Paragraph("<b>Clinical Flag / Interpretation</b>", s['cell_bold'])
    ]

    liver_rows = [
        headers,
        [Paragraph("ALT / SGPT (Alanine Aminotransferase)", s['cell_normal']), Paragraph("<b>165 U/L</b>", s['cell_abnormal']), Paragraph("7 - 56 U/L", s['cell_normal']), Paragraph("<font color='#b91c1c'>Marked transaminitis (&gt;3x ULN)</font>", s['cell_normal'])],
        [Paragraph("AST / SGOT (Aspartate Aminotransferase)", s['cell_normal']), Paragraph("<b>142 U/L</b>", s['cell_abnormal']), Paragraph("10 - 40 U/L", s['cell_normal']), Paragraph("<font color='#b91c1c'>Markedly elevated hepatocellular enzyme</font>", s['cell_normal'])],
        [Paragraph("Total Bilirubin", s['cell_normal']), Paragraph("<b>3.4 mg/dL</b>", s['cell_abnormal']), Paragraph("0.2 - 1.2 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Overt Hyperbilirubinemia (Jaundice)</font>", s['cell_normal'])],
        [Paragraph("Direct Bilirubin (Conjugated)", s['cell_normal']), Paragraph("<b>1.6 mg/dL</b>", s['cell_abnormal']), Paragraph("0.0 - 0.3 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Conjugated excretory impairment</font>", s['cell_normal'])],
        [Paragraph("Alkaline Phosphatase (ALP)", s['cell_normal']), Paragraph("<b>268 U/L</b>", s['cell_abnormal']), Paragraph("44 - 147 U/L", s['cell_normal']), Paragraph("<font color='#b91c1c'>Marked cholestatic canalicular pattern</font>", s['cell_normal'])],
        [Paragraph("Gamma-Glutamyl Transferase (GGT)", s['cell_normal']), Paragraph("<b>185 U/L</b>", s['cell_abnormal']), Paragraph("9 - 48 U/L", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severe biliary epithelial stress</font>", s['cell_normal'])],
        [Paragraph("Serum Albumin", s['cell_normal']), Paragraph("<b>2.9 g/dL</b>", s['cell_abnormal']), Paragraph("3.5 - 5.0 g/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Hypoalbuminemia / Synthetic deficit</font>", s['cell_normal'])],
        [Paragraph("Total Serum Protein", s['cell_normal']), Paragraph("<b>5.8 g/dL</b>", s['cell_abnormal']), Paragraph("6.0 - 8.3 g/dL", s['cell_normal']), Paragraph("<font color='#d97706'>Subnormal total protein synthesis</font>", s['cell_normal'])],
        [Paragraph("Prothrombin Time (PT / INR)", s['cell_normal']), Paragraph("<b>1.35 INR</b>", s['cell_abnormal']), Paragraph("0.85 - 1.15 INR", s['cell_normal']), Paragraph("<font color='#d97706'>Mild coagulopathy / Prolonged INR</font>", s['cell_normal'])]
    ]
    t_liver = Table(liver_rows, colWidths=[170, 100, 120, 150])
    t_liver.setStyle(table_style_common)
    story.append(t_liver)
    story.append(Spacer(1, 4))

    story.append(Paragraph("HEPATOLOGY ASSESSMENT & CLINICAL MANAGEMENT PLAN", s['heading']))
    story.append(Paragraph(
        "<b>Clinical Impression:</b> <b>Active Hepatocellular Injury with Cholestatic Pattern (Transaminitis & Hyperbilirubinemia)</b>. "
        "Marked elevation of alanine aminotransferase (ALT 165 U/L, >3x ULN) and conjugated bilirubin (Direct 1.6 mg/dL) with impaired hepatic synthesis (Albumin 2.9 g/dL).<br/><br/>"
        "<b>Recommended Clinical Interventions:</b><br/>"
        "1. Immediate abdominal ultrasound with Doppler imaging and transient liver elastography (FibroScan) to assess liver stiffness.<br/>"
        "2. Complete viral hepatitis serology panel (HBsAg, Anti-HCV, IgM Anti-HAV, IgM Anti-HEV) and autoimmune liver screen (ANA, ASMA, IgG).<br/>"
        "3. Immediate medication stewardship: review all prescription drugs, over-the-counter agents, and herbal supplements for hepatotoxicity.<br/>"
        "4. Strict alcohol abstinence; urgent outpatient Hepatology review within 5-7 days.",
        s['body']
    ))
    story.append(Spacer(1, 6))

    sig_data = [
        [
            Paragraph("<b>Dr. Sunita Rao, MD, DM</b><br/>Senior Consultant Hepatologist<br/>Reg No: DMC-74195", s['cell_normal']),
            Paragraph("<b>Dr. Ananya Mukherjee, MD, DNB</b><br/>Consultant Gastroenterologist<br/>Reg No: DMC-69832", s['cell_normal']),
            Paragraph("<b>Dr. R. K. Sharma, MD</b><br/>Head of Diagnostic Pathology<br/>Reg No: DMC-41203", s['cell_normal'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94a3b8')), ('TOPPADDING', (0,0), (-1,-1), 3)]))
    story.append(t_sig)

    doc.build(story)
    print(f"Generated: {output_path}")

# =========================================================================
# 4. TYPE 2 DIABETES MELLITUS PDF
# =========================================================================
def generate_diabetes_report(output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=32, bottomMargin=32)
    s = get_base_styles()
    story = []

    story.append(Paragraph("SYNTHETIC CLINICAL DEMONSTRATION RECORD — HEALTHGUARDAI CAPSTONE PROJECT — NOT REAL MEDICAL DATA", s['banner']))
    story.append(Paragraph("METROPOLITAN DIABETES, ENDOCRINOLOGY & METABOLISM CENTER", s['title']))
    story.append(Paragraph("NABH & NABL ACCREDITED TERTIARY CENTER | DEPARTMENT OF CLINICAL ENDOCRINOLOGY<br/>28/A Medical Square, Metro Vihar, New Delhi - 110001 | Phone: 011-2098-7654 | www.metro-diabetes-cds.org", s['subtitle']))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=5))

    story.append(Paragraph("PATIENT & CLINICAL REVIEW DETAILS", s['heading']))
    story.append(build_patient_table("METRO-ENDO-4098", "Department of Endocrinology & Metabolism", "CRITICAL HYPERGLYCEMIA (OVERT TYPE 2 DIABETES)", s))
    story.append(Spacer(1, 4))

    story.append(Paragraph("CLINICAL PRESENTATION & ENDOCRINE HISTORY", s['heading']))
    story.append(Paragraph(
        "Patient presents with a 2-month history of classic polydipsia (excessive thirst), marked polyuria (nocturia x 4), "
        "unintentional 4 kg weight loss despite polyphagia, blurred vision, and chronic fatigue. Family history positive for Type 2 Diabetes in both parents. "
        "Fasting laboratory panel ordered to confirm diagnosis, evaluate beta-cell reserve, and assess glycemic control.",
        s['body']
    ))
    story.append(Spacer(1, 4))

    headers = [
        Paragraph("<b>Biomarker / Investigation</b>", s['cell_bold']),
        Paragraph("<b>Observed Result</b>", s['cell_bold']),
        Paragraph("<b>Target Reference Range</b>", s['cell_bold']),
        Paragraph("<b>Clinical Flag / Interpretation</b>", s['cell_bold'])
    ]

    diab_rows = [
        headers,
        [Paragraph("Fasting Plasma Glucose (FBS)", s['cell_normal']), Paragraph("<b>215 mg/dL</b>", s['cell_abnormal']), Paragraph("70 - 99 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Diagnostic of Overt Diabetes (&gt;=126 mg/dL)</font>", s['cell_normal'])],
        [Paragraph("Glycated Hemoglobin (HbA1c)", s['cell_normal']), Paragraph("<b>10.4 %</b>", s['cell_abnormal']), Paragraph("< 5.7 % (Normal)", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severely Uncontrolled Diabetes (&gt;=6.5%)</font>", s['cell_normal'])],
        [Paragraph("Postprandial Glucose (PPBS 2hr)", s['cell_normal']), Paragraph("<b>328 mg/dL</b>", s['cell_abnormal']), Paragraph("< 140 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severe Postprandial Hyperglycemia (&gt;=200)</font>", s['cell_normal'])],
        [Paragraph("Fasting Serum Insulin", s['cell_normal']), Paragraph("<b>28.5 uIU/mL</b>", s['cell_abnormal']), Paragraph("2.6 - 24.9 uIU/mL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Hyperinsulinemia / Severe Insulin Resistance</font>", s['cell_normal'])],
        [Paragraph("HOMA-IR (Insulin Resistance Index)", s['cell_normal']), Paragraph("<b>15.1</b>", s['cell_abnormal']), Paragraph("< 2.0 (Normal)", s['cell_normal']), Paragraph("<font color='#b91c1c'>Severe peripheral tissue insulin resistance</font>", s['cell_normal'])],
        [Paragraph("Urine Glucose (Dipstick)", s['cell_normal']), Paragraph("<b>3+</b>", s['cell_abnormal']), Paragraph("Negative", s['cell_normal']), Paragraph("<font color='#b91c1c'>Marked Glucosuria (Marked glucosuria secondary to severe hyperglycemia)</font>", s['cell_normal'])],
        [Paragraph("Urine Ketones (Acetoacetate)", s['cell_normal']), Paragraph("<b>Negative</b>", s['cell_normal']), Paragraph("Negative", s['cell_normal']), Paragraph("No diabetic ketoacidosis (DKA)", s['cell_normal'])],
        [Paragraph("Estimated Average Glucose (eAG)", s['cell_normal']), Paragraph("<b>252 mg/dL</b>", s['cell_abnormal']), Paragraph("< 126 mg/dL", s['cell_normal']), Paragraph("<font color='#b91c1c'>Sustained 3-month high glycemic burden</font>", s['cell_normal'])],
        [Paragraph("C-Peptide (Fasting)", s['cell_normal']), Paragraph("<b>3.8 ng/mL</b>", s['cell_abnormal']), Paragraph("1.1 - 4.4 ng/mL", s['cell_normal']), Paragraph("<font color='#d97706'>Preserved beta-cell secretory capacity</font>", s['cell_normal'])]
    ]
    t_diab = Table(diab_rows, colWidths=[170, 100, 120, 150])
    t_diab.setStyle(table_style_common)
    story.append(t_diab)
    story.append(Spacer(1, 4))

    story.append(Paragraph("ENDOCRINOLOGY ASSESSMENT & CLINICAL MANAGEMENT PLAN", s['heading']))
    story.append(Paragraph(
        "<b>Clinical Impression:</b> <b>Newly Diagnosed, Poorly Controlled Type 2 Diabetes Mellitus with Severe Hyperglycemia (HbA1c 10.4%, Fasting Glucose 215 mg/dL)</b>. "
        "Marked glucosuria and symptomatic hyperosmolar state without ketosis.<br/><br/>"
        "<b>Recommended Clinical Interventions:</b><br/>"
        "1. Immediate initiation of dual combination antihyperglycemic pharmacotherapy (Metformin + SGLT2 inhibitor or GLP-1 RA).<br/>"
        "2. Home blood glucose monitoring (SMBG) protocol: fasting and 2-hour post-meal testing 3 times weekly.<br/>"
        "3. Baseline dilated eye fundus examination to screen for early diabetic retinopathy.<br/>"
        "4. Referral to a certified diabetes educator (CDE) for carbohydrate counting, glycemic index education, and lifestyle intervention.",
        s['body']
    ))
    story.append(Spacer(1, 6))

    sig_data = [
        [
            Paragraph("<b>Dr. Pooja Nair, MD, DM</b><br/>Senior Consultant Endocrinologist<br/>Reg No: DMC-61984", s['cell_normal']),
            Paragraph("<b>Dr. Harish Sethi, MD, DNB</b><br/>Consultant Diabetologist<br/>Reg No: DMC-53902", s['cell_normal']),
            Paragraph("<b>Dr. R. K. Sharma, MD</b><br/>Head of Diagnostic Pathology<br/>Reg No: DMC-41203", s['cell_normal'])
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94a3b8')), ('TOPPADDING', (0,0), (-1,-1), 3)]))
    story.append(t_sig)

    doc.build(story)
    print(f"Generated: {output_path}")

def generate_all():
    tasks = [
        ("Heart Disease", "siva_heart_disease_report.pdf", generate_heart_report),
        ("Chronic Kidney Disease", "siva_kidney_disease_report.pdf", generate_kidney_report),
        ("Hepatic / Liver Disease", "siva_liver_disease_report.pdf", generate_liver_report),
        ("Type 2 Diabetes", "siva_diabetes_report.pdf", generate_diabetes_report)
    ]
    
    downloads_dir = r"c:\Users\sivaa\Downloads"
    local_dir = r"backend\tests"

    for name, filename, func in tasks:
        local_target = os.path.join(local_dir, filename)
        func(local_target)
        downloads_target = os.path.join(downloads_dir, filename)
        try:
            shutil.copyfile(local_target, downloads_target)
            print(f"Copied {name} to: {downloads_target}")
        except Exception as e:
            print(f"Could not copy {name} to Downloads: {e}")

if __name__ == "__main__":
    generate_all()
