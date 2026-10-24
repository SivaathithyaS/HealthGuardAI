# 🌐 HealthGuard AI — Multimodal Clinical Intelligence & Prevention Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6+-F7931E.svg?style=flat&logo=scikit-learn)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/SHAP-TreeExplainer-FF6F00.svg?style=flat)](https://shap.readthedocs.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?style=flat&logo=vite)](https://vitejs.dev)
[![SQLite](https://img.shields.io/badge/SQLite-User%20Isolation-003B57.svg?style=flat&logo=sqlite)](https://sqlite.org)

An explainable, multimodal clinical AI decision-support and disease-prevention platform. **HealthGuard AI** ingests unstructured medical reports (PDF lab bloodwork, CT/CTA scans, brain MRIs, ECG waveforms, clinical symptom narratives), parses patient demographics and biomarkers, executes a **3-Tier Clinical Hierarchy**, and generates structured prevention roadmaps — all behind a **real email-OTP authenticated, per-user isolated health history system**.

---

## 🔐 Authentication & Personal Health History

HealthGuard AI includes a full authentication system with **real email OTP verification**, **PBKDF2-hashed passwords**, and **SQLite-persisted per-user isolated health records**.

### Pre-seeded Demo Accounts

Two accounts are auto-created on first launch — no registration needed:

| Role | Name | Email | Password |
|---|---|---|---|
| **Clinician** | Dr. Sarah Lin, MD | `clinician@healthguard.ai` | `Password123!` |
| **Patient (Demo)** | test1 | `test@gmail.com` | `test` |

> You can also click **"Quick Clinician Demo Access"** on the login page to sign in instantly.

### Registration Flow (with Real Email OTP)
1. Click **"Create an account"** on the login screen
2. Enter your name, email, and password → click **"Send verification code"**
3. A 6-digit OTP is emailed to you (requires SMTP config, see below)
4. Enter the code → account is created → sign in

### Personal Health History
Each user has a **completely isolated** health history tab (`My Health History`) that shows:
- All past checkup results with expandable details (findings, recommendations, risk score)
- **Longitudinal trajectory analysis** — visit-over-visit biomarker delta comparison
- Trajectory classification: `FAVORABLE_TRAJECTORY` / `STABLE_MAINTENANCE` / `ATTENTION_REQUIRED`

### Email OTP Setup (Optional)
Copy `.env.example` to `.env` and fill in your Gmail App Password:
```bash
cp .env.example .env
```
```env
SMTP_USER=your-gmail@gmail.com
SMTP_PASSWORD=xxxx-xxxx-xxxx-xxxx   # 16-char Google App Password
```
> Get an App Password at: https://support.google.com/accounts/answer/185833  
> If SMTP is not configured, the OTP is shown in the API response for dev/demo use.

---

## 🌟 Core System Capabilities

### 1. 📄 Multimodal Medical Document Ingestion & Extraction
- Ingests native PDF documents, scanned imaging reports, and clinical text
- **Multi-Line Entity Extractor**: Parses patient name, age, sex, MRN, study date, vitals and biomarkers without rigid formats
- **Isolated State Purging**: Every analysis generates a unique session UUID — no cross-case contamination

### 2. 🪜 3-Tier Clinical Evidence Hierarchy
- **Level 1 (Observed Finding)**: Raw quantitative/radiologic evidence
- **Level 2 (Clinical Interpretation)**: Pathophysiologic meaning
- **Level 3 (Diagnostic Consideration)**: Risk context and next-step recommendations

### 3. 🌿 Transparent Decision Node Split Traversal
Translates ML tree splits into human-readable clinical reasoning:
- **Step 1**: Hemodynamic threshold (BP ≥ 140 mmHg)
- **Step 2**: Atherogenic lipids (LDL ≥ 130 or Total Chol ≥ 200 mg/dL)
- **Step 3**: Glycemic homeostasis (HbA1c ≥ 5.7% or Glucose ≥ 100 mg/dL)
- **Step 4**: Anthropometric obesity (BMI ≥ 30.0 kg/m²)

### 4. ⚠️ Clinical Safety & Guardrails
- **Conflicting Evidence Detection**: Laterality discordance, dominant-hemisphere alerts
- **Safe Non-Definitive Framing**: Imaging impressions framed as *suspected*
- **Single BP Qualification**: Replaces premature hypertension diagnoses

### 5. ⚡ Evidence-Based Prevention Engine
- **⚡ Short-Term Routine (Days 1–30)**: Daily/weekly protocols — BP diary, DASH <1500 mg sodium, 30-min daily walk
- **🛡️ Long-Term Protocol (Months 1–6+)**: Sustained targets — 5–7% weight reduction, quarterly lipid & HbA1c re-assessment

### 6. 🔍 Explainable AI (XAI) with TreeSHAP
- Decomposes predictions into directional risk-increasing (φ > 0) and risk-reducing (φ < 0) clinical drivers
- Empirical 95% Confidence Intervals to prevent false numerical overconfidence

### 7. 🧠 Clinical Imaging & Waveform CNN Pipeline
- **ECG 1D-CNN**: Waveform classification (stub bundle, swappable with real weights)
- **Brain MRI DenseNet-121**: Imaging classification with GradCAM-style heatmap overlay
- Model bundles loaded from `backend/data/imaging/<name>/` (weights.pt + config.json + preprocess.py)
- SHA-256 checksum verification per bundle

---

## 📊 Datasets & Curated Benchmarks

All datasets in `backend/data/curated_high_quality/`:

| Dataset | Source | N | Features | Task |
|---|---|---|---|---|
| Disease-Symptom 41-Class | Open Biomedical Benchmark | 4,920 | 132 symptom indicators | 41-class differential diagnosis |
| UCI Heart Disease | Cleveland Clinic / UCI | 303 | 13 hemodynamic features | CAD binary classification |
| Pima Indians Diabetes | NIDDK / UCI | 768 | 8 metabolic biomarkers | Type 2 DM binary classification |
| Wisconsin Oncology (WDBC) | UCI ML Repository | 569 | 30 radiomics features | Malignancy vs Benign |
| Indian Liver Patient (ILPD) | UCI ML Repository | 583 | 10 hepatic biomarkers | Liver disease risk |
| Dermatology Biopsy | UCI ML Repository | 366 | 34 histopathology features | 6-class skin disease |
| Multimodal Clinical Benchmark | Blinded Hospital Scenarios | 10 | Full PDF clinical reports | Blinded multi-specialty validation |

---

## 🏗️ ML Model Architectures

```
backend/data/
├── heart_pipeline.pkl                         # Soft-Voting Ensemble [ROC-AUC: 0.9429]
├── diabetes_pipeline.pkl                      # Gradient Boosting + TreeSHAP [ROC-AUC: 0.8244]
├── oncology_radiomics_pipeline.pkl            # Cost-Sensitive Balanced RF [ROC-AUC: 0.9961]
├── universal_symptom_41_disease_pipeline.pkl  # 41-Disease Multiclass Ensemble [100% Acc]
├── stroke_pipeline.pkl                        # Neurovascular LVO Screening Pipeline
├── ckd_pipeline.pkl                           # Renal Biomarker Ensemble [ROC-AUC: 0.9825]
├── liver_pipeline.pkl                         # Hepatic Biomarker Pipeline
├── healthguard.db                             # SQLite — users, sessions, isolated checkup history
└── imaging/
    ├── ecg_1dcnn/                             # ECG waveform CNN stub bundle
    └── mri_cnn/                               # Brain MRI CNN stub bundle
```

---

## 📁 Repository Structure

```
HealthGuardAI/
├── frontend/                          # React 19 + Vite 6 Web Dashboard
│   ├── src/
│   │   ├── main.jsx                   # Entry point → AuthGate
│   │   ├── AuthGate.jsx               # Session hydration & routing
│   │   ├── App.jsx                    # Multi-Specialty Clinical Dashboard
│   │   ├── index.css                  # Dark Clinical Design System
│   │   └── components/
│   │       ├── AuthPage.jsx           # Login / Register / OTP verification UI
│   │       ├── HealthHistory.jsx      # Per-user isolated checkup timeline
│   │       ├── ImagingView.jsx        # ECG & MRI CNN upload + heatmap UI
│   │       ├── EcgWaveform.jsx        # Real-time ECG waveform renderer
│   │       ├── HeatmapOverlay.jsx     # GradCAM-style MRI heatmap overlay
│   │       ├── BenchmarkHubView.jsx   # Live validation benchmark dashboard
│   │       ├── ModelCardView.jsx      # Clinical model card specification
│   │       ├── SummaryView.jsx        # Plain-language summary view
│   │       ├── AuditLogModal.jsx      # Clinician feedback & audit trail
│   │       ├── OverrideModal.jsx      # Human-in-the-loop override dialog
│   │       └── RubricModal.jsx        # Evidence rubric viewer
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI gateway & route configuration
│   │   ├── routes/
│   │   │   ├── auth_routes.py         # Auth: register/OTP/login/me/history/logout
│   │   │   ├── analysis_routes.py     # Universal upload & direct prediction endpoints
│   │   │   ├── imaging_routes.py      # ECG/MRI CNN inference endpoints
│   │   │   ├── heart_routes.py        # Cardiology ensemble endpoint
│   │   │   └── report_routes.py       # Preset cases & sample provider
│   │   ├── schemas/
│   │   │   ├── universal_disease.py   # 3-Tier hierarchy & routine schemas
│   │   │   ├── multi_disease.py       # ML biomarker & prediction schemas
│   │   │   └── imaging.py             # CNN inference response schemas
│   │   └── services/
│   │       ├── user_db_service.py     # SQLite: users, sessions, checkup history, longitudinal
│   │       ├── email_service.py       # Gmail SMTP OTP delivery
│   │       ├── cnn_service.py         # Imaging model bundle loader & inferencer
│   │       ├── universal_disease_service.py  # Universal reasoning engine
│   │       ├── report_parser_service.py      # Multi-line PDF & text entity recognition
│   │       ├── neuro_oncology_service.py     # Brain MRI tumour analysis
│   │       ├── stroke_service.py             # CT/CTA neurovascular stroke analysis
│   │       └── prediction_service.py         # ML pipeline inferencing & TreeSHAP
│   └── data/
│       ├── curated_high_quality/      # Raw curated CSV datasets
│       ├── imaging/                   # CNN model bundles
│       ├── healthguard.db             # SQLite user database (auto-created)
│       └── *.pkl                      # Serialized ML pipeline binaries
├── tests/
│   ├── test_clinical_safety.py        # Clinical safety & guardrail unit tests
│   └── test_imaging.py                # CNN imaging pipeline tests (ok/uncertain/rejected)
├── .env.example                       # SMTP configuration template
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart & Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 1. Clone & Backend Setup
```bash
git clone https://github.com/SivaathithyaS/HealthGuardAI.git
cd HealthGuardAI

# Create & activate virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS/Linux

# Install Python dependencies
pip install -r requirements.txt

# (Optional) Configure real email OTP
cp .env.example .env
# Edit .env — add your Gmail App Password

# Start FastAPI backend
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API docs live at: **http://localhost:8000/docs**

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser.

### 3. Sign In
Use one of the pre-seeded accounts:

| Account | Email | Password |
|---|---|---|
| Clinician demo | `clinician@healthguard.ai` | `Password123!` |
| Patient demo | `test@gmail.com` | `test` |

Or click **"Quick Clinician Demo Access"** for instant login.

---

## 🗺️ Dashboard Tabs

| Tab | Description |
|---|---|
| **Universal Report Scanner** | Upload PDF/image/text reports → 3-tier hierarchy, prevention roadmap, SHAP drivers |
| **Cardiology Risk Assessment** | Interactive 13-feature heart disease ensemble with SHAP breakdown |
| **Diabetes Risk Assessment** | 8-feature metabolic biomarker ensemble with confidence intervals |
| **Live Validation Benchmark Hub** | Blinded 10-case evaluation across all ML models |
| **Clinical Model Card** | Full model specification — training data, metrics, limitations, bias analysis |
| **Imaging & Waveforms** | ECG 1D-CNN waveform upload + Brain MRI DenseNet upload with heatmap overlay |
| **My Health History** | Per-user isolated timeline — all past checkups, biomarker deltas, longitudinal trajectory |

---

## 🧪 Automated Testing

```bash
# Clinical safety & guardrail tests
python -m pytest tests/test_clinical_safety.py -v

# Imaging pipeline tests (ok / uncertain / rejected cases)
python -m pytest tests/test_imaging.py -v
```

**Results:**
- ✅ Cardiometabolic Case — BP qualification, BMI calculation, 4-tier hierarchy, 5 risk factors
- ✅ Brain Tumor Case — Non-definitive framing, biopsy confirmation required
- ✅ Acute Stroke Case — Conflicting laterality evidence alert detected
- ✅ Imaging OK case — Confident classification above threshold
- ✅ Imaging Uncertain case — Returns `status=uncertain` below threshold
- ✅ Imaging Rejected case — Rejects invalid input with `rejected_input=true`

---

## ⚖️ Clinical Disclaimer

**HealthGuard AI** is an academic research and clinical decision-support prototype. AI evidence scores, radiomic classifications, and decision node traversal paths are designed for clinical workflow assistance and education. They do **not** replace formal in-person diagnostic evaluation, histopathological tissue diagnosis, or physician judgment.

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.
