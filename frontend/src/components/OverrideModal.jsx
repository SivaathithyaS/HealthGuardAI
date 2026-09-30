import React, { useState } from 'react';
import { X, Edit3, Flag, Check, User } from 'lucide-react';

export default function OverrideModal({ isOpen, onClose, data, onSubmitFeedback }) {
  if (!isOpen || !data) return null;

  const { action, diffItem, patientName, caseId } = data;
  const isOverride = action === 'OVERRIDDEN';

  const [correctedCondition, setCorrectedCondition] = useState(
    isOverride ? `${diffItem.condition_name} (Atypical Variant)` : ''
  );
  const [rationale, setRationale] = useState('');
  const [clinicianId, setClinicianId] = useState('Dr. M. Chen, MD (Attending)');

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmitFeedback({
      action,
      diffItem,
      correctedCondition: isOverride ? correctedCondition : null,
      rationale: rationale.trim() || (isOverride ? "Diagnostic impression modified per clinical correlation." : "Flagged for specialist re-review."),
      clinicianId: clinicianId.trim() || "Attending Physician"
    });
    onClose();
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '580px' }}>
        
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            {isOverride ? (
              <Edit3 size={20} color="var(--accent-cyan)" />
            ) : (
              <Flag size={20} color="var(--accent-terracotta)" />
            )}
            <div>
              <h3 className="modal-title">
                {isOverride ? 'Clinician Override: Modify AI Diagnostic Finding' : 'Flag AI Output as Incorrect / Discordant'}
              </h3>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                Original AI Output: <strong>{diffItem.condition_name}</strong> ({diffItem.ai_evidence_score}/100)
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            
            {isOverride ? (
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-title)', marginBottom: '6px' }}>
                  Corrected Clinical Diagnosis / Impression: *
                </label>
                <input
                  type="text"
                  required
                  value={correctedCondition}
                  onChange={(e) => setCorrectedCondition(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-card)',
                    background: 'var(--bg-main)',
                    fontSize: '0.86rem',
                    color: 'var(--text-title)',
                    fontFamily: 'inherit'
                  }}
                  placeholder="e.g. Subacute Non-Arteritic Ischemia / Alternative Etiology"
                />
              </div>
            ) : (
              <div style={{ background: 'var(--accent-terracotta-bg)', border: '1px solid #fecdd3', borderRadius: 'var(--radius-sm)', padding: '12px 16px', fontSize: '0.8rem', color: 'var(--accent-terracotta)' }}>
                <strong>Flagging for Audit:</strong> This output will be flagged as incorrect or non-concordant. It will be recorded in the clinical audit trail for retraining and false-positive suppression.
              </div>
            )}

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-title)', marginBottom: '6px' }}>
                Clinical Rationale & Supporting Exam / Lab Evidence: *
              </label>
              <textarea
                required
                rows={4}
                value={rationale}
                onChange={(e) => setRationale(e.target.value)}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-card)',
                  background: 'var(--bg-main)',
                  fontSize: '0.84rem',
                  color: 'var(--text-title)',
                  fontFamily: 'inherit',
                  resize: 'vertical'
                }}
                placeholder={isOverride ? "State clinical reasons, exam findings, or contraindications supporting this correction..." : "Explain why this AI output is incorrect or clinically contraindicated..."}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 700, color: 'var(--text-title)', marginBottom: '6px' }}>
                Reviewing Clinician Signature / ID:
              </label>
              <input
                type="text"
                value={clinicianId}
                onChange={(e) => setClinicianId(e.target.value)}
                style={{
                  width: '100%',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-card)',
                  background: 'var(--bg-main)',
                  fontSize: '0.84rem',
                  color: 'var(--text-title)',
                  fontFamily: 'inherit'
                }}
              />
            </div>

          </div>

          <div className="modal-footer">
            <button
              type="button"
              className="tab-button"
              style={{ padding: '8px 16px', fontSize: '0.8rem', border: '1px solid var(--border-card)' }}
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="analyze-main-btn"
              style={{
                width: 'auto',
                padding: '8px 20px',
                fontSize: '0.8rem',
                background: isOverride ? 'var(--accent-primary)' : 'var(--accent-terracotta)',
                borderColor: isOverride ? 'var(--accent-primary)' : 'var(--accent-terracotta)'
              }}
            >
              <Check size={15} />
              <span>{isOverride ? 'Commit Clinician Override' : 'Confirm & Record Flag'}</span>
            </button>
          </div>
        </form>

      </div>
    </div>
  );
}
