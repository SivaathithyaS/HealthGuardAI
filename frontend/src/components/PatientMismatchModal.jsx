import React from 'react';
import { ShieldAlert, UserPlus, LogIn, X, FileText, User } from 'lucide-react';

/**
 * PatientMismatchModal
 * ────────────────────
 * Minimal, theme-aligned prompt displayed when an uploaded report's patient name
 * does not match the active user account.
 */
export default function PatientMismatchModal({
  isOpen,
  onClose,
  patientName,
  currentUserName,
  onCreateAccount,
  onSwitchAccount
}) {
  if (!isOpen) return null;

  const displayReportName = patientName && patientName !== 'Unknown' 
    ? patientName 
    : 'Another Individual';
  const displayCurrentName = currentUserName || 'Your Account';

  return (
    <div className="modal-overlay" onClick={onClose} style={{ zIndex: 1200 }}>
      <div 
        className="modal-dialog" 
        onClick={(e) => e.stopPropagation()} 
        style={{ 
          maxWidth: '430px',
          background: 'var(--bg-surface, #FFFFFF)',
          border: '1px solid var(--border-default, #E3E6E2)',
          borderRadius: '12px',
          boxShadow: '0 18px 38px rgba(27, 36, 32, 0.16)',
          overflow: 'hidden'
        }}
      >
        {/* Header */}
        <div 
          className="modal-header" 
          style={{ 
            padding: '14px 18px',
            borderBottom: '1px solid var(--border-subtle, #EDEFEC)',
            background: 'var(--bg-surface, #FFFFFF)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '9px' }}>
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '7px',
              background: 'var(--critical-bg, #FBF0EC)',
              border: '1px solid var(--critical-border, #E8C9BC)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--critical-accent, #B5522E)'
            }}>
              <ShieldAlert size={16} />
            </div>
            <h3 
              className="modal-title" 
              style={{ 
                margin: 0, 
                fontSize: '0.98rem', 
                fontWeight: 600, 
                color: 'var(--text-primary, #1B2420)',
                fontFamily: 'var(--font-serif, "Source Serif 4", Georgia, serif)'
              }}
            >
              Patient Name Mismatch
            </h3>
          </div>
          <button 
            className="modal-close-btn" 
            onClick={onClose} 
            title="Dismiss"
            style={{ color: 'var(--text-muted, #8B948E)', padding: '2px' }}
          >
            <X size={18} />
          </button>
        </div>

        {/* Body */}
        <div style={{ padding: '16px 18px' }}>
          
          {/* Identity comparison strip */}
          <div style={{
            background: 'var(--bg-page, #F4F5F3)',
            border: '1px solid var(--border-default, #E3E6E2)',
            borderRadius: '8px',
            padding: '10px 14px',
            marginBottom: '12px'
          }}>
            {/* Report Patient */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid var(--border-subtle, #EDEFEC)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.74rem', color: 'var(--text-secondary, #4F5A54)', fontWeight: 500 }}>
                <FileText size={13} color="var(--critical-accent, #B5522E)" />
                <span>Report Patient</span>
              </div>
              <span style={{ fontSize: '0.86rem', fontWeight: 700, color: 'var(--critical-text, #8A3D22)' }}>
                {displayReportName}
              </span>
            </div>

            {/* Active Account */}
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '8px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.74rem', color: 'var(--text-secondary, #4F5A54)', fontWeight: 500 }}>
                <User size={13} color="var(--brand-accent, #0E6B64)" />
                <span>Active Account</span>
              </div>
              <span style={{ fontSize: '0.86rem', fontWeight: 600, color: 'var(--good-text, #2E5944)' }}>
                {displayCurrentName}
              </span>
            </div>
          </div>

          {/* Minimal Caution Note */}
          <div style={{
            background: 'var(--moderate-bg, #FBF5E6)',
            border: '1px solid var(--moderate-border, #E7D9B0)',
            borderRadius: '6px',
            padding: '8px 12px',
            marginBottom: '16px',
            fontSize: '0.78rem',
            lineHeight: 1.45,
            color: 'var(--text-secondary, #4F5A54)'
          }}>
            <strong style={{ color: 'var(--moderate-text, #8A6A1F)' }}>Personalized AI:</strong> HealthGuard AI is calibrated to each individual's health baseline and cannot process another person's report under this account.
          </div>

          {/* Action Buttons */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <button
              type="button"
              onClick={() => onCreateAccount(displayReportName)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '7px',
                width: '100%',
                padding: '9px 14px',
                borderRadius: '6px',
                border: 'none',
                background: 'var(--brand-ink, #0E3B38)',
                color: '#FFFFFF',
                fontSize: '0.84rem',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'background 0.15s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = '#144c48'}
              onMouseOut={(e) => e.currentTarget.style.background = 'var(--brand-ink, #0E3B38)'}
            >
              <UserPlus size={15} /> Create Account for {displayReportName}
            </button>

            <button
              type="button"
              onClick={() => onSwitchAccount(displayReportName)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '7px',
                width: '100%',
                padding: '8px 14px',
                borderRadius: '6px',
                border: '1px solid var(--border-default, #E3E6E2)',
                background: 'var(--bg-surface, #FFFFFF)',
                color: 'var(--text-primary, #1B2420)',
                fontSize: '0.82rem',
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'background 0.15s ease'
              }}
              onMouseOver={(e) => e.currentTarget.style.background = 'var(--bg-page, #F4F5F3)'}
              onMouseOut={(e) => e.currentTarget.style.background = 'var(--bg-surface, #FFFFFF)'}
            >
              <LogIn size={14} /> Sign in as {displayReportName}
            </button>

            <button
              type="button"
              onClick={onClose}
              style={{
                background: 'none',
                border: 'none',
                color: 'var(--text-muted, #8B948E)',
                fontSize: '0.78rem',
                padding: '5px',
                cursor: 'pointer',
                textAlign: 'center',
                marginTop: '2px'
              }}
              onMouseOver={(e) => e.currentTarget.style.color = 'var(--text-primary, #1B2420)'}
              onMouseOut={(e) => e.currentTarget.style.color = 'var(--text-muted, #8B948E)'}
            >
              Cancel
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}
