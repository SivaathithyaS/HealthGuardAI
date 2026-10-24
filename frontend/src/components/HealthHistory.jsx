
import React, { useState, useEffect, useCallback } from 'react';
import {
  Activity, Calendar, ChevronDown, ChevronUp, Clock,
  HeartPulse, RefreshCw, ShieldCheck, TrendingDown, TrendingUp,
  AlertTriangle, CheckCircle2, BarChart3, Brain, Droplet, Eye,
  Stethoscope, Info, Minus
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

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
  if (score >= 70) return '#ef4444';
  if (score >= 40) return '#f59e0b';
  return '#10b981';
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
  const color = impact === 'concerning' ? '#ef4444' : impact === 'improving' ? '#10b981' : '#94a3b8';
  const Icon = impact === 'concerning' ? TrendingUp : impact === 'improving' ? TrendingDown : Minus;

  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: '10px',
      padding: '10px 14px',
      background: impact === 'concerning' ? 'rgba(239,68,68,0.07)' :
                  impact === 'improving'  ? 'rgba(16,185,129,0.07)' : 'rgba(148,163,184,0.07)',
      border: `1px solid ${color}30`,
      borderRadius: '8px',
      fontSize: '13px'
    }}>
      <Icon size={14} color={color} />
      <span style={{ color: 'var(--text-primary)', fontWeight: 500, flex: 1 }}>{delta.biomarker}</span>
      <span style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{delta.prior_value} → </span>
      <span style={{ color, fontWeight: 700 }}>{delta.current_value} {delta.unit}</span>
      <span style={{ color, fontSize: '12px', fontWeight: 600 }}>{delta.delta}</span>
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// CheckupCard
// ─────────────────────────────────────────────────────────────────────────────
function CheckupCard({ checkup }) {
  const [expanded, setExpanded] = useState(false);
  const meta = getModalityMeta(checkup.modality);
  const IconComp = meta.icon;
  const rc = riskColor(checkup.risk_score);

  return (
    <div style={{
      background: 'var(--bg-card, rgba(255,255,255,0.04))',
      border: '1px solid var(--border-subtle, rgba(255,255,255,0.08))',
      borderRadius: '12px',
      overflow: 'hidden',
      transition: 'box-shadow 0.2s'
    }}>
      {/* Header row */}
      <button
        onClick={() => setExpanded(e => !e)}
        style={{
          display: 'flex', alignItems: 'center', gap: '14px',
          width: '100%', padding: '14px 18px',
          background: 'transparent', border: 'none', cursor: 'pointer',
          textAlign: 'left'
        }}
      >
        {/* Modality icon */}
        <div style={{
          width: 36, height: 36, borderRadius: '8px', flexShrink: 0,
          background: `${meta.color}1a`, display: 'flex', alignItems: 'center', justifyContent: 'center'
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
              background: `${meta.color}20`, color: meta.color, fontWeight: 600
            }}>{meta.label}</span>
          </div>
        </div>

        {/* Risk score */}
        <div style={{ textAlign: 'right', flexShrink: 0 }}>
          <div style={{ fontSize: '18px', fontWeight: 800, color: rc, lineHeight: 1 }}>
            {checkup.risk_score.toFixed(1)}
          </div>
          <div style={{ fontSize: '10px', color: rc, fontWeight: 600, marginTop: '2px' }}>
            {riskLabel(checkup.risk_score)}
          </div>
        </div>

        {/* Expand toggle */}
        <div style={{ color: 'var(--text-muted)', flexShrink: 0, marginLeft: '8px' }}>
          {expanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
        </div>
      </button>

      {/* Expanded detail */}
      {expanded && (
        <div style={{ padding: '0 18px 18px 18px', borderTop: '1px solid var(--border-subtle, rgba(255,255,255,0.06))' }}>
          {/* Summary */}
          {checkup.summary && (
            <p style={{
              fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.6,
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
                  <AlertTriangle size={12} color="#f59e0b" style={{ marginTop: '2px', flexShrink: 0 }} />
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
                  <CheckCircle2 size={12} color="#10b981" style={{ marginTop: '2px', flexShrink: 0 }} />
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
function LongitudinalPanel({ data }) {
  if (!data || !data.has_prior_history) {
    return (
      <div style={{
        display: 'flex', alignItems: 'center', gap: '10px',
        padding: '14px 18px', borderRadius: '10px',
        background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)',
        fontSize: '13px', color: 'var(--text-muted)'
      }}>
        <Info size={16} color="#10b981" />
        <span>{data?.message || 'No prior visits on record. This is your baseline visit.'}</span>
      </div>
    );
  }

  const statusColor =
    data.trajectory_status === 'ATTENTION_REQUIRED' ? '#ef4444' :
    data.trajectory_status === 'FAVORABLE_TRAJECTORY' ? '#10b981' : '#94a3b8';

  const StatusIcon =
    data.trajectory_status === 'ATTENTION_REQUIRED' ? AlertTriangle :
    data.trajectory_status === 'FAVORABLE_TRAJECTORY' ? TrendingDown : Activity;

  return (
    <div style={{
      borderRadius: '12px', overflow: 'hidden',
      border: `1px solid ${statusColor}30`,
      background: `${statusColor}08`
    }}>
      <div style={{
        display: 'flex', alignItems: 'center', gap: '10px',
        padding: '14px 18px',
        borderBottom: `1px solid ${statusColor}20`
      }}>
        <StatusIcon size={18} color={statusColor} />
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: '13px', fontWeight: 700, color: statusColor }}>
            {data.trajectory_status.replace(/_/g, ' ')}
          </div>
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '2px' }}>
            {data.days_since_prior} days since last visit • {data.total_visits_recorded} total visits recorded
          </div>
        </div>
      </div>

      {data.summary_advice && (
        <p style={{ padding: '12px 18px', fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.6, margin: 0 }}>
          {data.summary_advice}
        </p>
      )}

      {data.deltas && data.deltas.length > 0 && (
        <div style={{ padding: '0 18px 18px 18px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '4px' }}>
            VISIT-OVER-VISIT BIOMARKER CHANGES
          </div>
          {data.deltas.map((d, i) => <DeltaBadge key={i} delta={d} />)}
        </div>
      )}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────
// Main HealthHistory export
// ─────────────────────────────────────────────────────────────────────────────
export default function HealthHistory({ user, token }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchHistory = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/auth/history`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      setData(json);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);

  const checkups = data?.checkups || [];
  const longitudinal = data?.longitudinal || null;

  return (
    <div style={{ maxWidth: '780px', margin: '0 auto', padding: '28px 20px' }}>
      {/* Header */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        marginBottom: '24px', flexWrap: 'wrap', gap: '12px'
      }}>
        <div>
          <h2 style={{
            margin: 0, fontSize: '22px', fontWeight: 800,
            color: 'var(--text-primary)',
            display: 'flex', alignItems: 'center', gap: '10px'
          }}>
            <Calendar size={20} color="var(--accent-teal, #0e9f8e)" />
            Personal Health History
          </h2>
          <p style={{ margin: '4px 0 0', fontSize: '13px', color: 'var(--text-muted)' }}>
            Isolated timeline for {user?.name || user?.email} • {checkups.length} checkup{checkups.length !== 1 ? 's' : ''} recorded
          </p>
        </div>

        <button
          onClick={fetchHistory}
          disabled={loading}
          style={{
            display: 'flex', alignItems: 'center', gap: '7px',
            padding: '8px 16px', borderRadius: '8px',
            background: 'rgba(14,159,142,0.12)', border: '1px solid rgba(14,159,142,0.3)',
            color: 'var(--accent-teal, #0e9f8e)', fontWeight: 600, fontSize: '13px',
            cursor: loading ? 'not-allowed' : 'pointer', opacity: loading ? 0.6 : 1,
            transition: 'all 0.2s'
          }}
        >
          <RefreshCw size={14} style={{ animation: loading ? 'spin 1s linear infinite' : 'none' }} />
          {loading ? 'Loading…' : 'Refresh'}
        </button>
      </div>

      {/* Error */}
      {error && (
        <div style={{
          padding: '14px 18px', borderRadius: '10px', marginBottom: '20px',
          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.2)',
          fontSize: '13px', color: '#ef4444', display: 'flex', gap: '8px'
        }}>
          <AlertTriangle size={16} style={{ flexShrink: 0 }} />
          <span>Could not load history: {error}</span>
        </div>
      )}

      {/* Longitudinal trajectory panel */}
      {longitudinal && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 700, letterSpacing: '0.08em', marginBottom: '10px' }}>
            <BarChart3 size={12} style={{ marginRight: '6px', verticalAlign: 'middle' }} />
            LONGITUDINAL HEALTH TRAJECTORY
          </div>
          <LongitudinalPanel data={longitudinal} />
        </div>
      )}

      {/* Checkup list */}
      {checkups.length === 0 && !loading && !error ? (
        <div style={{
          textAlign: 'center', padding: '60px 20px',
          color: 'var(--text-muted)', fontSize: '14px'
        }}>
          <HeartPulse size={40} style={{ opacity: 0.25, marginBottom: '16px' }} />
          <p style={{ margin: 0 }}>No checkups recorded yet.</p>
          <p style={{ margin: '6px 0 0', fontSize: '12px', opacity: 0.7 }}>
            Run a clinical analysis and your results will be stored here for longitudinal tracking.
          </p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {checkups.map(c => <CheckupCard key={c.id} checkup={c} />)}
        </div>
      )}
    </div>
  );
}
