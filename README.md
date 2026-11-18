# 🌐 HealthGuard AI — Multimodal Clinical Intelligence & Prevention Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C.svg?style=flat&logo=pytorch)](https://pytorch.org)
[![Groq](https://img.shields.io/badge/Groq-Llama%203.3%20%2F%20GPT--OSS-F55036.svg?style=flat)](https://groq.com)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6+-F7931E.svg?style=flat&logo=scikit-learn)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/SHAP-TreeExplainer-FF6F00.svg?style=flat)](https://shap.readthedocs.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?style=flat&logo=vite)](https://vitejs.dev)
[![SQLite](https://img.shields.io/badge/SQLite-User%20Isolation-003B57.svg?style=flat&logo=sqlite)](https://sqlite.org)

An explainable, multimodal clinical AI decision-support and disease-prevention platform. **HealthGuard AI** ingests unstructured medical reports (PDF lab bloodwork, CT/CTA scans, brain MRIs, ECG waveforms, clinical symptom narratives), parses patient demographics and biomarkers, executes a **3-Tier Clinical Hierarchy**, runs **real Grad-CAM / 1D-CNN saliency maps**, and generates structured prevention roadmaps with **longitudinal visit-over-visit trajectory comparisons and Groq LLM clinical narration** — all secured behind an **email-OTP authenticated, per-user isolated health history system**.

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
1. Click **"Create an account"** on the login screen.
2. Enter your name, email, and password → click **"Send verification code"**.
3. A 6-digit OTP is delivered via Gmail SMTP (or surfaced in response if SMTP is not configured).
4. Enter the code → account is verified and ready for sign-in.

### Personal Health History & Longitudinal Comparison
Each user has a **completely isolated** health history dashboard (`My Health History`) that provides:
- Past diagnostic checkup records with expandable findings, clinical recommendations, and AI risk scores.
- **Visit-over-Visit Longitudinal Trajectory Engine** (`backend/app/services/longitudinal_service.py`):
  - Automatically identifies the most recent *comparable* prior visit (same modality and matching clinical condition or $\ge 2$ overlapping canonical biomarkers).
  - Normalizes clinical biomarker aliases and performs unit conversions (e.g. glucose/cholesterol mmol/L $\rightarrow$ mg/dL, creatinine $\mu$mol/L $\rightarrow$ mg/dL, HbA1c mmol/mol $\rightarrow$ %).
  - Evaluates changes using clinical reference ranges first, classifying deltas into `improved`, `worsened`, `unchanged`, or `changed_within_range`.
  - Determines longitudinal trajectory: `FAVORABLE_TRAJECTORY`, `ATTENTION_REQUIRED`, `MIXED`, `STABLE_MAINTENANCE`, or `BASELINE_ESTABLISHED`.
- **Groq LLM Clinical Narration** (`backend/app/services/llm_narrator.py`):
  - Uses Groq Llama 3.3 70B / GPT-OSS 120B to narrate comparison results in clear, non-clinician language.
  - Explains **what each biomarker represents** and **what the increase/decrease means for the patient's body**.
  - Provides an **Overall Health Assessment** summarizing how much the condition has developed or worsened.
  - Generates **Actionable Health Tips** (evidence-based lifestyle, nutrition, hydration, and activity guidance).
  - Enforces deterministic safety guardrails: strict response validator prevents hallucinated statistics, forbids drug prescriptions or definitive diagnoses, and falls back to a deterministic template if the LLM is unavailable or fails validation.
- **Patient Identity Verification**:
  - Automatically verifies that extracted document names match the logged-in user profile, triggering a confirmation modal if a mismatch occurs.
- **Clinician Feedback & Audit Log**:
  - Clinicians can log review notes, diagnostic overrides, and audit trails stored in an isolated `feedback` table.

---

## 🌟 Core System Capabilities

### 1. 📄 Multimodal Medical Document Ingestion & Extraction
- Ingests native PDF lab bloodwork, radiology reports, discharge summaries, and clinical narratives.
- **Multi-Line Entity Extractor**: Extracts patient demographics, MRN, study dates, and numerical biomarker values with units and clinical statuses without relying on rigid formats.
- **Clean Session State**: Every analysis generates an isolated UUID to prevent cross-case contamination.

### 2. 🪜 3-Tier Clinical Evidence Hierarchy
- **Tier 1 (Observed Finding)**: Direct quantitative and radiological evidence (e.g., `Observed HbA1c: 11.2%`).
- **Tier 2 (Pathophysiological Interpretation)**: Biological mechanism (e.g., `Profound chronic hyperglycemia with glucotoxicity`).
- **Tier 3 (Clinical Consideration)**: Risk context, complications, and immediate next steps.

### 3. 🧠 Deep Learning Imaging & Waveform Pipeline (PyTorch)
- **Brain MRI DenseNet-121**:
  - Deep convolutional neural network for neuro-oncology imaging classification.
  - **Real Grad-CAM Visualizations**: Forward and backward hooks on the last convolutional block (`features.denseblock4.denselayer16.conv2`) compute true spatial gradients, upsampled to 224x224 with a Jet colormap overlay on the input slice.
  - Safe weights loading via PyTorch `weights_only=True` state dictionaries with SHA-256 integrity checksum verification.
- **ECG ResNet-1D / 1D-CNN**:
  - 1D Convolutional network classifying 10-second cardiac rhythm waveforms.
  - **1D Saliency Activation**: Grad-CAM over time highlights arrhythmogenic cycles across 500 temporal points.
  - **Exact Preprocessing Parity**: 10-second 100 Hz recordings (1000 samples) decimated via `scipy.signal.resample_poly(sig, 1, 2)` to 500 samples + z-score normalization.
- **Fail-Safe Integrity**: Strict HTTP 503 error handling on missing weights or inference errors; no silent fallback to keyword-based scripting unless running in explicit demo mode (`HEALTHGUARD_DEMO_MODE=1`).

### 4. 🌿 Decision Tree Traversal & TreeSHAP XAI
- Translates machine learning tree splits into human-interpretable clinical reasoning steps (hemodynamic thresholds, atherogenic lipids, glycemic control, anthropometric BMI).
- **TreeSHAP Explainability**: Quantifies directional positive ($\phi > 0$) and negative ($\phi < 0$) feature contributions with 95% confidence intervals.

### 5. ⚡ Evidence-Based Prevention Engine
- **Short-Term Routine (Days 1–30)**: Acute management protocols (e.g., BP monitoring, DASH sodium restriction, low-glycemic dietary planning).
- **Long-Term Protocol (Months 1–6+)**: Sustained therapeutic targets (weight reduction, quarterly HbA1c and lipid re-evaluations, renal monitoring).

---

## 📊 Curated Benchmark Datasets & Pre-Trained Pipelines

All high-quality datasets and pre-trained models are located in `backend/data/`:

| Dataset / Model | Clinical Task | Performance | Architecture |
|---|---|---|---|
| **Heart Disease Soft-Voting** | Coronary Artery Disease Detection | ROC-AUC: **0.9429** | Soft-Voting Ensemble (Cleveland/UCI) |
| **Diabetes Glycemic Pipeline** | Type 2 Diabetes Mellitus Risk | ROC-AUC: **0.8244** | Gradient Boosting + TreeSHAP |
| **Wisconsin Oncology (WDBC)** | Breast Radiomics Classification | ROC-AUC: **0.9961** | Cost-Sensitive Balanced Random Forest |
| **CKD Renal Ensemble** | Chronic Kidney Disease Staging | ROC-AUC: **0.9825** | Random Forest + Lab Biomarker Rules |
| **Universal 41-Disease System** | Multi-Class Symptom Differential | Accuracy: **100%** | Multi-Class Ensemble (4,920 cases) |
| **Brain MRI DenseNet-121** | Tumor Detection & Localization | Verified PyTorch weights | DenseNet-121 + Real Grad-CAM |
| **ECG ResNet-1D** | Arrhythmia & Waveform Classification | Verified PyTorch weights | 1D-ResNet + Temporal Saliency |

---

## 📁 Repository Structure

```
HealthGuardAI/
├── frontend/                                  # React 19 + Vite Web Application
│   ├── src/
│   │   ├── main.jsx                           # Application entry point
│   │   ├── AuthGate.jsx                       # Session hydration & protected routing
│   │   ├── App.jsx                            # Multi-Specialty Clinical Dashboard
│   │   ├── index.css                          # Clinical theme & dark styling system
│   │   └── components/
│   │       ├── AuthPage.jsx                   # Login, registration, & OTP verification
│   │       ├── HealthHistory.jsx              # Timeline, Longitudinal Comparison, & AI Narrative
│   │       ├── ImagingView.jsx                # ECG & Brain MRI upload with Grad-CAM overlays
│   │       ├── EcgWaveform.jsx                # Real-time interactive ECG waveform canvas
│   │       ├── HeatmapOverlay.jsx             # Grad-CAM heatmap overlay renderer
│   │       ├── ModelCardView.jsx              # Model card documentation & bias analysis
│   │       ├── AuditLogModal.jsx              # Clinician feedback & audit trail viewer
│   │       ├── PatientMismatchModal.jsx       # Patient identity verification dialog
│   │       └── OverrideModal.jsx              # Human-in-the-loop diagnostic override dialog
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── main.py                            # FastAPI gateway & CORS configuration
│   │   ├── routes/
│   │   │   ├── auth_routes.py                 # Auth, OTP, checkup history, & narrative regenerate
│   │   │   ├── analysis_routes.py             # Universal document analysis & auto-comparison
│   │   │   ├── imaging_routes.py              # PyTorch ECG & MRI CNN inference endpoints
│   │   │   ├── heart_routes.py                # Cardiology ensemble prediction endpoint
│   │   │   └── report_routes.py               # Pre-configured clinical test samples
│   │   ├── schemas/
│   │   │   ├── universal_disease.py           # 3-Tier evidence hierarchy & routines
│   │   │   ├── multi_disease.py               # Biomarker input & prediction schemas
│   │   │   └── imaging.py                     # CNN inference & Grad-CAM response schemas
│   │   └── services/
│   │       ├── user_db_service.py             # SQLite user isolation, checkups, & comparisons
│   │       ├── longitudinal_service.py        # Deterministic visit-over-visit comparison engine
│   │       ├── llm_narrator.py                # Groq LLM clinical narrator with guardrails
│   │       ├── cnn_service.py                 # PyTorch model loader with Grad-CAM hooks
│   │       ├── cnn_architectures.py           # DenseNet-121 & ResNet-1D architecture builders
│   │       ├── universal_disease_service.py   # Multi-tier clinical reasoning engine
│   │       ├── report_parser_service.py       # PDF document & biomarker entity extraction
│   │       ├── email_service.py               # Gmail SMTP OTP delivery
│   │       └── prediction_service.py          # ML pipelines & TreeSHAP explainability
│   └── data/
│       ├── healthguard.db                     # SQLite database (users, checkups, comparisons, feedback)
│       ├── imaging/
│       │   ├── ecg_cnn/                       # ResNet-1D weights.pt, config.json, preprocess.py
│       │   └── mri_cnn/                       # DenseNet-121 weights.pt, config.json, preprocess.py
│       ├── test_samples/                      # PDF test reports (baseline, recovery, relapse)
│       └── *.pkl                              # Trained scikit-learn model pipelines
├── evaluation/                                # Benchmark evaluation harness
│   ├── longitudinal_eval.py                   # 30-case synthetic validation script
│   ├── cases.json                             # Clinical test case definitions
│   └── results.json                           # 100% passing evaluation results
├── model_training/                            # Model training & weight conversion scripts
│   ├── convert_to_state_dict.py               # Converts pickle weights to safe state_dict
│   └── ecg_ptbxl/                             # PTB-XL ECG dataset loading & preprocessing
├── tests/                                     # Automated test suite (76 tests)
│   ├── test_clinical_safety.py                # Guardrails, laterality alerts, BP qualifications
│   ├── test_imaging.py                        # Real Grad-CAM, weights_only, error handling
│   ├── test_longitudinal.py                   # Canonicalization, deltas, trajectory classification
│   ├── test_llm_narrator.py                   # Groq API mocking, validator, template fallback
│   ├── test_document_router.py                # Document classifier routing tests
│   └── test_evaluation.py                     # Evaluation benchmark tests
├── .env.example                               # Environment template (SMTP & Groq settings)
├── requirements.txt                           # Python dependencies
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

# Configure environment variables
cp .env.example .env
```

#### Optional: Configure Environment Variables in `.env`
```env
# Groq LLM Narration (Free API key at https://console.groq.com/)
GROQ_API_KEY=gsk_your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
LLM_NARRATION_ENABLED=true

# Real Email OTP (Gmail App Password)
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-16-char-app-password
```
*(If `GROQ_API_KEY` is not provided, the platform automatically uses the deterministic clinical template narrator. If SMTP is not configured, OTPs are surfaced directly in the API response for development).*

#### Start the FastAPI Server
```bash
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive API documentation is available at: **http://localhost:8000/docs**

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Open **http://localhost:5173** in your browser.

### 3. Sign In
Use one of the pre-seeded accounts:
- **Clinician**: `clinician@healthguard.ai` / `Password123!` (or click **"Quick Clinician Demo Access"**)
- **Patient**: `test@gmail.com` / `test`

---

## 🗺️ Application Navigation

| View / Tab | Key Capabilities |
|---|---|
| **Universal Report Scanner** | Ingests PDF/image/text lab work & discharge summaries $\rightarrow$ 3-tier clinical evidence, prevention protocol, TreeSHAP drivers. |
| **Cardiology Risk Assessment** | 13-feature interactive hemodynamic risk calculator with soft-voting ensemble & SHAP waterfall. |
| **Diabetes Risk Assessment** | 8-feature metabolic assessment with 95% confidence intervals and preventive routines. |
| **Imaging & Waveforms** | Upload 10-second ECG recordings or Brain MRI slices $\rightarrow$ PyTorch CNN inference with real Grad-CAM heatmaps & 1D temporal saliency. |
| **My Health History** | Per-user isolated health timeline $\rightarrow$ Visit-over-visit longitudinal comparison, trajectory badges, Groq LLM clinical narrative, and health tips. |
| **Clinical Model Card** | Comprehensive technical and clinical documentation — datasets, architectures, intended use, and bias analysis. |

---

## 🧪 Automated Testing

HealthGuard AI includes an extensive automated test suite (**76 unit & integration tests**):

```bash
# Run the complete test suite
python -m pytest tests/ -v
```

### Test Coverage Highlights:
- **Clinical Safety (`test_clinical_safety.py`)**: Single BP reading qualification, laterality conflict alerts, safe non-definitive phrasing.
- **Deep Learning Imaging (`test_imaging.py`)**: Verifies distinct Grad-CAM heatmaps for different inputs, `weights_only=True` loading, preprocessor parity with PTB-XL, and HTTP 503 error handling without silent scripting fallbacks.
- **Longitudinal Engine (`test_longitudinal.py` - 50 tests)**: Canonical biomarker key mapping, unit conversions, reference-range delta evaluation, multi-visit trends, and trajectory classification.
- **LLM Narrator (`test_llm_narrator.py` - 14 tests)**: Number allowlist verification, drug and prescription rejection, forbidden diagnosis guards, and template fallback on network timeouts or 429 rate limits.

---

## ⚖️ Clinical Disclaimer

**HealthGuard AI** is an academic research and clinical decision-support prototype. AI evidence scores, radiomic classifications, decision node traversal paths, and longitudinal narrations are designed for clinical workflow assistance and patient education. They do **not** replace formal in-person diagnostic evaluation, histopathological tissue diagnosis, or the medical judgment of a licensed healthcare clinician.

---

## 📄 License
MIT License — see [LICENSE](LICENSE) for details.
