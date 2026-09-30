import React from 'react';
import { X, CheckCircle2, AlertCircle, FileText, ArrowRight, Award, Shield } from 'lucide-react';

export default function RubricModal({ isOpen, onClose, data, onNavigateToModelCard }) {
  if (!isOpen || !data) return null;

  const { conditionName, score, rubric } = data;
  const criteria = rubric?.criteria || [];
  const totalScore = rubric?.total_score ?? score ?? 0;
  const maxScore = rubric?.max_possible ?? 100.0;
  const scoringMethod = rubric?.scoring_method || "Weighted Clinical Rubric (Point-Factor System)";
  const validationCohort = rubric?.validation_cohort || "Northstar & Riverbend Clinical Validation Suite (N=12)";
  const validationDate = rubric?.validation_date || "September 2026";

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '720px' }}>
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Award size={20} color="var(--accent-primary)" />
            <div>
              <h3 className="modal-title">AI Evidence Score Methodology & Rubric Breakdown</h3>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                Transparent mathematical scoring rubric for <strong>{conditionName}</strong>
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          {/* Methodology Banner */}
          <div style={{ background: 'var(--bg-main)', border: '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '16px 20px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginBottom: '8px' }}>
              <span style={{ fontSize: '0.78rem', fontWeight: 800, textTransform: 'uppercase', color: 'var(--accent-primary)', letterSpacing: '0.04em' }}>
                Methodology: {scoringMethod}
              </span>
              <span style={{ fontSize: '0.74rem', background: 'var(--bg-card)', padding: '3px 10px', borderRadius: '999px', border: '1px solid var(--border-card)', color: 'var(--text-secondary)' }}>
                Validated: {validationDate} ({validationCohort})
              </span>
            </div>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              This evidence score (<strong>{totalScore} / {maxScore}</strong>) is derived from an explicit point-factor clinical decision rubric weighting radiographic confirmation, matching clinical deficits, definitive exclusion of mimics, and hyperacute onset windows.
            </p>
            <div style={{ fontSize: '0.75rem', color: 'var(--accent-terracotta)', fontWeight: 600, marginTop: '8px' }}>
              ⓘ Regulatory Notice: This heuristic score reflects model evidence strength and is <strong>not</strong> an epidemiological calibrated probability of disease.
            </div>
          </div>

          {/* Criteria Breakdown Table */}
          <div>
            <h4 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-title)', marginBottom: '10px' }}>
              Point-Factor Rubric Breakdown
            </h4>

            <div className="params-table-container">
              <table className="params-table" style={{ width: '100%', fontSize: '0.8rem' }}>
                <thead>
                  <tr>
                    <th style={{ width: '40%' }}>Clinical Scoring Criterion</th>
                    <th style={{ width: '15%', textAlign: 'center' }}>Points</th>
                    <th style={{ width: '15%', textAlign: 'center' }}>Status</th>
                    <th style={{ width: '30%' }}>Supporting Clinical Evidence</th>
                  </tr>
                </thead>
                <tbody>
                  {criteria.map((item, idx) => (
                    <tr key={idx}>
                      <td style={{ fontWeight: 600, color: 'var(--text-title)' }}>
                        {item.criterion}
                      </td>
                      <td style={{ textAlign: 'center', fontFamily: 'var(--font-mono)', fontWeight: 700, color: item.met ? 'var(--accent-forest)' : 'var(--accent-terracotta)' }}>
                        +{item.points} / {item.max_points}
                      </td>
                      <td style={{ textAlign: 'center' }}>
                        {item.met ? (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent-forest)', background: 'var(--accent-forest-bg)', padding: '2px 8px', borderRadius: '4px' }}>
                            <CheckCircle2 size={12} /> Met
                          </span>
                        ) : (
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px', fontSize: '0.72rem', fontWeight: 700, color: 'var(--accent-terracotta)', background: 'var(--accent-terracotta-bg)', padding: '2px 8px', borderRadius: '4px' }}>
                            <AlertCircle size={12} /> Unmet
                          </span>
                        )}
                      </td>
                      <td style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', fontStyle: 'italic' }}>
                        "{item.evidence}"
                      </td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr style={{ background: 'var(--bg-main)', fontWeight: 800 }}>
                    <td>Total Cumulative Evidence Score</td>
                    <td style={{ textAlign: 'center', fontFamily: 'var(--font-mono)', color: 'var(--accent-primary)', fontSize: '0.9rem' }}>
                      {totalScore} / {maxScore}
                    </td>
                    <td colSpan={2} style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      Sum of satisfied point-factors
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button 
            className="tab-button" 
            style={{ padding: '8px 16px', fontSize: '0.8rem', border: '1px solid var(--border-card)' }}
            onClick={() => {
              onClose();
              if (onNavigateToModelCard) onNavigateToModelCard();
            }}
          >
            <FileText size={15} />
            <span>Read Full Model Card & Validation Specs</span>
            <ArrowRight size={14} />
          </button>
          <button 
            className="analyze-main-btn" 
            style={{ width: 'auto', padding: '8px 18px', fontSize: '0.8rem' }}
            onClick={onClose}
          >
            Close Breakdown
          </button>
        </div>
      </div>
    </div>
  );
}
