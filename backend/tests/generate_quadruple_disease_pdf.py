import os
import shutil
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_quadruple_disease_report(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=32,
        bottomMargin=32
    )

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
        leading=10,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # 1. Header Banner
    story.append(Paragraph("SYNTHETIC CLINICAL DEMONSTRATION RECORD — HEALTHGUARDAI CAPSTONE PROJECT — NOT REAL MEDICAL DATA", banner_style))
    story.append(Paragraph("METROPOLITAN MULTISPECIALTY MEDICAL CENTER & ADVANCED DIAGNOSTIC INSTITUTE", title_style))
    story.append(Paragraph("NABH & NABL ACCREDITED TERTIARY REFERRAL CENTER | JOINT CLINICAL DECISION SUPPORT EVALUATION<br/>Departments of Cardiology, Endocrinology, Nephrology & Hepatology | 28/A Medical Square, Metro Vihar, New Delhi - 110001", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=5))

    # 2. Patient Details Table
    story.append(Paragraph("PATIENT DEMOGRAPHICS & CLINICAL ORDER DETAILS", section_heading))
    pt_data = [
        [
            Paragraph("<b>Patient Name:</b> Sivaathithya", cell_normal),
            Paragraph("<b>Age / Sex:</b> 46 Years / Male", cell_normal),
            Paragraph("<b>UHID / MRN:</b> METRO-QUAD-4092", cell_normal)
        ],
        [
            Paragraph("<b>Evaluation Date:</b> 20/02/2027", cell_normal),
            Paragraph("<b>Panel Ordered:</b> Comprehensive Quadruple-Organ Biomarker Panel", cell_normal),
            Paragraph("<b>Acuity Status:</b> <font color='#b91c1c'><b>CRITICAL / MULTISYSTEM CDS REVIEW</b></font>", cell_normal)
        ],
        [
            Paragraph("<b>Consultant Team:</b> Cardiology, Endocrinology, Nephrology & Hepatology", cell_normal),
            Paragraph("<b>Specimen:</b> Fasting Venous Serum & Spot Urine", cell_normal),
            Paragraph("<b>Sample Collection:</b> Strict 12-Hour Overnight Fasting", cell_normal)
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
    story.append(t_pt)
    story.append(Spacer(1, 4))

    # 3. Clinical Reason for Comprehensive Evaluation
    story.append(Paragraph("CLINICAL PRESENTATION & REASON FOR MULTISYSTEM SCREENING", section_heading))
    p_hist = Paragraph(
        "46-year-old male with persistent fatigue, bilateral lower extremity pitting edema, exertional dyspnea, polyuria, "
        "and right upper quadrant discomfort. Clinical history of poorly controlled hypertension and impaired glucose tolerance. "
        "Comprehensive quadruple-organ evaluation ordered to simultaneously quantify cardiovascular hemodynamics, atherogenic dyslipidemia, "
        "glycemic control, renal glomerular clearance, and hepatic parenchymal integrity.",
        body_style
    )
    story.append(p_hist)
    story.append(Spacer(1, 4))

    headers = [
        Paragraph("<b>Biomarker / Investigation</b>", cell_bold),
        Paragraph("<b>Observed Result</b>", cell_bold),
        Paragraph("<b>Target Reference Range</b>", cell_bold),
        Paragraph("<b>Clinical Flag / Interpretation</b>", cell_bold)
    ]

    table_style_common = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ])

    # SECTION 1: CARDIOVASCULAR & LIPID PROFILE (HEART DISEASE)
    story.append(Paragraph("1. CARDIOVASCULAR PROFILE & ATHEROGENIC LIPID PANEL (HEART DISEASE AXIS)", section_heading))
    cardio_rows = [
        headers,
        [Paragraph("Blood Pressure (Resting Arterial)", cell_normal), Paragraph("<b>152 / 94 mmHg</b>", cell_abnormal), Paragraph("< 120 / < 80 mmHg", cell_normal), Paragraph("<font color='#b91c1c'>Stage 2 Hypertension</font>", cell_normal)],
        [Paragraph("Total Cholesterol", cell_normal), Paragraph("<b>242 mg/dL</b>", cell_abnormal), Paragraph("< 200 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Elevated / Atherogenic</font>", cell_normal)],
        [Paragraph("LDL Cholesterol (Atherogenic)", cell_normal), Paragraph("<b>162 mg/dL</b>", cell_abnormal), Paragraph("< 100 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>High / Plaque Risk</font>", cell_normal)],
        [Paragraph("HDL Cholesterol (Cardioprotective)", cell_normal), Paragraph("<b>36 mg/dL</b>", cell_abnormal), Paragraph("> 40 mg/dL (Male)", cell_normal), Paragraph("<font color='#d97706'>Low / Subnormal Protection</font>", cell_normal)],
        [Paragraph("Serum Triglycerides", cell_normal), Paragraph("<b>224 mg/dL</b>", cell_abnormal), Paragraph("< 150 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Hypertriglyceridemia</font>", cell_normal)],
        [Paragraph("Resting Heart Rate", cell_normal), Paragraph("<b>84 bpm</b>", cell_normal), Paragraph("60 - 100 bpm", cell_normal), Paragraph("Normal sinus rhythm", cell_normal)]
    ]
    t_cardio = Table(cardio_rows, colWidths=[170, 95, 125, 150])
    t_cardio.setStyle(table_style_common)
    story.append(t_cardio)
    story.append(Spacer(1, 4))

    # SECTION 2: GLYCEMIC PROFILE & DIABETIC MONITORING (TYPE 2 DIABETES AXIS)
    story.append(Paragraph("2. GLYCEMIC BURDEN & DIABETES MONITORING PANEL (DIABETES AXIS)", section_heading))
    diab_rows = [
        headers,
        [Paragraph("Fasting Plasma Glucose (FBS)", cell_normal), Paragraph("<b>168 mg/dL</b>", cell_abnormal), Paragraph("70 - 99 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Overt Diabetic Range (>=126)</font>", cell_normal)],
        [Paragraph("Glycated Hemoglobin (HbA1c)", cell_normal), Paragraph("<b>8.6 %</b>", cell_abnormal), Paragraph("< 5.7 % (Normal)", cell_normal), Paragraph("<font color='#b91c1c'>Uncontrolled Diabetes (>=6.5%)</font>", cell_normal)],
        [Paragraph("Postprandial Glucose (PPBS 2hr)", cell_normal), Paragraph("<b>246 mg/dL</b>", cell_abnormal), Paragraph("< 140 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Marked glycemic spike</font>", cell_normal)],
        [Paragraph("Fasting Serum Insulin", cell_normal), Paragraph("<b>24.5 uIU/mL</b>", cell_abnormal), Paragraph("2.6 - 24.9 uIU/mL", cell_normal), Paragraph("<font color='#d97706'>Elevated / Insulin Resistance</font>", cell_normal)]
    ]
    t_diab = Table(diab_rows, colWidths=[170, 95, 125, 150])
    t_diab.setStyle(table_style_common)
    story.append(t_diab)
    story.append(Spacer(1, 4))

    # SECTION 3: RENAL FUNCTION & GLOMERULAR FILTRATION (CHRONIC KIDNEY DISEASE AXIS)
    story.append(Paragraph("3. RENAL FUNCTION & GLOMERULAR FILTRATION PANEL (CKD AXIS)", section_heading))
    renal_rows = [
        headers,
        [Paragraph("Serum Creatinine", cell_normal), Paragraph("<b>2.20 mg/dL</b>", cell_abnormal), Paragraph("0.70 - 1.30 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Markedly elevated</font>", cell_normal)],
        [Paragraph("Estimated GFR (eGFR, CKD-EPI 2021)", cell_normal), Paragraph("<b>36 mL/min/1.73m²</b>", cell_abnormal), Paragraph("> 90 mL/min/1.73m²", cell_normal), Paragraph("<font color='#b91c1c'>CKD Stage G3b (Moderate-Severe)</font>", cell_normal)],
        [Paragraph("Blood Urea Nitrogen (BUN)", cell_normal), Paragraph("<b>36 mg/dL</b>", cell_abnormal), Paragraph("7 - 20 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Azotemic waste retention</font>", cell_normal)],
        [Paragraph("Urine Albumin-Creatinine Ratio (uACR)", cell_normal), Paragraph("<b>420 mg/g</b>", cell_abnormal), Paragraph("< 30 mg/g", cell_normal), Paragraph("<font color='#b91c1c'>Severely Increased / A3 Macroalbuminuria</font>", cell_normal)],
        [Paragraph("Urine Protein (Dipstick)", cell_normal), Paragraph("<b>2+</b>", cell_abnormal), Paragraph("Negative", cell_normal), Paragraph("<font color='#b91c1c'>Significant Glomerular Leakage</font>", cell_normal)],
        [Paragraph("Serum Potassium", cell_normal), Paragraph("<b>5.1 mmol/L</b>", cell_abnormal), Paragraph("3.5 - 5.0 mmol/L", cell_normal), Paragraph("<font color='#d97706'>Mild hyperkalemia</font>", cell_normal)],
        [Paragraph("Serum Phosphorus", cell_normal), Paragraph("<b>4.8 mg/dL</b>", cell_abnormal), Paragraph("2.5 - 4.5 mg/dL", cell_normal), Paragraph("<font color='#d97706'>Subtle phosphate retention</font>", cell_normal)]
    ]
    t_renal = Table(renal_rows, colWidths=[170, 95, 125, 150])
    t_renal.setStyle(table_style_common)
    story.append(t_renal)
    story.append(Spacer(1, 4))

    # SECTION 4: HEPATIC ENZYMES & LIVER FUNCTION (HEPATIC / LIVER DISEASE AXIS)
    story.append(Paragraph("4. HEPATIC FUNCTION & ENZYME PANEL (LIVER DISEASE AXIS)", section_heading))
    liver_rows = [
        headers,
        [Paragraph("ALT / SGPT (Alanine Aminotransferase)", cell_normal), Paragraph("<b>118 U/L</b>", cell_abnormal), Paragraph("7 - 56 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Transaminitis (>2x ULN)</font>", cell_normal)],
        [Paragraph("AST / SGOT (Aspartate Aminotransferase)", cell_normal), Paragraph("<b>98 U/L</b>", cell_abnormal), Paragraph("10 - 40 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Markedly elevated</font>", cell_normal)],
        [Paragraph("Total Bilirubin", cell_normal), Paragraph("<b>2.1 mg/dL</b>", cell_abnormal), Paragraph("0.2 - 1.2 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Hyperbilirubinemia</font>", cell_normal)],
        [Paragraph("Direct Bilirubin (Conjugated)", cell_normal), Paragraph("<b>0.8 mg/dL</b>", cell_abnormal), Paragraph("0.0 - 0.3 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Conjugated excretory delay</font>", cell_normal)],
        [Paragraph("Alkaline Phosphatase (ALP)", cell_normal), Paragraph("<b>195 U/L</b>", cell_abnormal), Paragraph("44 - 147 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Cholestatic pattern</font>", cell_normal)],
        [Paragraph("Serum Albumin", cell_normal), Paragraph("<b>3.1 g/dL</b>", cell_abnormal), Paragraph("3.5 - 5.0 g/dL", cell_normal), Paragraph("<font color='#d97706'>Low / synthetic deficit</font>", cell_normal)],
        [Paragraph("Gamma-Glutamyl Transferase (GGT)", cell_normal), Paragraph("<b>112 U/L</b>", cell_abnormal), Paragraph("9 - 48 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Canalicular epithelial stress</font>", cell_normal)]
    ]
    t_liver = Table(liver_rows, colWidths=[170, 95, 125, 150])
    t_liver.setStyle(table_style_common)
    story.append(t_liver)
    story.append(Spacer(1, 4))

    # 4. Clinical Assessment & Multidisciplinary Plan
    story.append(Paragraph("MULTIDISCIPLINARY CLINICAL ASSESSMENT & UNIFIED MANAGEMENT PLAN", section_heading))
    p_assess = Paragraph(
        "<b>Clinical Impression:</b> Multisystem Cardiorenal-Metabolic & Hepatic Syndrome in patient Sivaathithya (46yo M). "
        "Concomitant four-organ pathology confirmed: <b>(1) Stage 2 Hypertension & Atherogenic Dyslipidemia</b> (BP 152/94, LDL 162 mg/dL); "
        "<b>(2) Poorly Controlled Type 2 Diabetes Mellitus</b> (HbA1c 8.6%, Fasting Glucose 168 mg/dL); "
        "<b>(3) Chronic Kidney Disease Stage G3b A3</b> (eGFR 36 mL/min/1.73m², uACR 420 mg/g, Creatinine 2.20 mg/dL); and "
        "<b>(4) Active Hepatic Transaminitis & Cholestasis</b> (ALT 118 U/L, AST 98 U/L, Bilirubin 2.1 mg/dL, ALP 195 U/L).<br/><br/>"
        "<b>Integrated Clinical Action Plan:</b><br/>"
        "• <i>Cardiovascular & Metabolic:</i> Target BP &lt; 130/80 mmHg; initiate cardioprotective therapy (ACEi/ARB, high-intensity statin, SGLT2 inhibitor / GLP-1 RA).<br/>"
        "• <i>Renal Stewardship:</i> Monitor renal hemodynamic response; restrict sodium (&lt;1,800 mg/day); discontinue all nephrotoxins (NSAIDs).<br/>"
        "• <i>Hepatology Workup:</i> Perform liver elastography (FibroScan) and abdominal ultrasound; withhold potential hepatotoxic agents.<br/>"
        "• <i>Urgency:</i> High Priority multidisciplinary outpatient consultation within 7 days.",
        body_style
    )
    story.append(p_assess)
    story.append(Spacer(1, 6))

    # 5. Signatures
    sig_data = [
        [
            Paragraph("<b>Dr. Vikram Menon, MD, DM</b><br/>Senior Consultant Cardiologist<br/>Reg No: DMC-55102", cell_normal),
            Paragraph("<b>Dr. Pooja Nair, MD, DM</b><br/>Senior Consultant Endocrinologist<br/>Reg No: DMC-61984", cell_normal),
            Paragraph("<b>Dr. Arvind Deshmukh, MD, DM</b><br/>Senior Consultant Nephrologist<br/>Reg No: DMC-68421", cell_normal),
            Paragraph("<b>Dr. Sunita Rao, MD, DM</b><br/>Senior Consultant Hepatologist<br/>Reg No: DMC-74195", cell_normal)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[135, 135, 135, 135])
    t_sig.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
    ]))
    story.append(t_sig)

    doc.build(story)
    print(f"Report generated successfully: {output_path}")

if __name__ == "__main__":
    local_path = "backend/tests/siva_quadruple_disease_report.pdf"
    generate_quadruple_disease_report(local_path)
    
    downloads_path = r"c:\Users\sivaa\Downloads\siva_quadruple_disease_report.pdf"
    try:
        shutil.copyfile(local_path, downloads_path)
        print(f"Copied to downloads: {downloads_path}")
    except Exception as e:
        print(f"Could not copy to Downloads directly: {e}")
