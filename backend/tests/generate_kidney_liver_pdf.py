import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_kidney_liver_report(output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        alignment=1, # Center
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#475569'),
        alignment=1,
        spaceAfter=6
    )

    banner_style = ParagraphStyle(
        'Banner',
        parent=styles['Normal'],
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#b91c1c'),
        alignment=1,
        spaceAfter=8
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=9.5,
        leading=12,
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=7,
        spaceAfter=4,
        borderPadding=(2, 4, 2, 4)
    )

    cell_bold = ParagraphStyle(
        'CellBold',
        parent=styles['Normal'],
        fontSize=8,
        leading=10.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#0f172a')
    )

    cell_normal = ParagraphStyle(
        'CellNormal',
        parent=styles['Normal'],
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor('#334155')
    )

    cell_abnormal = ParagraphStyle(
        'CellAbnormal',
        parent=styles['Normal'],
        fontSize=8,
        leading=10.5,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#b91c1c')
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    story = []

    # Header
    story.append(Paragraph("SYNTHETIC DATA — DEMONSTRATION RECORD FOR CAPSTONE PROJECT — NOT REAL MEDICAL DATA", banner_style))
    story.append(Paragraph("METROPOLITAN MULTISPECIALTY CLINICAL LABORATORIES", title_style))
    story.append(Paragraph("NABH & NABL ACCREDITED TERTIARY DIAGNOSTIC CENTER | DEPARTMENT OF NEPHROLOGY & HEPATOLOGY<br/>28/A Medical Square, Metro Vihar, New Delhi - 110001 | Phone: 011-2098-7654 | www.metro-labs-cds.org", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=8))

    # Patient Details Table
    story.append(Paragraph("PATIENT & REVIEW DETAILS", section_heading))
    pt_data = [
        [
            Paragraph("<b>Patient Name:</b> Sivaathithya", cell_normal),
            Paragraph("<b>Age / Sex:</b> 46 Years / Male", cell_normal),
            Paragraph("<b>UHID / MRN:</b> METRO-SIVA-3098", cell_normal)
        ],
        [
            Paragraph("<b>Evaluation Date:</b> 18/02/2027", cell_normal),
            Paragraph("<b>Clinic / Department:</b> Nephrology & Hepatology OPD", cell_normal),
            Paragraph("<b>Acuity Status:</b> <font color='#b91c1c'><b>ATTENTION REQUIRED (DUAL-ORGAN CDS)</b></font>", cell_normal)
        ],
        [
            Paragraph("<b>Consultant:</b> Dr. Arvind Deshmukh, MD, DM", cell_normal),
            Paragraph("<b>Specimen:</b> Venous Blood & Spot Urine", cell_normal),
            Paragraph("<b>Sample Collection:</b> Fasting (12 hrs)", cell_normal)
        ]
    ]
    t_pt = Table(pt_data, colWidths=[180, 180, 180])
    t_pt.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8fafc')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('LEFTPADDING', (0,0), (-1,-1), 6),
        ('RIGHTPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_pt)
    story.append(Spacer(1, 6))

    # Clinical Presentation History
    story.append(Paragraph("CLINICAL PRESENTATION & REASON FOR REVIEW", section_heading))
    p_hist = Paragraph(
        "Patient presents with a 4-month history of bilateral lower extremity edema, persistent fatigue, early morning nausea, foamy urine, "
        "dark amber urine, and mild scleral icterus accompanied by right upper quadrant fullness. No history of nephrolithiasis, acute abdominal trauma, "
        "or heavy alcohol use. Comprehensive dual-organ screening panel requested to evaluate concomitant renal functional decline and active hepatic inflammation.",
        body_style
    )
    story.append(p_hist)
    story.append(Spacer(1, 6))

    # 1. Kidney Panel Table
    story.append(Paragraph("1. RENAL FUNCTION & CLINICAL NEPHROLOGY PANEL", section_heading))
    headers = [
        Paragraph("<b>Biomarker / Investigation</b>", cell_bold),
        Paragraph("<b>Observed Result</b>", cell_bold),
        Paragraph("<b>Target Reference Range</b>", cell_bold),
        Paragraph("<b>Clinical Flag / Interpretation</b>", cell_bold)
    ]
    renal_rows = [
        headers,
        [Paragraph("Serum Creatinine", cell_normal), Paragraph("<b>2.4 mg/dL</b>", cell_abnormal), Paragraph("0.7 - 1.3 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Markedly elevated</font>", cell_normal)],
        [Paragraph("eGFR (CKD-EPI 2021)", cell_normal), Paragraph("<b>33 mL/min/1.73 m²</b>", cell_abnormal), Paragraph("> 90 mL/min/1.73 m²", cell_normal), Paragraph("<font color='#b91c1c'>Reduced (Stage G3b)</font>", cell_normal)],
        [Paragraph("Blood Urea Nitrogen (BUN)", cell_normal), Paragraph("<b>38 mg/dL</b>", cell_abnormal), Paragraph("7 - 20 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Azotemic retention</font>", cell_normal)],
        [Paragraph("Urine Albumin-Creatinine Ratio (uACR)", cell_normal), Paragraph("<b>480 mg/g</b>", cell_abnormal), Paragraph("< 30 mg/g", cell_normal), Paragraph("<font color='#b91c1c'>Severely increased (A3)</font>", cell_normal)],
        [Paragraph("Urine Protein (Dipstick)", cell_normal), Paragraph("<b>3+</b>", cell_abnormal), Paragraph("Negative", cell_normal), Paragraph("<font color='#b91c1c'>Heavy proteinuria</font>", cell_normal)],
        [Paragraph("Serum Potassium", cell_normal), Paragraph("<b>5.3 mmol/L</b>", cell_abnormal), Paragraph("3.5 - 5.0 mmol/L", cell_normal), Paragraph("<font color='#d97706'>Mildly elevated</font>", cell_normal)],
        [Paragraph("Serum Bicarbonate", cell_normal), Paragraph("<b>20 mmol/L</b>", cell_abnormal), Paragraph("22 - 29 mmol/L", cell_normal), Paragraph("<font color='#d97706'>Subnormal (Mild acidosis)</font>", cell_normal)],
        [Paragraph("Serum Phosphate", cell_normal), Paragraph("<b>5.1 mg/dL</b>", cell_abnormal), Paragraph("2.5 - 4.5 mg/dL", cell_normal), Paragraph("<font color='#d97706'>Mildly elevated</font>", cell_normal)]
    ]
    t_renal = Table(renal_rows, colWidths=[170, 100, 120, 150])
    t_renal.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_renal)
    story.append(Spacer(1, 6))

    # 2. Liver Panel Table
    story.append(Paragraph("2. HEPATIC FUNCTION & LIVER ENZYME PANEL (LFT)", section_heading))
    liver_rows = [
        headers,
        [Paragraph("ALT / SGPT (Alanine Aminotransferase)", cell_normal), Paragraph("<b>128 U/L</b>", cell_abnormal), Paragraph("7 - 56 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Marked transaminitis (>2x ULN)</font>", cell_normal)],
        [Paragraph("AST / SGOT (Aspartate Aminotransferase)", cell_normal), Paragraph("<b>112 U/L</b>", cell_abnormal), Paragraph("10 - 40 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Markedly elevated</font>", cell_normal)],
        [Paragraph("Total Bilirubin", cell_normal), Paragraph("<b>2.3 mg/dL</b>", cell_abnormal), Paragraph("0.2 - 1.2 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Hyperbilirubinemia</font>", cell_normal)],
        [Paragraph("Direct Bilirubin (Conjugated)", cell_normal), Paragraph("<b>0.9 mg/dL</b>", cell_abnormal), Paragraph("0.0 - 0.3 mg/dL", cell_normal), Paragraph("<font color='#b91c1c'>Conjugated elevation</font>", cell_normal)],
        [Paragraph("Alkaline Phosphatase (ALP)", cell_normal), Paragraph("<b>215 U/L</b>", cell_abnormal), Paragraph("44 - 147 U/L", cell_normal), Paragraph("<font color='#b91c1c'>Cholestatic pattern</font>", cell_normal)],
        [Paragraph("Serum Albumin", cell_normal), Paragraph("<b>3.1 g/dL</b>", cell_abnormal), Paragraph("3.5 - 5.0 g/dL", cell_normal), Paragraph("<font color='#d97706'>Low / synthetic deficit</font>", cell_normal)],
        [Paragraph("Total Serum Protein", cell_normal), Paragraph("<b>5.9 g/dL</b>", cell_normal), Paragraph("6.0 - 8.3 g/dL", cell_normal), Paragraph("Subnormal baseline", cell_normal)],
        [Paragraph("Gamma-Glutamyl Transferase (GGT)", cell_normal), Paragraph("<b>96 U/L</b>", cell_abnormal), Paragraph("9 - 48 U/L", cell_normal), Paragraph("<font color='#d97706'>Biliary/canalicular stress</font>", cell_normal)]
    ]
    t_liver = Table(liver_rows, colWidths=[170, 100, 120, 150])
    t_liver.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e2e8f0')),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('LEFTPADDING', (0,0), (-1,-1), 5),
        ('RIGHTPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_liver)
    story.append(Spacer(1, 6))

    # Assessment & Plan
    story.append(Paragraph("CLINICAL ASSESSMENT & MULTIDISCIPLINARY MANAGEMENT PLAN", section_heading))
    p_assess = Paragraph(
        "<b>Clinical Impression:</b> Dual-organ pathology consisting of <b>Chronic Kidney Disease, Stage G3b with severely increased albuminuria (A3)</b>, "
        "concomitant with <b>Active Hepatic Dysfunction / Transaminitis</b> (ALT 128 U/L, AST 112 U/L, Total Bilirubin 2.3 mg/dL, ALP 215 U/L). "
        "Renal functional impairment and hepatic parenchymal irritation require immediate joint specialist investigation.<br/><br/>"
        "<b>Recommended Diagnostic Workup:</b><br/>"
        "1. Complete bilateral renal duplex ultrasonography and hepatic ultrasound with Doppler / elastography.<br/>"
        "2. Viral hepatitis serologies (HBsAg, Anti-HCV, IgM Anti-HAV) and autoimmune liver screen.<br/>"
        "3. Immediate medication reconciliation: discontinue all nephrotoxins (NSAIDs) and hold potentially hepatotoxic drugs.<br/>"
        "4. Strict dietary sodium (<2,000 mg/day) and potassium management; outpatient Nephrology and Hepatology dual consultation.",
        body_style
    )
    story.append(p_assess)
    story.append(Spacer(1, 8))

    # Signature
    sig_data = [
        [
            Paragraph("<b>Dr. Arvind Deshmukh, MD, DM (Nephrology)</b><br/>Senior Consultant Nephrologist<br/>Reg No: DMC-68421", cell_normal),
            Paragraph("<b>Dr. Sunita Rao, MD, DM (Hepatology)</b><br/>Senior Consultant Hepatologist<br/>Reg No: DMC-74195", cell_normal),
            Paragraph("<b>Dr. R. K. Sharma, MD (Pathology)</b><br/>Director of Clinical Laboratories<br/>Reg No: DMC-41203", cell_normal)
        ]
    ]
    t_sig = Table(sig_data, colWidths=[180, 180, 180])
    t_sig.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 0.5, colors.HexColor('#94a3b8')),
        ('TOPPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_sig)

    doc.build(story)
    print(f"Report generated successfully: {output_path}")

if __name__ == "__main__":
    import shutil
    local_path = "backend/tests/siva_kidney_liver_report.pdf"
    generate_kidney_liver_report(local_path)
    
    # Also write to Downloads if possible
    downloads_path = r"c:\Users\sivaa\Downloads\siva_kidney_liver_report.pdf"
    try:
        shutil.copyfile(local_path, downloads_path)
        print(f"Copied to downloads: {downloads_path}")
    except Exception as e:
        print(f"Could not copy to Downloads directly: {e}")
