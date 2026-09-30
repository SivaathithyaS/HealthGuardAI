import React, { useState } from 'react';
import { 
  BarChart3, RefreshCw, CheckCircle2, AlertCircle, Shield, 
  Layers, Filter, Database, TrendingUp, Compass, Calendar, Award 
} from 'lucide-react';

export default function BenchmarkHubView({ evalResults, evalLoading, onRerunBenchmark }) {
  const [modalityFilter, setModalityFilter] = useState('ALL');
  const [statusFilter, setStatusFilter] = useState('ALL');

  if (!evalResults) {
    return (
      <div className="glass-card" style={{ textAlign: 'center', padding: '60px 20px' }}>
        <RefreshCw size={36} className="animate-spin" color="var(--accent-primary)" style={{ margin: '0 auto 16px' }} />
        <h3 style={{ fontFamily: 'var(--font-serif)', fontSize: '1.3rem', color: 'var(--text-title)' }}>
          Loading Live Clinical Validation Benchmark...
        </h3>
        <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', marginTop: '8px' }}>
          Computing live performance metrics across blinded validation cases.
        </p>
      </div>
    );
  }

  // Filter evaluated cases
  const filteredCases = (evalResults.evaluated_cases || []).filter(c => {
    if (modalityFilter !== 'ALL' && c.modality !== modalityFilter) return false;
    if (statusFilter === 'CORRECT' && !c.match_status.startsWith('CORRECT')) return false;
    if (statusFilter === 'ERROR' && c.match_status.startsWith('CORRECT')) return false;
    return true;
  });

  const cm = evalResults.confusion_matrix || { true_positive: 0, false_positive: 0, true_negative: 0, false_negative: 0 };
  const calib = evalResults.calibration_curve || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      
      {/* Top Banner Card */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <span style={{ fontSize: '0.74rem', background: 'var(--accent-forest-bg)', color: 'var(--accent-forest)', padding: '3px 10px', borderRadius: '999px', fontWeight: 800 }}>
                FLAGSHIP VALIDATION BENCHMARK
              </span>
              <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                N = {evalResults.total_cases} Blinded Test Cases
              </span>
            </div>
            <h2 style={{ fontSize: '1.45rem', fontWeight: 800, color: 'var(--text-title)', fontFamily: 'var(--font-serif)' }}>
              Live Multi-Modal Validation Benchmark Hub
            </h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-muted)', maxWidth: '780px', marginTop: '4px' }}>
              Rigorous empirical evaluation computed live across blinded clinical cases (disease-positive and hard negative controls) spanning Neurovascular CTA, Brain MRI, and Clinical Laboratory panels.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '8px' }}>
            <button 
              className="analyze-main-btn" 
              style={{ width: 'auto', padding: '12px 22px' }} 
              onClick={onRerunBenchmark} 
              disabled={evalLoading}
            >
              {evalLoading ? <RefreshCw className="animate-spin" size={16} /> : <BarChart3 size={16} />}
              <span>{evalLoading ? 'Running Benchmark Suite...' : 'Rerun Evaluation Suite'}</span>
            </button>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              Last evaluated: {evalResults.last_updated || 'Live Calculation'}
            </span>
          </div>
        </div>
      </div>

      {/* Primary Metrics Grid (7 Cards) */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '16px' }}>
        
        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-forest)' }}>
            {(evalResults.accuracy * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Overall Accuracy
          </div>
        </div>

        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-primary)' }}>
            {(evalResults.sensitivity_recall * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Sensitivity (Recall)
          </div>
        </div>

        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-forest)' }}>
            {(evalResults.specificity * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Specificity
          </div>
        </div>

        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-cyan)' }}>
            {(evalResults.precision * 100).toFixed(1)}%
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Precision (PPV)
          </div>
        </div>

        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-forest)' }}>
            {evalResults.macro_f1.toFixed(3)}
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Macro F1 Score
          </div>
        </div>

        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-amber)' }}>
            {evalResults.auroc.toFixed(3)}
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            AUROC Area
          </div>
        </div>

        <div className="glass-card" style={{ textAlign: 'center', padding: '18px 14px' }}>
          <div style={{ fontSize: '2.1rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-terracotta)' }}>
            {evalResults.brier_score.toFixed(4)}
          </div>
          <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
            Brier Calibration
          </div>
        </div>

      </div>

      {/* Row 2: 2x2 Confusion Matrix & Calibration Curve Chart */}
      <div className="two-col-grid">
        
        {/* 2x2 Confusion Matrix styled in green / warm cream theme */}
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title-group">
              <Layers size={18} color="var(--accent-primary)" />
              <div>
                <h3 className="card-title">2x2 Multi-Modal Confusion Matrix</h3>
                <p className="card-subtitle">Validated ground truth vs. autonomous pipeline prediction</p>
              </div>
            </div>
          </div>

          <div style={{ margin: '14px 0' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              
              {/* True Positive */}
              <div style={{ background: 'var(--accent-forest-bg)', border: '1px solid #b7dfca', borderRadius: 'var(--radius-md)', padding: '20px', textAlign: 'center' }}>
                <div style={{ fontSize: '2.4rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-forest)' }}>
                  {cm.true_positive}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-forest)', textTransform: 'uppercase' }}>
                  True Positive (TP)
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Disease correctly identified
                </div>
              </div>

              {/* False Positive */}
              <div style={{ background: cm.false_positive > 0 ? 'var(--accent-terracotta-bg)' : '#faf8f5', border: cm.false_positive > 0 ? '1px solid #fecdd3' : '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '20px', textAlign: 'center' }}>
                <div style={{ fontSize: '2.4rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: cm.false_positive > 0 ? 'var(--accent-terracotta)' : 'var(--text-muted)' }}>
                  {cm.false_positive}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: cm.false_positive > 0 ? 'var(--accent-terracotta)' : 'var(--text-muted)', textTransform: 'uppercase' }}>
                  False Positive (FP)
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Normal misclassified as disease
                </div>
              </div>

              {/* False Negative */}
              <div style={{ background: cm.false_negative > 0 ? 'var(--accent-terracotta-bg)' : '#faf8f5', border: cm.false_negative > 0 ? '1px solid #fecdd3' : '1px solid var(--border-subtle)', borderRadius: 'var(--radius-md)', padding: '20px', textAlign: 'center' }}>
                <div style={{ fontSize: '2.4rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: cm.false_negative > 0 ? 'var(--accent-terracotta)' : 'var(--text-muted)' }}>
                  {cm.false_negative}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: cm.false_negative > 0 ? 'var(--accent-terracotta)' : 'var(--text-muted)', textTransform: 'uppercase' }}>
                  False Negative (FN)
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Disease missed / under-called
                </div>
              </div>

              {/* True Negative */}
              <div style={{ background: 'var(--accent-forest-bg)', border: '1px solid #b7dfca', borderRadius: 'var(--radius-md)', padding: '20px', textAlign: 'center' }}>
                <div style={{ fontSize: '2.4rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--accent-forest)' }}>
                  {cm.true_negative}
                </div>
                <div style={{ fontSize: '0.78rem', fontWeight: 800, color: 'var(--accent-forest)', textTransform: 'uppercase' }}>
                  True Negative (TN)
                </div>
                <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                  Hard negative control confirmed
                </div>
              </div>

            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '14px', fontSize: '0.76rem', color: 'var(--text-muted)' }}>
              <span>Precision: <strong>{(evalResults.precision * 100).toFixed(1)}%</strong></span>
              <span>Recall: <strong>{(evalResults.sensitivity_recall * 100).toFixed(1)}%</strong></span>
              <span>Type I Error: <strong>{cm.false_positive}</strong></span>
              <span>Type II Error: <strong>{cm.false_negative}</strong></span>
            </div>
          </div>
        </div>

        {/* Empirical Calibration Curve Line Chart */}
        <div className="glass-card">
          <div className="card-header">
            <div className="card-title-group">
              <TrendingUp size={18} color="var(--accent-primary)" />
              <div>
                <h3 className="card-title">Empirical Calibration Curve</h3>
                <p className="card-subtitle">Predicted confidence vs. actual empirical disease outcome</p>
              </div>
            </div>
            <span style={{ fontSize: '0.72rem', background: 'var(--accent-forest-bg)', color: 'var(--accent-forest)', padding: '3px 8px', borderRadius: '4px', fontWeight: 700 }}>
              Brier: {evalResults.brier_score.toFixed(4)}
            </span>
          </div>

          <div className="calibration-chart-box">
            {/* SVG Line Chart */}
            <svg className="calib-svg" viewBox="0 0 380 220">
              {/* Grid Lines */}
              <line x1="50" y1="20" x2="350" y2="20" stroke="#e8e3d8" strokeDasharray="3 3" />
              <line x1="50" y1="65" x2="350" y2="65" stroke="#e8e3d8" strokeDasharray="3 3" />
              <line x1="50" y1="110" x2="350" y2="110" stroke="#e8e3d8" strokeDasharray="3 3" />
              <line x1="50" y1="155" x2="350" y2="155" stroke="#e8e3d8" strokeDasharray="3 3" />
              <line x1="50" y1="200" x2="350" y2="200" stroke="#141f1a" strokeWidth="1.5" />
              <line x1="50" y1="20" x2="50" y2="200" stroke="#141f1a" strokeWidth="1.5" />

              {/* Y Axis Labels */}
              <text x="42" y="24" textAnchor="end" fontSize="10" fill="#79867f" fontFamily="sans-serif">1.0</text>
              <text x="42" y="69" textAnchor="end" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.75</text>
              <text x="42" y="114" textAnchor="end" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.50</text>
              <text x="42" y="159" textAnchor="end" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.25</text>
              <text x="42" y="204" textAnchor="end" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.0</text>

              {/* X Axis Labels */}
              <text x="50" y="215" textAnchor="middle" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.0</text>
              <text x="125" y="215" textAnchor="middle" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.25</text>
              <text x="200" y="215" textAnchor="middle" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.50</text>
              <text x="275" y="215" textAnchor="middle" fontSize="10" fill="#79867f" fontFamily="sans-serif">0.75</text>
              <text x="350" y="215" textAnchor="middle" fontSize="10" fill="#79867f" fontFamily="sans-serif">1.0</text>

              {/* Ideal 45-degree Reference Line (Dashed) */}
              <line x1="50" y1="200" x2="350" y2="20" stroke="#79867f" strokeWidth="1.5" strokeDasharray="4 4" />

              {/* Empirical Model Calibration Points & Line */}
              {(() => {
                // Map bin centers to SVG coordinates
                // x: 50 + p * 300
                // y: 200 - frac * 180
                const points = calib.map(pt => ({
                  x: 50 + (pt.mean_predicted) * 300,
                  y: 200 - (pt.empirical_fraction) * 180,
                  pt
                }));

                const pathData = points.reduce((acc, curr, i) => `${acc} ${i === 0 ? 'M' : 'L'} ${curr.x} ${curr.y}`, '');

                return (
                  <g>
                    <path d={pathData} fill="none" stroke="var(--accent-forest)" strokeWidth="3" />
                    {points.map((p, i) => (
                      <g key={i}>
                        <circle cx={p.x} cy={p.y} r="5.5" fill="#ffffff" stroke="var(--accent-forest)" strokeWidth="2.5" />
                        <title>{`Bin: ${p.pt.bin_range}\nMean Pred: ${p.pt.mean_predicted}\nEmpirical: ${p.pt.empirical_fraction}\nSamples: ${p.pt.sample_count}`}</title>
                      </g>
                    ))}
                  </g>
                );
              })()}
            </svg>

            {/* Chart Legend */}
            <div style={{ display: 'flex', gap: '20px', alignItems: 'center', marginTop: '10px', fontSize: '0.74rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '16px', height: '2px', background: '#79867f', borderTop: '2px dashed #79867f' }}></span>
                <span style={{ color: 'var(--text-muted)' }}>Ideal Perfect Calibration (y = x)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                <span style={{ width: '16px', height: '3px', background: 'var(--accent-forest)' }}></span>
                <span style={{ color: 'var(--accent-forest)', fontWeight: 700 }}>HealthGuard Model Calibration</span>
              </div>
            </div>
          </div>
        </div>

      </div>

      {/* Row 3: Filterable Blinded Evaluated Cases Manifest */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '14px', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '1.15rem', fontWeight: 800, fontFamily: 'var(--font-serif)', color: 'var(--text-title)' }}>
              Evaluated Benchmark Cohort Manifest ({filteredCases.length} of {evalResults.total_cases} Cases)
            </h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Individual case provenance with modality, ground truth condition, prediction label, and match status.
            </p>
          </div>

          {/* Filter Pills */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 700 }}>Modality:</span>
            {['ALL', 'NEUROVASCULAR_CTA', 'BRAIN_MRI_REPORT', 'LAB_REPORT'].map(mod => (
              <button
                key={mod}
                className={`tab-button ${modalityFilter === mod ? 'active' : ''}`}
                style={{ padding: '5px 11px', fontSize: '0.72rem' }}
                onClick={() => setModalityFilter(mod)}
              >
                {mod === 'ALL' ? 'All' : mod.replace(/_/g, ' ')}
              </button>
            ))}

            <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)', fontWeight: 700, marginLeft: '8px' }}>Outcome:</span>
            {['ALL', 'CORRECT', 'ERROR'].map(st => (
              <button
                key={st}
                className={`tab-button ${statusFilter === st ? 'active' : ''}`}
                style={{ padding: '5px 11px', fontSize: '0.72rem' }}
                onClick={() => setStatusFilter(st)}
              >
                {st}
              </button>
            ))}
          </div>
        </div>

        <div className="params-table-container">
          <table className="eval-table">
            <thead>
              <tr>
                <th>Case ID</th>
                <th>Clinical Title</th>
                <th>Modality & Specialty</th>
                <th>Ground Truth Target</th>
                <th>Predicted Output</th>
                <th>Score</th>
                <th>Evaluation Status</th>
              </tr>
            </thead>
            <tbody>
              {filteredCases.map(c => (
                <tr key={c.case_id}>
                  <td><strong style={{ fontFamily: 'var(--font-mono)' }}>{c.case_id}</strong></td>
                  <td style={{ fontWeight: 600, color: 'var(--text-title)' }}>{c.title}</td>
                  <td>
                    <span style={{ fontSize: '0.72rem', background: 'var(--bg-subtle)', padding: '2px 8px', borderRadius: '4px', border: '1px solid var(--border-subtle)', fontFamily: 'var(--font-mono)' }}>
                      {c.modality}
                    </span>
                  </td>
                  <td style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{c.ground_truth}</td>
                  <td style={{ fontWeight: 600 }}>{c.predicted_label}</td>
                  <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 700 }}>{c.model_score}/100</td>
                  <td>
                    <span 
                      style={{ 
                        padding: '4px 9px', borderRadius: '999px', fontSize: '0.7rem', fontWeight: 800,
                        background: c.match_status.startsWith('CORRECT') ? 'var(--accent-forest-bg)' : 'var(--accent-terracotta-bg)',
                        color: c.match_status.startsWith('CORRECT') ? 'var(--accent-forest)' : 'var(--accent-terracotta)',
                        border: c.match_status.startsWith('CORRECT') ? '1px solid #86efac' : '1px solid #fda4af'
                      }}
                    >
                      {c.match_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  );
}
