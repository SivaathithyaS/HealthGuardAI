import React from 'react';
import { 
  FileText, Shield, Database, Award, AlertTriangle, GitBranch, 
  ArrowRight, CheckCircle2, UserCheck, RefreshCw, BarChart3, Scale, Info
} from 'lucide-react';

export default function ModelCardView({ onNavigateToBenchmark }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Header Banner */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
              <span style={{ fontSize: '0.74rem', background: 'var(--accent-primary)', color: '#ffffff', padding: '3px 10px', borderRadius: '999px', fontWeight: 800 }}>
                CLINICAL DECISION SUPPORT MODEL CARD
              </span>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                System Release v1.2.0 • Last Revised: September 2026
              </span>
            </div>
            <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text-title)', fontFamily: 'var(--font-serif)' }}>
              HealthGuard AI — System Architecture & Model Card Specification
            </h2>
            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', maxWidth: '820px', marginTop: '6px' }}>
              Standardized clinical machine learning and decision-support documentation covering algorithmic architecture, reference validation datasets, mathematical scoring rubrics, human-in-the-loop oversight, and known operational limitations.
            </p>
          </div>

          <button 
            className="analyze-main-btn" 
            style={{ width: 'auto', padding: '12px 22px' }}
            onClick={onNavigateToBenchmark}
          >
            <BarChart3 size={16} />
            <span>View Live Benchmark Hub</span>
          </button>
        </div>
      </div>

      {/* Model Overview & Specifications */}
      <div className="glass-card">
        <div className="model-card-section">
          <div className="model-section-title">
            <GitBranch size={20} color="var(--accent-primary)" />
            <span>1. Model & System Overview</span>
          </div>
          <div className="model-section-content">
            HealthGuard AI is a multi-modal clinical decision-support pipeline designed to ingest unstructured radiology reports, clinical notes, and structured laboratory blood panels. The pipeline operates via a transparent, multi-stage hybrid architecture:
            <ul style={{ paddingLeft: '22px', marginTop: '8px', lineHeight: 1.6 }}>
              <li><strong>Document & Specialty Classification:</strong> Deterministic regex-anchored NLP classifiers assign documents to clinical modalities (Neurovascular CTA, Brain MRI, Clinical Pathology/Labs).</li>
              <li><strong>Provenance-Linked Parameter Extraction:</strong> Extracts numerical biomarkers and imaging signs alongside exact verbatim source quotations for clinical auditability.</li>
              <li><strong>Decision Node Traversal Paths ("Node Points"):</strong> Executes step-by-step split criteria that mirror clinical guidelines (e.g. AHA/ASA acute stroke protocols, KDIGO CKD guidelines).</li>
              <li><strong>Weighted Clinical Scoring Rubric:</strong> Computes objective, verifiable evidence scores based on explicit point-factor criteria rather than opaque black-box heuristics.</li>
            </ul>
          </div>

          <div className="model-spec-grid">
            <div className="model-spec-item">
              <div className="model-spec-label">Architecture Type</div>
              <div className="model-spec-val">Hybrid NLP + Rule-Based Decision Trees</div>
            </div>
            <div className="model-spec-item">
              <div className="model-spec-label">Current Version</div>
              <div className="model-spec-val">v1.2.0 (Clinical Triage Edition)</div>
            </div>
            <div className="model-spec-item">
              <div className="model-spec-label">Input Formats</div>
              <div className="model-spec-val">PDF, Plaintext Reports, Clinical OCR</div>
            </div>
            <div className="model-spec-item">
              <div className="model-spec-label">Validation Framework</div>
              <div className="model-spec-val">Blinded Synthetic Multi-Modal Benchmark</div>
            </div>
          </div>
        </div>

        {/* Training & Reference Validation Data */}
        <div className="model-card-section">
          <div className="model-section-title">
            <Database size={20} color="var(--accent-primary)" />
            <span>2. Reference Cohorts & Validation Data</span>
          </div>
          <div className="model-section-content">
            <p>
              <strong>Validation Dataset Declaration:</strong> The live benchmark suite evaluates the system against the <strong>Northstar & Riverbend Blinded Clinical Benchmark Suite (N = 12 blinded cases)</strong>.
            </p>
            <p style={{ marginTop: '8px' }}>
              To ensure rigorous safety validation without regulatory patient privacy compromises during academic evaluation, these cases comprise high-fidelity synthetic clinical records structured identically to real-world multi-center clinical notes. The cohort includes 7 disease-positive pathology cases (e.g. emergent Right M1 MCA occlusion, high-grade intra-axial glioblastoma, microcytic iron deficiency, Hashimoto's thyroiditis, Stage 3 CKD) and 5 hard negative controls (unremarkable brain MRI, normal CTA, benign dural meningioma, subacute non-neoplastic infarct, optimal homeostasis lab checkup).
            </p>
            <div style={{ background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '12px 16px', marginTop: '10px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <strong>Blinded Test Integrity:</strong> All 12 validation cases are evaluated in an isolated evaluation harness with ground-truth labels hidden from the inference pipeline until metric computation.
            </div>
          </div>
        </div>

        {/* Intended Use & Clinical Scope */}
        <div className="model-card-section">
          <div className="model-section-title">
            <Shield size={20} color="var(--accent-primary)" />
            <span>3. Intended Use & Clinical Scope</span>
          </div>
          <div className="model-section-content">
            <p>
              HealthGuard AI is designed strictly as an <strong>assistive triage, clinical education, and decision-support tool</strong>.
            </p>
            <ul style={{ paddingLeft: '22px', marginTop: '8px', lineHeight: 1.6 }}>
              <li><strong>Appropriate Use:</strong> Accelerating clinical intake, cross-referencing extracted lab values against guideline-defined thresholds, highlighting anatomical laterality contradictions, and recommending standardized follow-up workup pathways.</li>
              <li><strong>Prohibited / Inappropriate Use:</strong> Autonomous or unsupervised medical diagnosis, direct patient-administered triage without licensed clinician review, or sole basis for invasive surgical interventions.</li>
            </ul>
          </div>
        </div>

        {/* Scoring Rubric Methodology */}
        <div className="model-card-section">
          <div className="model-section-title">
            <Scale size={20} color="var(--accent-primary)" />
            <span>4. Mathematical Scoring Rubric Methodology</span>
          </div>
          <div className="model-section-content">
            <p>
              Prior iterations presented confidence numbers without explicit formal derivations. In Release v1.2.0, every Evidence Score (e.g. 94/100) is calculated via an explicit <strong>Weighted Point-Factor Clinical Decision Rubric</strong>:
            </p>
            <div style={{ background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '14px 18px', margin: '10px 0', fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--text-title)' }}>
              Total Evidence Score = &Sigma; (Point-Factor Weight &times; Condition Verified Status)
            </div>
            <p>
              For example, in acute neurovascular stroke evaluation, points are allocated as follows:
            </p>
            <ul style={{ paddingLeft: '22px', marginTop: '8px', lineHeight: 1.6 }}>
              <li><strong>+30 Points:</strong> Radiographic CTA visualization of abrupt proximal arterial trunk cut-off (M1 segment occlusion).</li>
              <li><strong>+25 Points:</strong> Matching contralateral acute focal neurological deficit (e.g. left-sided hemiparesis).</li>
              <li><strong>+20 Points:</strong> Definitive baseline noncontrast CT exclusion of intraparenchymal or extra-axial hemorrhage.</li>
              <li><strong>+15 Points:</strong> Verification of symptom onset within viable therapeutic reperfusion window (&lt;4.5 hours).</li>
              <li><strong>+4 Points:</strong> Early cytotoxic parenchymal hypoattenuation / insular cortex gray-white differentiation loss.</li>
            </ul>
            <p style={{ marginTop: '8px' }}>
              Clinicians can view the complete itemized rubric breakdown by clicking the <strong>ⓘ</strong> icon alongside any evidence score in the report.
            </p>
          </div>
        </div>

        {/* Human-in-the-Loop Feedback Loop Architecture */}
        <div className="model-card-section">
          <div className="model-section-title">
            <UserCheck size={20} color="var(--accent-primary)" />
            <span>5. Human-in-the-Loop Feedback & Retraining Architecture</span>
          </div>
          <div className="model-section-content">
            <p>
              To eliminate closed-loop AI safety risks, HealthGuard AI integrates a persistent <strong>Human-in-the-Loop (HITL) confirmation and override mechanism</strong> on every differential diagnosis and recommendation card:
            </p>
            <ul style={{ paddingLeft: '22px', marginTop: '8px', lineHeight: 1.6 }}>
              <li><strong>✅ Clinician Confirmation:</strong> Formally logs attending physician verification of model findings.</li>
              <li><strong>✏️ Clinician Override:</strong> Permits the clinician to replace the AI impression with a corrected differential diagnosis, clinical rationale, and physician signature.</li>
              <li><strong>🚩 Flag as Incorrect:</strong> Records suspected artifacts, false positive extractions, or discordant recommendations.</li>
            </ul>
            <p style={{ marginTop: '10px' }}>
              <strong>Retraining & Active Learning Pipeline:</strong> In a production hospital deployment, all confirmed, overridden, and flagged cases are structured into an automated audit stream. Overridden and flagged cases are automatically queued for monthly retraining and threshold recalibration:
            </p>
            <div style={{ background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-sm)', padding: '12px 18px', marginTop: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
              <em>Active Retraining Cycle:</em> Clinician Override Log &rarr; Hard-Negative Sample Mining &rarr; Rule Weight Recalibration (via Platt Scaling / Bayesian threshold optimization) &rarr; Blinded Regression Benchmark Verification &rarr; Deployed Model Card Revision.
            </div>
          </div>
        </div>

        {/* Known Limitations */}
        <div className="model-card-section">
          <div className="model-section-title">
            <AlertTriangle size={20} color="var(--accent-terracotta)" />
            <span>6. Known Limitations & Failure Modes</span>
          </div>
          <div className="model-section-content">
            <ul style={{ paddingLeft: '22px', lineHeight: 1.6 }}>
              <li><strong>Pediatric Populations:</strong> The system has not been validated on pediatric imaging or neonatal lab ranges; adult reference intervals are assumed.</li>
              <li><strong>Atypical Language Dominance:</strong> While the contradiction engine flags right MCA lesions paired with expressive aphasia, it notes that 5% of right-handed and up to 30% of left-handed individuals exhibit non-dominant or bilateral language representation.</li>
              <li><strong>Pre-Analytical Specimen Artifacts:</strong> Serum hemolyzed specimens or delayed centrifugation may spuriously elevate potassium or distort liver enzyme ratios.</li>
              <li><strong>Heuristic Nature of Scores:</strong> Evidence scores reflect point-factor rubric satisfaction rather than true epidemiological disease prevalence in general outpatient clinics.</li>
            </ul>
          </div>
        </div>

        {/* Link to Benchmark Hub */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '20px', flexWrap: 'wrap', gap: '14px' }}>
          <div>
            <div style={{ fontWeight: 800, color: 'var(--text-title)' }}>Ready to inspect empirical performance?</div>
            <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Explore live accuracy, confusion matrices, and calibration curves.</div>
          </div>

          <button 
            className="analyze-main-btn" 
            style={{ width: 'auto', padding: '12px 24px' }}
            onClick={onNavigateToBenchmark}
          >
            <span>Proceed to Live Benchmark Hub</span>
            <ArrowRight size={16} />
          </button>
        </div>

      </div>

    </div>
  );
}
