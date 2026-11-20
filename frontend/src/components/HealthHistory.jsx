
import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity, Calendar, ChevronDown, ChevronUp, Clock,
  HeartPulse, RefreshCw, ShieldCheck, TrendingDown, TrendingUp,
  AlertTriangle, CheckCircle2, BarChart3, Brain, Droplet, Eye,
  Stethoscope, Info, Minus, Sparkles, FileText, RotateCcw, Trash2
} from 'lucide-react';

import { API_BASE } from '../config';

// ─────────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────────

const MODALITY_META = {
  BRAIN_MRI_REPORT:  { label: 'Brain MRI',       icon: Brain,       color: '#6366f1' },
  BRAIN_CT_REPORT:   { label: 'Brain CT',         icon: Brain,       color: '#8b5cf6' },
  LAB_REPORT:        { label: 'Lab Report',        icon: Droplet,     color: '#0ea5e9' },
  ECG_REPORT:        { label: 'ECG',               icon: Activity,    color: '#f43f5e' },
  HEART:             { label: 'Cardiology',        icon: HeartPulse,  color: '#e11d48' },
  DIABETES:          { label: 'Diabetes',          icon: Droplet,     color: '#06b6d4' },
  CKD:               { label: 'Kidney Disease',    icon: ShieldCheck, color: '#10b981' },
  LIVER:             { label: 'Liver Health',      icon: Activity,    color: '#f59e0b' },
  STROKE_CT:         { label: 'Stroke / CT',       icon: Brain,       color: '#a855f7' },
  ECG_CNN:           { label: 'ECG Imaging',       icon: Activity,    color: '#ef4444' },
  MRI_CNN:           { label: 'MRI Imaging',       icon: Brain,       color: '#8b5cf6' },
  UNKNOWN:           { label: 'Clinical Report',   icon: Stethoscope, color: '#64748b' },
};

function getModalityMeta(modality) {
  const key = (modality || '').toUpperCase();
  return MODALITY_META[key] || MODALITY_META.UNKNOWN;
}

function riskColor(score) {
  if (score >= 70) return 'var(--critical-accent, #B5522E)';
  if (score >= 40) return 'var(--moderate-accent, #B5901F)';
  return 'var(--brand-accent, #0E6B64)';
}

function riskLabel(score) {
  if (score >= 70) return 'High Risk';
  if (score >= 40) return 'Moderate Risk';
  return 'Low Risk';
}

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleString('en-IN', {
      day: '2-digit', month: 'short', year: 'numeric',
      hour: '2-digit', minute: '2-digit'
    });
  } catch { return iso; }
}

// ─────────────────────────────────────────────────────────────────────────────
// DeltaBadge
// ─────────────────────────────────────────────────────────────────────────────
function DeltaBadge({ delta }) {
  const impact = delta.impact;
  const isConcerning = impact === 'concerning';
  const isImproving = impact === 'improving';
  const iconColor = isConcerning ? 'var(--critical-accent, #B5522E)' : isImproving ? 'var(--brand-accent, #0E6B64)' : 'var(--text-muted, #8B948E)';
  const textColor = isConcerning ? 'var(--critical-text, #8A3D22)' : isImproving ? 'var(--good-text, #2E5944)' : 'var(--text-secondary, #4F5A54)';
  const Icon = isConcerning ? TrendingUp : isImproving ? TrendingDown : Minus;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '10px',
      padding: '8px 12px',
      background: 'var(--bg-surface, #FFFFFF)',
      border: '1px solid var(--border-subtle, #EDEFEC)',
      borderRadius: '6px',
      fontSize: '12.5px'
    }}>
      <Icon size={13} color={iconColor} />
      <span style={{ color: 'var(--text-primary)', fontWeight: 500, flex: 1 }}>{delta.biomarker}</span>
      <span style={{ color: 'var(--text-muted)', fontSize: '12px', fontFamily: 'var(--font-mono)' }}>{delta.prior_value} → </span>
      <span style={{ color: textColor, fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{delta.current_value} {delta.unit}</span>
      <span style={{ color: textColor, fontSize: '11px', fontWeight: 600, marginLeft: '4px' }}>{delta.delta}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// NarrativePanel — renders LLM/template narrative
// ─────────────────────────────────────────────────────────────────────────────
function NarrativePanel({ narrative, checkupId, token, onRegenerate }) {
  const [regenerating, setRegenerating] = useState(false);

  if (!narrative) return null;

  const isLlm = narrative.narrative_source === 'llm';
  const sourceLabel = isLlm ? 'AI-assisted longitudinal narrative' : 'Clinical summary narrative';
  const SourceIcon = isLlm ? Sparkles : FileText;

  const handleRegenerate = async () => {
    setRegenerating(true);
    try {
      await fetch(`${API_BASE}/api/auth/history/${checkupId}/narrative/regenerate`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      if (onRegenerate) onRegenerate();
    } catch (e) {
      console.error('Regenerate failed', e);
    } finally {
      setRegenerating(false);
    }
  };

  return (
    <div style={{
      borderRadius: '8px', overflow: 'hidden',
      border: '1px solid var(--border-subtle, #EDEFEC)',
      background: 'var(--bg-surface, #FFFFFF)',
      marginTop: '12px',
    }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', gap: '8px',
        padding: '10px 14px',
        borderBottom: '1px solid var(--border-subtle, #EDEFEC)',
        background: 'var(--bg-page, #F4F5F3)',
      }}>
        <SourceIcon size={13} color="var(--brand-accent, #0E6B64)" />
        <span style={{ fontSize: '12px', color: 'var(--text-secondary, #4F5A54)', fontWeight: 600, flex: 1 }}>
          {sourceLabel}
        </span>
        <button
          onClick={handleRegenerate}
          disabled={regenerating}
          title="Regenerate narrative"
          style={{
            display: 'flex', alignItems: 'center', gap: '4px',
            padding: '3px 8px', borderRadius: '4px',
            background: 'var(--bg-surface, #FFFFFF)',
            border: '1px solid var(--border-default, #E3E6E2)',
            color: 'var(--text-secondary, #4F5A54)', fontSize: '11px',
            cursor: regenerating ? 'not-allowed' : 'pointer',
          }}
        >
          <RotateCcw size={10} style={{ animation: regenerating ? 'spin 1s linear infinite' : 'none' }} />
          {regenerating ? 'Regenerating…' : 'Regenerate'}
        </button>
      </div>

      <div style={{ padding: '14px 16px' }}>
        {/* Headline */}
        {narrative.headline && (
          <div style={{
            fontSize: '13.5px', fontWeight: 600, color: 'var(--text-primary)',
            marginBottom: '12px', lineHeight: 1.45,
          }}>
            {narrative.headline}
          </div>
        )}

        {/* Improved group */}
        {narrative.improved && narrative.improved.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{
              fontSize: '11px', fontWeight: 600, color: 'var(--good-text, #2E5944)',
              letterSpacing: '0.06em', marginBottom: '6px',
              display: 'flex', alignItems: 'center', gap: '5px'
            }}>
              <TrendingDown size={12} color="var(--brand-accent, #0E6B64)" />
              <span>IMPROVED METRICS</span>
            </div>
            {narrative.improved.map((b, i) => (
              <div key={i} style={{
                padding: '9px 12px', borderRadius: '6px',
                background: 'var(--bg-surface, #FFFFFF)',
                border: '1px solid var(--border-subtle, #EDEFEC)',
                marginBottom: '6px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px' }}>
                    {b.biomarker}
                  </span>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: '11.5px', color: 'var(--text-secondary)',
                    background: 'var(--bg-page, #F4F5F3)', padding: '2px 7px', borderRadius: '4px',
                    border: '1px solid var(--border-subtle, #EDEFEC)'
                  }}>
                    {b.from} → {b.to} {b.unit}
                  </span>
                </div>
                {b.note && (
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '3px' }}>{b.note}</div>
                )}
                {b.clinical_significance && (
                  <div style={{
                    fontSize: '12px', color: 'var(--text-secondary, #4F5A54)',
                    marginTop: '5px', paddingTop: '5px',
                    borderTop: '1px dashed var(--border-subtle, #EDEFEC)',
                    lineHeight: 1.5
                  }}>
                    {b.clinical_significance}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Worsened group */}
        {narrative.worsened && narrative.worsened.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{
              fontSize: '11px', fontWeight: 600, color: 'var(--critical-text, #8A3D22)',
              letterSpacing: '0.06em', marginBottom: '6px',
              display: 'flex', alignItems: 'center', gap: '5px'
            }}>
              <TrendingUp size={12} color="var(--critical-accent, #B5522E)" />
              <span>ATTENTION NEEDED</span>
            </div>
            {narrative.worsened.map((b, i) => (
              <div key={i} style={{
                padding: '9px 12px', borderRadius: '6px',
                background: 'var(--bg-surface, #FFFFFF)',
                border: '1px solid var(--border-subtle, #EDEFEC)',
                marginBottom: '6px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px' }}>
                    {b.biomarker}
                  </span>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: '11.5px', color: 'var(--text-secondary)',
                    background: 'var(--bg-page, #F4F5F3)', padding: '2px 7px', borderRadius: '4px',
                    border: '1px solid var(--border-subtle, #EDEFEC)'
                  }}>
                    {b.from} → {b.to} {b.unit}
                  </span>
                </div>
                {b.note && (
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '3px' }}>{b.note}</div>
                )}
                {b.clinical_significance && (
                  <div style={{
                    fontSize: '12px', color: 'var(--text-secondary, #4F5A54)',
                    marginTop: '5px', paddingTop: '5px',
                    borderTop: '1px dashed var(--border-subtle, #EDEFEC)',
                    lineHeight: 1.5
                  }}>
                    {b.clinical_significance}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Unchanged group */}
        {narrative.unchanged && narrative.unchanged.length > 0 && (
          <div style={{ marginBottom: '12px' }}>
            <div style={{
              fontSize: '11px', fontWeight: 600, color: 'var(--text-secondary, #4F5A54)',
              letterSpacing: '0.06em', marginBottom: '6px',
              display: 'flex', alignItems: 'center', gap: '5px'
            }}>
              <Minus size={12} color="var(--text-muted, #8B948E)" />
              <span>STABLE / UNCHANGED</span>
            </div>
            {narrative.unchanged.map((b, i) => (
              <div key={i} style={{
                padding: '9px 12px', borderRadius: '6px',
                background: 'var(--bg-surface, #FFFFFF)',
                border: '1px solid var(--border-subtle, #EDEFEC)',
                marginBottom: '6px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', flexWrap: 'wrap' }}>
                  <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '13px' }}>
                    {b.biomarker}
                  </span>
                  <span style={{
                    fontFamily: 'var(--font-mono)', fontSize: '11.5px', color: 'var(--text-secondary)',
                    background: 'var(--bg-page, #F4F5F3)', padding: '2px 7px', borderRadius: '4px',
                    border: '1px solid var(--border-subtle, #EDEFEC)'
                  }}>
                    {b.from} → {b.to} {b.unit}
                  </span>
                </div>
                {b.note && (
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '3px' }}>{b.note}</div>
                )}
                {b.clinical_significance && (
                  <div style={{
                    fontSize: '12px', color: 'var(--text-secondary, #4F5A54)',
                    marginTop: '5px', paddingTop: '5px',
                    borderTop: '1px dashed var(--border-subtle, #EDEFEC)',
                    lineHeight: 1.5
                  }}>
                    {b.clinical_significance}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Summary paragraph */}
        {narrative.summary && (
          <p style={{
            fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6,
            marginTop: '10px', marginBottom: narrative.caveats?.length ? '8px' : 0,
          }}>
            {narrative.summary}
          </p>
        )}

        {/* Caveats */}
        {narrative.caveats && narrative.caveats.length > 0 && (
          <div style={{ marginTop: '8px' }}>
            {narrative.caveats.map((c, i) => (
              <div key={i} style={{
                fontSize: '11.5px', color: 'var(--text-muted)',
                display: 'flex', gap: '6px', alignItems: 'flex-start', marginBottom: '3px',
              }}>
                <Info size={11} style={{ marginTop: '2px', flexShrink: 0 }} />
                <span>{c}</span>
              </div>
            ))}
          </div>
        )}

        {/* Overall Current Health Condition Assessment */}
        {narrative.overall_assessment && (
          <div style={{
            marginTop: '12px', padding: '12px 14px', borderRadius: '8px',
            background: 'var(--bg-page, #F4F5F3)',
            border: '1px solid var(--border-default, #E3E6E2)',
            fontSize: '12.5px', lineHeight: 1.6, color: 'var(--text-primary)'
          }}>
            <div style={{
              fontSize: '11px', fontWeight: 700, color: 'var(--brand-ink, #0E3B38)',
              letterSpacing: '0.06em', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px'
            }}>
              <Activity size={12} color="var(--brand-accent, #0E6B64)" />
              OVERALL HEALTH ASSESSMENT
            </div>
            <div style={{ color: 'var(--text-secondary)' }}>{narrative.overall_assessment}</div>
          </div>
        )}

        {/* Practical Health Tips to Improve */}
        {narrative.health_tips && narrative.health_tips.length > 0 && (
          <div style={{
            marginTop: '10px', padding: '12px 14px', borderRadius: '8px',
            background: 'var(--bg-page, #F4F5F3)',
            border: '1px solid var(--border-default, #E3E6E2)',
            fontSize: '12.5px', lineHeight: 1.6
          }}>
            <div style={{
              fontSize: '11px', fontWeight: 700, color: 'var(--brand-ink, #0E3B38)',
              letterSpacing: '0.06em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px'
            }}>
              <Sparkles size={12} color="var(--brand-accent, #0E6B64)" />
              LIFESTYLE & CLINICAL RECOMMENDATIONS
            </div>
            <ul style={{ margin: 0, paddingLeft: '18px', display: 'flex', flexDirection: 'column', gap: '5px', color: 'var(--text-secondary)' }}>
              {narrative.health_tips.map((tip, idx) => (
                <li key={idx} style={{ fontSize: '12px', lineHeight: 1.5 }}>{tip}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckupCard
// ─────────────────────────────────────────────────────────────────────────────
function CheckupCard({ checkup, onDelete }) {
  const [expanded, setExpanded] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const meta = getModalityMeta(checkup.modality);
  const IconComp = meta.icon;
  const numScore = typeof checkup.risk_score === 'number' 
    ? checkup.risk_score 
    : (parseFloat(checkup.risk_score) || 0);
  const rc = riskColor(numScore);

  const handleDelete = (e) => {
    e.stopPropagation();
    setDeleting(true);
    onDelete(checkup.id);
  };

  return (
    <div style={{
      background: 'var(--bg-surface, #FFFFFF)',
      border: '1px solid var(--border-default, #E3E6E2)',
      borderRadius: '12px',
      overflow: 'hidden',
      transition: 'box-shadow 0.2s',
      opacity: deleting ? 0.4 : 1
    }}>
      {/* Header row */}
      <div
        onClick={() => setExpanded(e => !e)}
        style={{
          display: 'flex', alignItems: 'center', gap: '14px',
          width: '100%', padding: '14px 18px',
          background: 'transparent', cursor: 'pointer',
          textAlign: 'left', userSelect: 'none'
        }}
      >
        {/* Modality icon */}
        <div style={{
          width: 36, height: 36, borderRadius: '8px', flexShrink: 0,
          background: `${meta.color}14`, display: 'flex', alignItems: 'center', justifyContent: 'center'
        }}>
          <IconComp size={18} color={meta.color} />
        </div>

        {/* Title + date */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: '14px', fontWeight: 600,
            color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap'
          }}>
            {checkup.title}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Clock size={11} />
            {formatDate(checkup.created_at)}
            <span style={{
              marginLeft: '6px', padding: '1px 7px', borderRadius: '10px', fontSize: '11px',
              background: `${meta.color}15`, color: meta.color, fontWeight: 600
            }}>{meta.label}</span>
          </div>
        </div>

        {/* Risk score */}
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: '18px', fontWeight: 800, color: rc, lineHeight: 1 }}>
            {numScore.toFixed(1)}
          </div>
          <div style={{ fontSize: '10px', color: rc, fontWeight: 600, marginTop: '2px' }}>
            {riskLabel(numScore)}
          </div>
        </div>

        {/* Delete button */}
        {onDelete && (
          <button
            type="button"
            onClick={handleDelete}
            title="Delete checkup record"
            aria-label="Delete checkup record"
            style={{
              padding: '6px 8px',
              borderRadius: '6px',
              color: 'var(--text-muted, #8B948E)',
              background: 'transparent',
              border: '1px solid transparent',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.15s ease',
              marginLeft: '4px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.color = 'var(--critical-accent, #B5522E)';
              e.currentTarget.style.background = 'var(--critical-bg, #FBF0EC)';
              e.currentTarget.style.borderColor = 'var(--critical-border, #E8C9BC)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.color = 'var(--text-muted, #8B948E)';
              e.currentTarget.style.background = 'transparent';
              e.currentTarget.style.borderColor = 'transparent';
            }}
          >
            <Trash2 size={15} />
          </button>
        )}

        {/* Expand toggle */}
        <div style={{ color: 'var(--text-muted)', flexShrink: 0, marginLeft: '2px' }}>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </div>

      {/* Expanded detail */}
      {expanded && (
        <div style={{ padding: '0 18px 18px 18px', borderTop: '1px solid var(--border-subtle, #EDEFEC)' }}>
          {/* Summary */}
          {checkup.summary && (
            <p style={{
              fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6,
              marginTop: '14px', marginBottom: '12px'
            }}>
              {checkup.summary}
            </p>
          )}

          {/* Findings */}
          {checkup.findings && checkup.findings.length > 0 && (
            <div style={{ marginBottom: '12px' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '8px' }}>KEY FINDINGS</div>
              {checkup.findings.slice(0, 5).map((f, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-primary)', marginBottom: '5px' }}>
                  <AlertTriangle size={12} color="var(--moderate-accent, #B5901F)" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>{f}</span>
                </div>
              ))}
            </div>
          )}

          {/* Recommendations */}
          {checkup.recommendations && checkup.recommendations.length > 0 && (
            <div>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '8px' }}>RECOMMENDATIONS</div>
              {checkup.recommendations.slice(0, 4).map((r, i) => (
                <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '8px', fontSize: '13px', color: 'var(--text-primary)', marginBottom: '5px' }}>
                  <CheckCircle2 size={12} color="var(--brand-accent, #0E6B64)" style={{ marginTop: '2px', flexShrink: 0 }} />
                  <span>{r}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// LongitudinalPanel
// ─────────────────────────────────────────────────────────────────────────────
function LongitudinalPanel({ data, narrative, checkupId, token, onRegenerate }) {
  const status = data?.status || '';
  const trajectory = data?.trajectory_status || data?.trajectory || '';

  if (!data || (!data.has_prior_history && status === 'BASELINE') || status === 'BASELINE') {
    return (
      <div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px 16px', borderRadius: '8px',
          background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E3E6E2)',
          fontSize: '13px', color: 'var(--text-secondary)'
        }}>
          <Info size={15} color="var(--brand-accent, #0E6B64)" />
          <span>{data?.message || data?.summary_advice || 'No prior visits on record. This is your baseline visit.'}</span>
        </div>
        {narrative && (
          <NarrativePanel
            narrative={narrative}
            checkupId={checkupId}
            token={token}
            onRegenerate={onRegenerate}
          />
        )}
      </div>
    );
  }

  if (status === 'NOT_COMPARABLE') {
    return (
      <div>
        <div style={{
          display: 'flex', alignItems: 'center', gap: '10px',
          padding: '12px 16px', borderRadius: '8px',
          background: 'var(--bg-surface, #FFFFFF)', border: '1px solid var(--border-default, #E3E6E2)',
          fontSize: '13px', color: 'var(--text-secondary)'
        }}>
          <Info size={15} color="var(--text-muted, #8B948E)" />
          <span>{data?.not_comparable_reason || data?.summary_advice || 'No comparable prior visit found for trajectory comparison.'}</span>
        </div>
        {narrative && (
          <NarrativePanel
            narrative={narrative}
            checkupId={checkupId}
            token={token}
            onRegenerate={onRegenerate}
          />
        )}
      </div>
    );
  }

  const isMixed = trajectory === 'MIXED';
  const badgeConfig = (() => {
    if (trajectory === 'FAVORABLE_TRAJECTORY') {
      return {
        label: 'Favorable Trajectory',
        Icon: TrendingDown,
        color: 'var(--good-text, #2E5944)',
        bg: 'var(--good-bg, #EAF2EC)',
        border: 'var(--good-border, #CFE3D5)'
      };
    }
    if (trajectory === 'ATTENTION_REQUIRED') {
      return {
        label: 'Needs Clinical Attention',
        Icon: AlertTriangle,
        color: 'var(--critical-text, #8A3D22)',
        bg: 'var(--critical-bg, #FBF0EC)',
        border: 'var(--critical-border, #E8C9BC)'
      };
    }
    if (isMixed) {
      return {
        label: 'Mixed Findings',
        Icon: Activity,
        color: 'var(--moderate-text, #8A6A1F)',
        bg: 'var(--moderate-bg, #FBF5E6)',
        border: 'var(--moderate-border, #E7D9B0)'
      };
    }
    return {
      label: (trajectory || 'Baseline Established').replace(/_/g, ' '),
      Icon: Activity,
      color: 'var(--text-secondary, #4F5A54)',
      bg: 'var(--bg-page, #F4F5F3)',
      border: 'var(--border-default, #E3E6E2)'
    };
  })();

  const BadgeIcon = badgeConfig.Icon;

  return (
    <div style={{
      borderRadius: '12px', overflow: 'hidden',
      border: '1px solid var(--border-default, #E3E6E2)',
      background: 'var(--bg-surface, #FFFFFF)'
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 18px',
        background: 'var(--bg-card-hover, #F8F9F7)',
        borderBottom: '1px solid var(--border-subtle, #EDEFEC)',
        flexWrap: 'wrap', gap: '8px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{
            display: 'inline-flex', alignItems: 'center', gap: '5px',
            padding: '3px 8px', borderRadius: '4px',
            fontSize: '11px', fontWeight: 600, letterSpacing: '0.04em',
            background: badgeConfig.bg, color: badgeConfig.color, border: `1px solid ${badgeConfig.border}`
          }}>
            <BadgeIcon size={12} />
            {badgeConfig.label}
          </span>
        </div>
        <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
          {data.days_since_prior || data.days_between || 0} days since last visit • {data.total_visits_recorded} recorded visit{data.total_visits_recorded !== 1 ? 's' : ''}
        </div>
      </div>

      {/* Narrative panel (LLM or template) */}
      {narrative ? (
        <div style={{ padding: '0 16px 16px 16px' }}>
          <NarrativePanel
            narrative={narrative}
            checkupId={checkupId}
            token={token}
            onRegenerate={onRegenerate}
          />
        </div>
      ) : data.summary_advice && (
        <p style={{ padding: '14px 18px', fontSize: '13px', color: 'var(--text-secondary)', lineHeight: 1.6, margin: 0 }}>
          {data.summary_advice}
        </p>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main HealthHistory export
// ─────────────────────────────────────────────────────────────────────────────
export default function HealthHistory({ user, token, onNavigateToScanner }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const effectiveToken = token || sessionStorage.getItem('healthguard_access_token');

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/history`, {
        headers: { Authorization: `Bearer ${effectiveToken}` }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [effectiveToken]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const handleDeleteCheckup = async (id) => {
    // Optimistic UI removal
    setData(prev => {
      if (!prev) return prev;
      const updated = (prev.checkups || []).filter(c => c.id !== id);
      return {
        ...prev,
        checkups: updated,
        total: updated.length
      };
    });

    try {
      const res = await fetch(`${API_BASE}/api/auth/history/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${effectiveToken}` }
      });
      if (!res.ok) {
        console.error("Failed to delete checkup on server:", res.status);
        fetchHistory();
      } else {
        fetchHistory();
      }
    } catch (err) {
      console.error("Failed to delete checkup", err);
      fetchHistory();
    }
  };

  const handleClearHistory = async () => {
    // Optimistic UI clear
    setData(prev => ({
      ...prev,
      checkups: [],
      longitudinal: null,
      total: 0
    }));

    try {
      const res = await fetch(`${API_BASE}/api/auth/history`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${effectiveToken}` }
      });
      if (!res.ok) {
        console.error("Failed to clear history on server:", res.status);
        fetchHistory();
      }
    } catch (err) {
      console.error("Failed to clear history", err);
      fetchHistory();
    }
  };

  const checkups = data?.checkups || [];
  const longitudinal = data?.longitudinal || data?.comparison || null;
  const narrative = data?.narrative || null;
  const latestCheckupId = checkups.length > 0 ? checkups[0].id : null;

  return (
    <div style={{ maxWidth: '820px', margin: '0 auto', padding: '16px 20px 40px' }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: '20px', flexWrap: 'wrap', gap: '12px'
      }}>
        <div>
          <h2 style={{
            margin: 0, fontSize: '20px', fontWeight: 700,
            color: 'var(--text-primary)',
            display: 'flex', alignItems: 'center', gap: '10px'
          }}>
            <Calendar size={18} color="var(--brand-accent)" />
            Personal Health History
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
            Isolated longitudinal records for {user?.name || user?.email || 'Authenticated User'} • {checkups.length} recorded visit{checkups.length !== 1 ? 's' : ''}
          </p>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {checkups.length > 0 && (
            <button
              onClick={handleClearHistory}
              style={{
                padding: '7px 12px', borderRadius: '6px',
                background: 'transparent', border: '1px solid var(--border-default)',
                color: 'var(--text-muted)', fontSize: '12px', cursor: 'pointer'
              }}
            >
              Clear all
            </button>
          )}

          <button
            onClick={fetchHistory}
            disabled={loading}
            style={{
              display: 'flex', alignItems: 'center', gap: '6px',
              padding: '7px 14px', borderRadius: '6px',
              background: 'var(--bg-surface)', border: '1px solid var(--border-default)',
              color: 'var(--brand-ink)', fontWeight: 500, fontSize: '13px',
              cursor: loading ? 'not-allowed' : 'pointer'
            }}
          >
            <RefreshCw size={13} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
            {loading ? 'Refreshing…' : 'Refresh'}
          </button>
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '12px 16px', borderRadius: '8px', marginBottom: '20px',
          background: 'var(--critical-bg, #FBF0EC)', border: '1px solid var(--critical-border, #E8C9BC)',
          fontSize: '13px', color: 'var(--critical-text, #8A3D22)', display: 'flex', gap: '8px', alignItems: 'center'
        }}>
          <AlertTriangle size={15} style={{ flexShrink: 0 }} />
          <span>Could not load history: {error}</span>
        </div>
      )}

      {/* Longitudinal trajectory panel */}
      {checkups.length > 0 && longitudinal && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '10px' }}>
            <BarChart3 size={12} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            LONGITUDINAL HEALTH TRAJECTORY
          </div>
          <LongitudinalPanel
            data={longitudinal}
            narrative={narrative}
            checkupId={latestCheckupId}
            token={effectiveToken}
            onRegenerate={fetchHistory}
          />
        </div>
      )}

      {/* Checkup list */}
      {checkups.length === 0 && !loading && !error ? (
        <div style={{
          textAlign: 'center', padding: '60px 20px',
          color: 'var(--text-muted)', fontSize: '14px'
        }}>
          <h3 style={{ margin: 0, fontSize: '1.05rem', fontWeight: 600, color: 'var(--text-primary)' }}>No report scanned yet</h3>
          <p style={{ margin: '6px 0 0', fontSize: '13px', opacity: 0.7 }}>
            Upload and scan clinical documents or imaging reports to build your longitudinal timeline.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {checkups.map(c => (
            <CheckupCard 
              key={c.id} 
              checkup={c} 
              onDelete={handleDeleteCheckup} 
            />
          ))}
        </div>
      )}
    </div>
  );
}
