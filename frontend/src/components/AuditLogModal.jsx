import React, { useState } from 'react';
import { X, Download, Trash2, CheckCircle2, AlertCircle, Edit3, Flag, Shield, User } from 'lucide-react';

export default function AuditLogModal({ isOpen, onClose, feedbackLog, onClearLog }) {
  if (!isOpen) return null;

  const [filterAction, setFilterAction] = useState('ALL');

  const filteredLog = (feedbackLog || []).filter(item => {
    if (filterAction !== 'ALL' && item.action !== filterAction) return false;
    return true;
  });

  const handleExportJSON = () => {
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(feedbackLog, null, 2));
    const downloadAnchor = document.createElement('a');
    downloadAnchor.setAttribute("href", dataStr);
    downloadAnchor.setAttribute("download", `healthguard_audit_log_${new Date().toISOString().slice(0, 10)}.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  const countConfirmed = (feedbackLog || []).filter(i => i.action === 'CONFIRMED').length;
  const countOverridden = (feedbackLog || []).filter(i => i.action === 'OVERRIDDEN').length;
  const countFlagged = (feedbackLog || []).filter(i => i.action === 'FLAGGED').length;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '840px' }}>
        
        <div className="modal-header">
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <Shield size={20} color="var(--accent-primary)" />
            <div>
              <h3 className="modal-title">Clinician Review History & Audit Feedback Log</h3>
              <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)' }}>
                Persistent record of clinician confirmations, overrides, and discrepancy flags
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          
          {/* Summary Pills Row */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            <div style={{ background: 'var(--bg-main)', padding: '12px', borderRadius: 'var(--radius-sm)', textAlign: 'center', border: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-title)', fontFamily: 'var(--font-serif)' }}>
                {feedbackLog.length}
              </div>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                Total Actions
              </div>
            </div>

            <div style={{ background: 'var(--accent-forest-bg)', padding: '12px', borderRadius: 'var(--radius-sm)', textAlign: 'center', border: '1px solid #b7dfca' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-forest)', fontFamily: 'var(--font-serif)' }}>
                {countConfirmed}
              </div>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--accent-forest)', textTransform: 'uppercase' }}>
                Confirmed
              </div>
            </div>

            <div style={{ background: 'var(--accent-cyan-bg)', padding: '12px', borderRadius: 'var(--radius-sm)', textAlign: 'center', border: '1px solid #bae6fd' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-cyan)', fontFamily: 'var(--font-serif)' }}>
                {countOverridden}
              </div>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--accent-cyan)', textTransform: 'uppercase' }}>
                Overridden
              </div>
            </div>

            <div style={{ background: 'var(--accent-terracotta-bg)', padding: '12px', borderRadius: 'var(--radius-sm)', textAlign: 'center', border: '1px solid #fecdd3' }}>
              <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--accent-terracotta)', fontFamily: 'var(--font-serif)' }}>
                {countFlagged}
              </div>
              <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--accent-terracotta)', textTransform: 'uppercase' }}>
                Flagged
              </div>
            </div>
          </div>

          {/* Action Filter Row */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px', marginTop: '6px' }}>
            <div style={{ display: 'flex', gap: '6px', alignItems: 'center' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>Filter:</span>
              {['ALL', 'CONFIRMED', 'OVERRIDDEN', 'FLAGGED'].map(act => (
                <button
                  key={act}
                  className={`tab-button ${filterAction === act ? 'active' : ''}`}
                  style={{ padding: '4px 10px', fontSize: '0.72rem' }}
                  onClick={() => setFilterAction(act)}
                >
                  {act}
                </button>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '8px' }}>
              <button 
                className="tab-button" 
                style={{ padding: '6px 12px', fontSize: '0.74rem', border: '1px solid var(--border-card)' }}
                onClick={handleExportJSON}
                disabled={feedbackLog.length === 0}
              >
                <Download size={14} />
                <span>Export Audit Log (JSON)</span>
              </button>
              
              <button 
                className="tab-button" 
                style={{ padding: '6px 12px', fontSize: '0.74rem', border: '1px solid #fda4af', color: 'var(--accent-terracotta)' }}
                onClick={onClearLog}
                disabled={feedbackLog.length === 0}
              >
                <Trash2 size={14} />
                <span>Clear</span>
              </button>
            </div>
          </div>

          {/* Table of Entries */}
          <div className="params-table-container">
            <table className="eval-table" style={{ width: '100%', fontSize: '0.78rem' }}>
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Patient / Case</th>
                  <th>Action</th>
                  <th>AI Suspected Condition</th>
                  <th>Clinician Note / Correction</th>
                  <th>Reviewer</th>
                </tr>
              </thead>
              <tbody>
                {filteredLog.length === 0 ? (
                  <tr>
                    <td colSpan={6} style={{ textAlign: 'center', padding: '24px', color: 'var(--text-muted)' }}>
                      No clinician feedback logged yet. Use the action buttons (Confirm, Override, Flag) on any differential diagnosis card.
                    </td>
                  </tr>
                ) : (
                  filteredLog.map(item => (
                    <tr key={item.id}>
                      <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.72rem', whiteSpace: 'nowrap' }}>
                        {item.timestamp}
                      </td>
                      <td>
                        <strong>{item.patient_name || item.case_id}</strong>
                      </td>
                      <td>
                        <span className={`hitl-logged-badge ${item.action.toLowerCase()}`}>
                          {item.action === 'CONFIRMED' && <CheckCircle2 size={12} />}
                          {item.action === 'OVERRIDDEN' && <Edit3 size={12} />}
                          {item.action === 'FLAGGED' && <Flag size={12} />}
                          {item.action}
                        </span>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600 }}>{item.condition_name}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>Score: {item.original_score}/100</div>
                      </td>
                      <td style={{ maxWidth: '240px' }}>
                        {item.action === 'OVERRIDDEN' && (
                          <div style={{ color: 'var(--accent-cyan)', fontWeight: 700, marginBottom: '2px' }}>
                            Correction: {item.override_text}
                          </div>
                        )}
                        <div style={{ fontStyle: 'italic', color: 'var(--text-secondary)' }}>
                          {item.override_reason || "Verified and accepted findings."}
                        </div>
                      </td>
                      <td style={{ fontSize: '0.72rem', color: 'var(--text-secondary)' }}>
                        {item.clinician_id}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

        </div>

        <div className="modal-footer">
          <button 
            className="analyze-main-btn" 
            style={{ width: 'auto', padding: '8px 18px', fontSize: '0.8rem' }}
            onClick={onClose}
          >
            Close Audit Log
          </button>
        </div>

      </div>
    </div>
  );
}
