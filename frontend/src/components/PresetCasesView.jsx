import React, { useState } from 'react';
import { 
  FileText, ArrowRight, Brain, HeartPulse, Droplet, 
  Stethoscope, ShieldAlert, CheckCircle2, ChevronDown, ChevronUp,
  Sparkles, User, Calendar, AlertTriangle
} from 'lucide-react';

export default function PresetCasesView({ samples = [], onSelectCase, onRunAnalysis }) {
  const [expandedTextId, setExpandedTextId] = useState(null);

  const getSpecialtyIcon = (specialty = '') => {
    const s = specialty.toLowerCase();
    if (s.includes('neuro') || s.includes('brain') || s.includes('stroke')) return Brain;
    if (s.includes('cardio') || s.includes('heart')) return HeartPulse;
    if (s.includes('hematology') || s.includes('blood') || s.includes('anemia')) return Droplet;
    if (s.includes('pulmonology') || s.includes('lung') || s.includes('thorax')) return Stethoscope;
    return FileText;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '22px' }}>
      {/* Intro Header */}
      <div className="glass-card" style={{ padding: '20px 24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h2 className="card-title" style={{ fontSize: '1.25rem', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileText size={20} color="var(--brand-accent)" />
              Pre-configured Clinical Case Library
            </h2>
            <p className="card-subtitle" style={{ fontSize: '0.82rem', marginTop: '4px' }}>
              Standardized multi-specialty clinical reports with verified diagnostic outcomes. Select any scenario to load its report and execute the 3-tier clinical hierarchy and prevention roadmap.
            </p>
          </div>
          <span style={{ fontSize: '0.78rem', background: 'var(--brand-accent-soft)', color: 'var(--brand-accent)', border: '1px solid var(--good-border)', padding: '4px 10px', borderRadius: '6px', fontWeight: 600 }}>
            {samples.length} Curated Cases
          </span>
        </div>
      </div>

      {/* Case Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(360px, 1fr))', gap: '16px' }}>
        {samples.map((sample) => {
          const IconComp = getSpecialtyIcon(sample.specialty);
          const isTextExpanded = expandedTextId === sample.id;

          return (
            <div 
              key={sample.id} 
              className="glass-card"
              style={{
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                padding: '20px 22px',
                borderRadius: 'var(--radius-lg)',
                border: '1px solid var(--border-default)',
                background: 'var(--bg-surface)'
              }}
            >
              <div>
                {/* Specialty Pill & ID */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    fontSize: '0.72rem',
                    fontWeight: 600,
                    textTransform: 'uppercase',
                    letterSpacing: '0.04em',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    background: 'var(--brand-accent-soft)',
                    color: 'var(--brand-accent)',
                    border: '1px solid var(--good-border)'
                  }}>
                    <IconComp size={12} />
                    {sample.specialty || 'General Medicine'}
                  </span>
                  <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                    {sample.id}
                  </span>
                </div>

                {/* Title */}
                <h3 style={{
                  fontFamily: 'var(--font-serif)',
                  fontSize: '1.08rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginBottom: '8px',
                  lineHeight: 1.35
                }}>
                  {sample.title.replace(/^[^\w\s]+/, '').trim()}
                </h3>

                {/* Clinical Description / Highlights */}
                <p style={{
                  fontSize: '0.8rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.5,
                  marginBottom: '14px'
                }}>
                  {sample.description || 'Verified multi-parameter diagnostic case report.'}
                </p>

                {/* Collapsible raw text view */}
                {isTextExpanded && (
                  <div style={{
                    marginTop: '10px',
                    marginBottom: '14px',
                    padding: '12px',
                    background: 'var(--bg-page)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: '6px',
                    maxHeight: '180px',
                    overflowY: 'auto',
                    fontSize: '0.74rem',
                    fontFamily: 'var(--font-mono)',
                    color: 'var(--text-secondary)',
                    whiteSpace: 'pre-wrap',
                    lineHeight: 1.45
                  }}>
                    {sample.text}
                  </div>
                )}
              </div>

              {/* Bottom Actions */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', paddingTop: '12px', borderTop: '1px solid var(--border-subtle)' }}>
                <button
                  type="button"
                  onClick={() => setExpandedTextId(isTextExpanded ? null : sample.id)}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    fontSize: '0.76rem',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px'
                  }}
                >
                  {isTextExpanded ? (
                    <>Hide report text <ChevronUp size={13} /></>
                  ) : (
                    <>Preview text <ChevronDown size={13} /></>
                  )}
                </button>

                <button
                  type="button"
                  className="analyze-main-btn"
                  style={{
                    padding: '8px 16px',
                    fontSize: '0.8rem',
                    gap: '6px'
                  }}
                  onClick={() => {
                    onSelectCase(sample);
                    if (onRunAnalysis) {
                      onRunAnalysis(sample.text);
                    }
                  }}
                >
                  <span>Load & Analyze</span>
                  <ArrowRight size={13} />
                </button>
              </div>

            </div>
          );
        })}
      </div>
    </div>
  );
}
