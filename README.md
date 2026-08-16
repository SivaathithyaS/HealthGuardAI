# HealthGuard AI: Multi-Disease Clinical Decision Support & Prevention Platform

An explainable hybrid machine learning clinical platform for multi-disease risk prediction, automated medical lab report scanning, local SHAP explainability, and personalized prevention roadmaps.

---

## 🌟 Key Features

1. **📄 Medical Lab Report Scanner & AI Diagnostic**
   - Upload scanned PDF, image (OCR), or raw lab reports (CBC, CMP, Lipid Profile, Renal Function KFT, Liver Function LFT).
   - Automatically extracts clinical biomarkers, highlights abnormal findings against reference ranges, and provides plain-English medical explanations.
   - Routes extracted biomarkers simultaneously into 4 disease predictive models.

2. **🫀 Multi-Disease Machine Learning Suite**
   - **Cardiovascular Disease**: UCI Cleveland Soft-Voting Ensemble ($90.2\%$ accuracy, $0.952$ ROC-AUC).
   - **Type 2 Diabetes**: Pima Indians Metabolic Ensemble ($74.0\%$ accuracy, $0.821$ ROC-AUC).
   - **Chronic Kidney Disease (CKD)**: UCI Renal Biomarker Ensemble ($91.3\%$ accuracy, $0.983$ ROC-AUC).
   - **Hepatic / Liver Disease**: Indian Liver Patient Dataset Ensemble ($69.2\%$ accuracy, $0.766$ ROC-AUC).

3. **🔍 Explainable AI (XAI)**
   - TreeSHAP local explainability decomposing patient log-odds into directional risk-increasing and risk-reducing clinical drivers.

4. **🌱 Counterfactual Prevention Roadmap**
   - Simulates risk reduction when modifiable biomarkers (glucose, blood pressure, cholesterol, BMI, transaminases, etc.) are optimized.
   - Structured 3-Tier Prevention Action Plan (1–4 Weeks, 1–3 Months, 6+ Months).

---

## 🏗️ Architecture & Directory Layout

```
HealthGuardAI/
├── frontend/               # React 19 + Vite 6 + Tailwind/Vanilla Design System
│   └── src/
│       ├── App.jsx         # Multi-Tab Dashboard (Report Scanner + 4 Disease Suites)
│       └── index.css       # Medical Theme CSS System
├── backend/
│   ├── app/
│   │   ├── ml_models/      # Training scripts for all 4 disease ensembles
│   │   ├── schemas/        # Pydantic validation models (Heart, Diabetes, CKD, Liver)
│   │   ├── services/       # Report parser, multi-disease orchestrator, SHAP engine
│   │   ├── routes/         # REST API route handlers (/report, /predict, /roadmap)
│   │   └── main.py         # FastAPI application entrypoint
│   └── data/               # Serialized ML pipeline artifacts (*_pipeline.pkl)
└── docs/                   # System documentation & API specifications
```

---

## 🚀 Quickstart Guide

### 1. Backend Server
```bash
cd backend
pip install -r requirements.txt
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Dashboard: [http://localhost:5173](http://localhost:5173)
