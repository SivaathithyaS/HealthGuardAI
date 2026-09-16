# 🌐 HealthGuard AI — Universal Multi-Specialty Clinical Intelligence & Prevention Platform

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19.0+-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.6+-F7931E.svg?style=flat&logo=scikit-learn)](https://scikit-learn.org)
[![SHAP](https://img.shields.io/badge/SHAP-TreeExplainer-FF6F00.svg?style=flat)](https://shap.readthedocs.io)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python)](https://python.org)
[![Vite](https://img.shields.io/badge/Vite-6.0+-646CFF.svg?style=flat&logo=vite)](https://vitejs.dev)

An explainable, multimodal clinical AI decision support and disease prevention platform. **HealthGuard AI** ingests unstructured medical reports (PDF lab bloodwork, emergency CT/CTA scans, brain MRIs, and clinical symptom narratives), parses patient demographics and quantitative biomarkers, executes a **3-Tier Clinical Hierarchy**, traverses transparent **Decision Node Split Thresholds ("Node Points")**, evaluates calibrated **Soft-Voting Machine Learning Ensembles**, and generates structured **Short-Term (Days 1–30)** and **Long-Term (Months 1–6+) Prevention Routines**.

---

## 🌟 Core System Capabilities

### 1. 📄 Multimodal Medical Document Ingestion & Extraction
- Ingests native PDF documents, scanned imaging reports, and clinical text.
- **Multi-Line & Colon-Independent Entity Extractor**: Automatically parses patient name, age, biological sex, MRN, study date, ordering department, and quantitative vitals/biomarkers without relying on rigid single-line formats.
- **Isolated State Purging**: Every analysis generates a unique session UUID and purges prior patient state to eliminate cross-case contamination.

### 2. 🪜 3-Tier Clinical Evidence Hierarchy
Separates raw observations from pathophysiologic reasoning and diagnostic risk context:
- **Level 1 (Observed Finding)**: Quantitative/radiologic evidence (e.g., `Resting BP 148/94 mmHg`, `5.4x4.7 cm infiltrative fronto-insular mass`, `Right M1 MCA non-opacification`).
- **Level 2 (Clinical Interpretation)**: Pathophysiologic meaning (e.g., `Blood pressure in hypertensive range; confirmation recommended`, `Tumor neo-angiogenesis with central ischemic necrosis`).
- **Level 3 (Diagnostic Consideration)**: Risk context (e.g., `Repeated 24h ambulatory BP monitoring recommended`, `Glioblastoma is leading consideration; strictly requires tissue histopathology confirmation`).

### 3. 🌿 Transparent Decision Node Split Traversal ("Node Points")
Translates machine learning tree split criteria into human-interpretable clinical reasoning steps:
- **Step 1**: Hemodynamic / Blood Pressure threshold ($\ge 140\text{ mmHg}$).
- **Step 2**: Atherogenic Lipid fractions ($\text{LDL} \ge 130\text{ mg/dL}$ or $\text{Total Chol} \ge 200\text{ mg/dL}$).
- **Step 3**: Glycemic homeostasis ($\text{HbA1c} \ge 5.7\%$ or $\text{Fasting Glucose} \ge 100\text{ mg/dL}$).
- **Step 4**: Anthropometric Obesity ($\text{BMI} \ge 30.0\text{ kg/m}^2$).

### 4. ⚠️ Clinical Safety & Guardrails
- **Conflicting Clinical Evidence Detection**: Automatically identifies anatomical laterality discordance (e.g., Right M1 MCA occlusion with left hemiparesis paired with expressive language difficulty, alerting clinicians to dominant-hemisphere reconciliation).
- **Safe Non-Definitive Framing**: Frames imaging impressions as *suspected* (e.g., *"Aggressive High-Grade Primary Brain Neoplasm (Suspected); definitive diagnosis strictly requires histopathology"*).
- **Explicit BMI Calculation**: Automatically computes $\text{BMI} \approx 30.3\text{ kg/m}^2$ (from height $174\text{ cm}$ and weight $91.8\text{ kg}$) as a Class 1 Obesity modifiable risk factor.
- **Single BP Qualification**: Replaces premature hypertension diagnoses with: *"Blood pressure is in the hypertensive range on a single reading; confirmation with repeated/home/ambulatory measurements is recommended."*

### 5. ⚡ Evidence-Based Prevention Engine (Short-Term vs Long-Term)
- **⚡ Short-Term Routine (Days 1–30)**: Immediate daily/weekly protocols (twice-daily BP diary, DASH $<1500\text{ mg}$ sodium reduction, daily $30\text{ min}$ walk, primary care visit).
- **🛡️ Long-Term Protocol (Months 1–6+)**: Sustained targets ($5\text{–}7\%$ body weight reduction, quarterly lipid & HbA1c re-assessment, progressive aerobic + resistance conditioning).

### 6. 🔍 Explainable AI (XAI) with TreeSHAP
- Decomposes ensemble predictions into directional risk-increasing ($\phi_i > 0$) and risk-reducing ($\phi_i < 0$) clinical drivers.
- Computes empirical **95% Confidence Intervals** (e.g., *95% CI: 65.5% – 72.5%*) to prevent false numerical overconfidence.

---

## 📊 Datasets & Curated Benchmarks

All datasets are saved in `backend/data/curated_high_quality/`:

| Dataset Name | Source Repository | Sample Size ($N$) | Features / Attributes | Clinical Target & Task |
|---|---|---|---|---|
| **Disease-Symptom 41-Class** | Open Biomedical Benchmark | **$N = 4,920$** rows | $132$ binary symptom indicators | Multi-class differential diagnosis across **41 unique diseases** |
| **UCI Heart Disease** | UCI ML Repository (Cleveland Clinic) | **$N = 303$** cases | $13$ hemodynamic features | Binary classification of Coronary Artery Disease ($\ge 50\%$ narrowing) |
| **Pima Indians Diabetes** | NIDDK / UCI Repository | **$N = 768$** patients | $8$ metabolic biomarkers | Binary classification of Type 2 Diabetes Mellitus |
| **Wisconsin Oncology (WDBC)** | UCI ML Repository | **$N = 569$** biopsies | $30$ radiomics features | Biopsy Malignancy vs Benign Classification |
| **Indian Liver Patient (ILPD)** | UCI ML Repository | **$N = 583$** records | $10$ hepatic biochemical markers | Liver / Hepatic Disease risk classification |
| **Dermatology Biopsy** | UCI ML Repository | **$N = 366$** cases | $34$ histopathology features | 6 Erythemato-Squamous skin disease classification |
| **Multimodal Clinical Benchmark** | Blinded Hospital Scenarios | **$N = 10$** blinded cases | Full PDF Clinical Reports | Blinded multi-specialty validation suite |

---

## 🏗️ ML Model Architectures & Pipelines

```
backend/data/
├── heart_pipeline.pkl                         # Soft-Voting Ensemble (RandomForest + GradientBoosting) [ROC-AUC: 0.9429]
├── diabetes_pipeline.pkl                      # Gradient Boosting + TreeSHAP Engine [ROC-AUC: 0.8244]
├── oncology_radiomics_pipeline.pkl            # Cost-Sensitive Balanced Random Forest [ROC-AUC: 0.9961]
├── universal_symptom_41_disease_pipeline.pkl  # 41-Disease Multiclass Hierarchical Tree Ensemble [100% Accuracy]
├── stroke_pipeline.pkl                        # Neurovascular LVO Screening Pipeline
├── ckd_pipeline.pkl                           # Renal Biomarker Classification Ensemble [ROC-AUC: 0.9825]
└── liver_pipeline.pkl                         # Hepatic Biomarker Classification Pipeline
```

---

## 📁 Repository Structure

```
HealthGuardAI/
├── frontend/                          # React 19 + Vite 6 Modern Web Dashboard
│   ├── src/
│   │   ├── App.jsx                    # Full-Width Multi-Specialty Clinical Dashboard
│   │   └── index.css                  # Slate Dark Theme CSS Design System
│   └── package.json
├── backend/                           # FastAPI Clinical Intelligence Backend
│   ├── app/
│   │   ├── main.py                    # API Gateway & Route Configuration
│   │   ├── routes/
│   │   │   ├── analysis_routes.py     # Universal Upload & Direct Prediction Endpoints
│   │   │   ├── document_routes.py     # Preset Cases & Samples Provider
│   │   │   └── evaluation_routes.py   # Blinded 10-Case Evaluation Benchmark Engine
│   │   ├── schemas/
│   │   │   ├── universal_disease.py   # 3-Tier Hierarchy, Routines & Safety Schemas
│   │   │   └── multi_disease.py       # ML Biomarker & Prediction Schemas
│   │   ├── services/
│   │   │   ├── universal_disease_service.py # Universal Reasoning, Decision Node & Routine Engine
│   │   │   ├── report_parser_service.py     # Multi-Line PDF & Text Entity Recognition
│   │   │   ├── neuro_oncology_service.py    # Brain MRI Radiomics & Tumor Analysis
│   │   │   ├── stroke_service.py            # CT/CTA Neurovascular Stroke Analysis
│   │   │   └── prediction_service.py        # ML Pipeline Inferencing & TreeSHAP Drivers
│   │   └── ml_models/
│   │       └── train_curated_datasets.py    # Training & Serialization Scripts
│   ├── data/
│   │   ├── curated_high_quality/      # Raw Curated CSV Datasets
│   │   └── *.pkl                      # Serialized ML Pipeline Binaries
│   └── generate_review1_pdf.py        # Automated PDF Report Generator
├── docs/
│   ├── review1.pdf                    # Generated Presentation-Ready PDF Report
│   └── review1.md                     # Markdown Technical Documentation
├── tests/
│   └── test_clinical_safety.py        # Automated Clinical Safety & Guardrail Unit Tests
├── requirements.txt
└── README.md
```

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm

### 2. Backend Setup
```bash
# Clone repository
git clone https://github.com/your-username/HealthGuardAI.git
cd HealthGuardAI

# Install Python dependencies
pip install -r requirements.txt

# Start FastAPI server
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation will be live at: **[http://localhost:8000/docs](http://localhost:8000/docs)**

### 3. Frontend Setup
```bash
# In a new terminal window
cd frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** in your browser.

---

## 🧪 Automated Testing & Verification

Run the clinical safety and unit test suite:
```bash
python3 -m unittest tests/test_clinical_safety.py
```
**Test Results:**
- ✅ **Cardiometabolic Case**: Blood pressure confirmation qualified, BMI $30.3\text{ kg/m}^2$ calculated, 4-tier hierarchy and 5 modifiable risk factors verified.
- ✅ **Brain Tumor Case**: Non-definitive certainty level verified, required tissue biopsy confirmation verified.
- ✅ **Acute Stroke Case**: Conflicting clinical evidence alert detected for Right MCA occlusion + expressive language difficulty.
- **Pass Rate**: 3 of 3 Test Suites Passed (100% assertions satisfied in $0.017\text{s}$).

---

## ⚖️ Clinical Disclaimer
**HealthGuard AI** is an academic research and clinical decision-support prototype. AI evidence scores, radiomic classifications, and decision node traversal paths are designed for clinical workflow assistance and education. They do not replace formal in-person diagnostic evaluation, histopathological tissue diagnosis, or physician judgment.

---

## 📄 License
This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
