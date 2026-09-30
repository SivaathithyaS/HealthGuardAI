import React from 'react';
import { 
  AlertTriangle, ShieldAlert, ArrowRight, CheckCircle2, User, 
  Calendar, FileText, AlertOctagon, Heart, Activity, Stethoscope 
} from 'lucide-react';

export default function SummaryView({ analysisResult, onSwitchToClinicianView }) {
  if (!analysisResult) return null;

  const summary = analysisResult.plain_language_summary;
  const score = analysisResult.ai_evidence_score || 0;

  // Derive 3-tier label (0-40 Low, 41-75 Moderate, 76-100 High) without showing raw numbers
  let concernLabel = "High — Immediate Review Required";
  let concernClass = "critical";
  if (score < 41) {
    concernLabel = "Low Concern";
    concernClass = "low";
  } else if (score < 76) {
    concernLabel = "Moderate — Review Recommended";
    concernClass = "moderate";
  }

  const urgencyTier = summary?.urgency_tier || (
    score >= 76 
      ? "🔴 Time-Critical — Suspected High-Priority Condition, Escalate Immediately" 
      : score >= 41 
        ? "🟠 Moderate — Clinical Assessment & Follow-up Recommended" 
        : "🟢 Low Concern — Routine Clinical Monitoring"
  );

  const headline = summary?.headline || `Clinical Summary for ${analysisResult.patient_context?.name || "Patient"}`;

  const bullets = summary?.plain_language_bullets || [
    "Key laboratory or imaging indicators fall outside healthy reference ranges.",
    "Findings require clinical review to determine optimal short-term and long-term care plans.",
    "Comprehensive full-panel data and diagnostic step-by-step logic are available in the clinical report."
  ];

  const keyAction = summary?.key_action || analysisResult.required_confirmation || "Review full diagnostic findings and proceed with indicated specialist evaluation.";

  return (
    <div className="summary-container">
      
      {/* Contradiction Warning (when triggered by contradiction engine) */}
      {analysisResult.conflicting_evidence_alert && analysisResult.conflicting_evidence_alert.conflict_detected && (
        <div className="conflicting-evidence-card">
          <div className="conflict-header">
            <AlertOctagon size={18} color="#dc2626" />
            <span>{analysisResult.conflicting_evidence_alert.conflict_title}</span>
          </div>
          <div className="conflict-elements">
            {analysisResult.conflicting_evidence_alert.conflicting_elements.map((el, i) => (
              <span key={i} className="conflict-element-tag">{el}</span>
            ))}
          </div>
          <div className="conflict-explanation">
            {analysisResult.conflicting_evidence_alert.clinical_explanation}
          </div>
          <div className="conflict-guidance">
            <strong>Action Guidance:</strong> {analysisResult.conflicting_evidence_alert.reconciliation_guidance}
          </div>
        </div>
      )}

      {/* Main Executive Summary Card */}
      <div className={`summary-headline-card ${concernClass}`}>
        
        {/* Urgency Badge & Concern Tier */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' }}>
          <div className={`summary-urgency-pill ${concernClass}`}>
            <AlertTriangle size={15} />
            <span>{urgencyTier}</span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Urgency Tier:
            </span>
            <span className={`summary-urgency-pill ${concernClass}`} style={{ marginBottom: 0, padding: '4px 12px' }}>
              {concernLabel}
            </span>
          </div>
        </div>

        {/* Headline Sentence in Plain Language */}
        <h2 className="summary-title">
          {headline}
        </h2>

        {/* Patient Demographics Banner */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', fontSize: '0.84rem', color: 'var(--text-secondary)', paddingBottom: '14px', borderBottom: '1px solid var(--border-subtle)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <User size={15} color="var(--accent-primary)" />
            <strong>{analysisResult.patient_context?.name}</strong>
          </div>
          <span>•</span>
          <span>Age: <strong>{analysisResult.patient_context?.age} years</strong></span>
          <span>•</span>
          <span>Sex: <strong>{analysisResult.patient_context?.gender}</strong></span>
          <span>•</span>
          <span>Specialty: <strong>{analysisResult.detected_specialty}</strong></span>
        </div>

        {/* 2-3 Plain Language Bullets (no jargon) */}
        <div className="summary-bullets-box">
          <div style={{ fontSize: '0.74rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '12px', letterSpacing: '0.04em' }}>
            Key Clinical Observations (Plain Language Breakdown)
          </div>

          {bullets.map((bullet, idx) => (
            <div key={idx} className="summary-bullet-item">
              <div className="summary-bullet-dot" />
              <span>{bullet}</span>
            </div>
          ))}
        </div>

        {/* Immediate Recommended Action */}
        <div className="summary-action-banner">
          <div className="summary-action-text">
            <strong>Immediate Priority Action:</strong> {keyAction}
          </div>

          <button 
            className="analyze-main-btn" 
            style={{ width: 'auto', padding: '12px 24px', display: 'inline-flex', alignItems: 'center', gap: '10px' }}
            onClick={onSwitchToClinicianView}
          >
            <span>View Full Clinical Report</span>
            <ArrowRight size={16} />
          </button>
        </div>

      </div>

      {/* Advisory Notice */}
      <div className="ai-safety-banner" style={{ marginTop: '4px' }}>
        <ShieldAlert size={18} className="ai-safety-icon" />
        <div>
          <div className="ai-safety-title">Clinical Decision Support Triage Notice</div>
          <div className="ai-safety-text">
            Summary View is designed for high-level clinical communication and non-specialist review. All raw biomarker measurements, 3-tier evidence provenance, and differential rankings remain fully accessible in the Clinician View.
          </div>
        </div>
      </div>

    </div>
  );
}
