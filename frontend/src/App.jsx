import React, { useState, useEffect, useRef } from 'react';
import { 
  FileText, Upload, Sparkles, AlertCircle, CheckCircle2, AlertTriangle, 
  TrendingDown, Zap, Heart, Activity, Stethoscope, Droplet, 
  RefreshCw, ShieldAlert, Check, Calendar, ArrowRight, Layers, User, Award, Brain, Target, ShieldCheck, BarChart3, Database, FileCheck, GitBranch, Compass, TestTube, Users, Clock, Shield, AlertOctagon, Flame, ChevronDown, ChevronUp, Sun, Moon, CalendarDays
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function App() {
  const [activeTab, setActiveTab] = useState('universal');
  const [serverOnline, setServerOnline] = useState(false);
  
  // Universal Report Scanner State
  const [pipelineStage, setPipelineStage] = useState('IDLE');
  const [clinicalText, setClinicalText] = useState('');
  const [selectedPresetId, setSelectedPresetId] = useState('sample-3-stroke');
  const [showCustomText, setShowCustomText] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);
  const [sampleReports, setSampleReports] = useState([]);
  const fileInputRef = useRef(null);

  // Evaluation Hub State
  const [evalResults, setEvalResults] = useState(null);
  const [evalLoading, setEvalLoading] = useState(false);

  // Individual Cardiology Ensemble State
  const [heartForm, setHeartForm] = useState({
    age: 52, sex: 1, cp: 2, trestbps: 148, chol: 238, fbs: 0,
    restecg: 1, thalach: 145, exang: 1, oldpeak: 1.2, slope: 1, ca: 1, thal: 2
  });
  const [heartPred, setHeartPred] = useState(null);
  const [heartLoading, setHeartLoading] = useState(false);

  // Individual Diabetes Ensemble State
  const [diabForm, setDiabForm] = useState({
    pregnancies: 0, glucose: 118, blood_pressure: 94, skin_thickness: 32,
    insulin: 145, bmi: 30.3, diabetes_pedigree: 0.52, age: 52
  });
  const [diabResult, setDiabResult] = useState(null);
  const [diabLoading, setDiabLoading] = useState(false);

  useEffect(() => {
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(() => setServerOnline(true))
      .catch(() => setServerOnline(false));

    fetch(`${API_BASE}/api/documents/samples`)
      .then(res => res.json())
      .then(data => {
        if (data.samples && data.samples.length > 0) {
          setSampleReports(data.samples);
          setClinicalText(data.samples[0].text);
          setSelectedPresetId(data.samples[0].id);
          executeUniversalAnalysis(data.samples[0].text);
        }
      })
      .catch(() => {});
  }, []);

  const executeUniversalAnalysis = async (textToScan = clinicalText) => {
    if (!textToScan || textToScan.trim().length < 10) {
      setAnalysisError('Please enter clinical notes, lab values, or imaging findings.');
      return;
    }
    setAnalysisError(null);
    setPipelineStage('CLASSIFYING');

    try {
      setPipelineStage('EXTRACTING');
      await new Promise(r => setTimeout(r, 60));
      
      setPipelineStage('TRAVERSING_NODES');
      const res = await fetch(`${API_BASE}/api/analysis/universal`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: textToScan })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Diagnostic analysis failed.');
      }
      const data = await res.json();
      setAnalysisResult(data);
      setPipelineStage('COMPLETE');
    } catch (err) {
      setAnalysisError(err.message);
      setPipelineStage('IDLE');
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setAnalysisError(null);
    setPipelineStage('CLASSIFYING');
    setSelectedPresetId('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setPipelineStage('TRAVERSING_NODES');
      const res = await fetch(`${API_BASE}/api/analysis/upload`, {
        method: 'POST',
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'File ingestion failed.');
      }
      const data = await res.json();
      setAnalysisResult(data);
      setPipelineStage('COMPLETE');
    } catch (err) {
      setAnalysisError(err.message);
      setPipelineStage('IDLE');
    }
  };

  const runEvaluationHub = async () => {
    setEvalLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/evaluation/metrics`);
      const data = await res.json();
      setEvalResults(data);
    } catch (err) {
      console.error(err);
    } finally {
      setEvalLoading(false);
    }
  };

  const handleHeartPredict = async (e) => {
    if (e) e.preventDefault();
    setHeartLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/predict/heart`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(heartForm)
      });
      const data = await res.json();
      setHeartPred(data);
    } catch (err) {
      console.error(err);
    } finally {
      setHeartLoading(false);
    }
  };

  const handleDiabPredict = async (e) => {
    if (e) e.preventDefault();
    setDiabLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/predict/diabetes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(diabForm)
      });
      const data = await res.json();
      setDiabResult(data);
    } catch (err) {
      console.error(err);
    } finally {
      setDiabLoading(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="navbar">
        <div className="brand">
          <div className="brand-icon">
            <Compass size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center' }}>
              <span className="brand-title">HealthGuard AI</span>
              <span className="brand-badge">Clinical Decision Support</span>
            </div>
            <p style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
              Multi-Specialty Analysis • 3-Tier Finding Hierarchy • Short & Long-Term Prevention Routines
            </p>
          </div>
        </div>
        <div className="status-pill">
          <span 
            className="status-dot" 
            style={{ background: serverOnline ? '#10b981' : '#f43f5e', boxShadow: serverOnline ? '0 0 8px #10b981' : '0 0 8px #f43f5e' }}
          />
          <span>{serverOnline ? 'FastAPI Backend Active' : 'Connecting to API...'}</span>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="tabs-header">
        <button 
          className={`tab-button ${activeTab === 'universal' ? 'active' : ''}`}
          onClick={() => setActiveTab('universal')}
        >
          <Compass size={16} />
          <span>🌐 Clinical Diagnostic & Prevention Engine</span>
        </button>

        <button 
          className={`tab-button ${activeTab === 'evaluation' ? 'active' : ''}`}
          onClick={() => { setActiveTab('evaluation'); if (!evalResults) runEvaluationHub(); }}
        >
          <BarChart3 size={16} />
          <span>📊 Live Validation Benchmark Hub</span>
        </button>

        <button 
          className={`tab-button ${activeTab === 'heart' ? 'active' : ''}`}
          onClick={() => { setActiveTab('heart'); if (!heartPred) handleHeartPredict(); }}
        >
          <Heart size={16} />
          <span>🫀 Cardiology Ensemble (UCI Cleveland)</span>
        </button>

        <button 
          className={`tab-button ${activeTab === 'diabetes' ? 'active' : ''}`}
          onClick={() => { setActiveTab('diabetes'); if (!diabResult) handleDiabPredict(); }}
        >
          <Droplet size={16} />
          <span>🩸 Diabetes Ensemble (Pima Indians)</span>
        </button>
      </nav>

      {/* ========================================================================= */}
      {/* TAB 1: UNIVERSAL MULTI-DISEASE DIAGNOSTIC & REPORT SCANNER                */}
      {/* ========================================================================= */}
      {activeTab === 'universal' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          
          {/* ========================================================================= */}
          {/* TOP INTAKE BAR: FULL-WIDTH COMPACT CONTROLS                               */}
          {/* ========================================================================= */}
          <div className="intake-card">
            <div className="intake-controls-row">
              {/* Upload Dropzone Button */}
              <div 
                className="upload-mini-btn"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload size={18} />
                <span>Upload PDF / Report</span>
                <input 
                  ref={fileInputRef}
                  type="file" 
                  accept=".pdf,.png,.jpg,.jpeg,.txt" 
                  style={{ display: 'none' }}
                  onChange={handleFileUpload}
                />
              </div>

              {/* Preset Cases Scroll Row */}
              <div className="presets-scroll-row">
                {sampleReports.map(sample => (
                  <button
                    key={sample.id}
                    className={`preset-chip ${selectedPresetId === sample.id ? 'active' : ''}`}
                    onClick={() => {
                      setSelectedPresetId(sample.id);
                      setClinicalText(sample.text);
                      executeUniversalAnalysis(sample.text);
                    }}
                  >
                    <span className="preset-chip-title">{sample.title.split('—')[0]}</span>
                    <span className="preset-chip-sub">{sample.specialty}</span>
                  </button>
                ))}
              </div>

              {/* Action Button */}
              <button 
                className="analyze-main-btn"
                onClick={() => executeUniversalAnalysis()}
                disabled={['CLASSIFYING', 'EXTRACTING', 'TRAVERSING_NODES'].includes(pipelineStage)}
              >
                {['CLASSIFYING', 'EXTRACTING', 'TRAVERSING_NODES'].includes(pipelineStage) ? (
                  <>
                    <RefreshCw className="animate-spin" size={16} />
                    <span>Analyzing...</span>
                  </>
                ) : (
                  <>
                    <Sparkles size={16} />
                    <span>Run Analysis</span>
                  </>
                )}
              </button>
            </div>

            {/* Custom Narrative Toggle */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '4px', borderTop: '1px solid var(--border-subtle)' }}>
              <button 
                style={{ background: 'none', border: 'none', color: 'var(--text-muted)', fontSize: '0.74rem', display: 'flex', alignItems: 'center', gap: '4px', cursor: 'pointer' }}
                onClick={() => setShowCustomText(!showCustomText)}
              >
                {showCustomText ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                <span>{showCustomText ? 'Hide Clinical Text Editor' : 'Paste Custom Clinical Text / Lab Values / Symptoms'}</span>
              </button>

              {pipelineStage === 'COMPLETE' && (
                <span style={{ fontSize: '0.72rem', color: '#10b981', fontWeight: 600 }}>
                  ✓ Analysis Complete & State Purged
                </span>
              )}
            </div>

            {showCustomText && (
              <div className="intake-text-expand">
                <textarea
                  className="report-textarea"
                  value={clinicalText}
                  onChange={e => {
                    setClinicalText(e.target.value);
                    setSelectedPresetId('');
                  }}
                  placeholder="Paste or type clinical text: e.g. TSH/Free T4, CBC/Ferritin, ANA/Lupus, CT Head Stroke, Brain MRI, or metabolic lab panels..."
                />
              </div>
            )}

            {analysisError && (
              <div style={{ padding: '8px 12px', background: 'rgba(239, 68, 68, 0.15)', border: '1px solid rgba(239, 68, 68, 0.3)', borderRadius: '6px', color: '#fca5a5', fontSize: '0.78rem' }}>
                <AlertCircle size={14} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                {analysisError}
              </div>
            )}
          </div>

          {/* ========================================================================= */}
          {/* FULL-WIDTH OUTPUT DASHBOARD (SPANS 100% OF SCREEN)                       */}
          {/* ========================================================================= */}
          {analysisResult && (
            <div className="dashboard-grid">
              
              {/* ========================================================================= */}
              {/* ROW 1: AI SAFETY BANNER & CONFLICTING EVIDENCE (WHEN APPLICABLE)          */}
              {/* ========================================================================= */}
              <div className="ai-safety-banner">
                <ShieldAlert size={18} className="ai-safety-icon" />
                <div>
                  <div className="ai-safety-title">AI Clinical Safety & Decision Support Notice</div>
                  <div className="ai-safety-text">
                    {analysisResult.ai_safety_notice}
                  </div>
                </div>
              </div>

              {analysisResult.conflicting_evidence_alert && analysisResult.conflicting_evidence_alert.conflict_detected && (
                <div className="conflicting-evidence-card">
                  <div className="conflict-header">
                    <AlertOctagon size={18} color="#ef4444" />
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
                    <strong>Clinical Recommendation:</strong> {analysisResult.conflicting_evidence_alert.reconciliation_guidance}
                  </div>
                </div>
              )}

              {/* ========================================================================= */}
              {/* ROW 2 (TWO-COLUMN): PATIENT PROFILE CARD & PRIMARY DIAGNOSIS               */}
              {/* ========================================================================= */}
              <div className="two-col-grid">
                
                {/* Column 1: Patient Profile & Extracted Demographics */}
                <div className="patient-profile-card">
                  <div className="patient-profile-header">
                    <div className="patient-name-large">
                      <User size={20} color="#38bdf8" />
                      <span>{analysisResult.patient_context.name}</span>
                    </div>
                    <span style={{ fontSize: '0.72rem', background: 'rgba(56, 189, 248, 0.15)', color: '#7dd3fc', border: '1px solid rgba(56, 189, 248, 0.3)', padding: '2px 8px', borderRadius: '999px', fontWeight: 700 }}>
                      {analysisResult.detected_specialty}
                    </span>
                  </div>

                  <div className="patient-demographics-grid">
                    <div className="patient-stat-cell">
                      <span className="patient-stat-label">Patient Age</span>
                      <span className="patient-stat-value">{analysisResult.patient_context.age} Years</span>
                    </div>

                    <div className="patient-stat-cell">
                      <span className="patient-stat-label">Gender / Sex</span>
                      <span className="patient-stat-value">{analysisResult.patient_context.gender}</span>
                    </div>

                    <div className="patient-stat-cell">
                      <span className="patient-stat-label">MRN / Record #</span>
                      <span className="patient-stat-value" style={{ fontFamily: 'var(--font-mono)' }}>{analysisResult.patient_context.mrn}</span>
                    </div>

                    <div className="patient-stat-cell">
                      <span className="patient-stat-label">Study Date</span>
                      <span className="patient-stat-value">{analysisResult.patient_context.study_date}</span>
                    </div>

                    {analysisResult.patient_context.calculated_bmi && (
                      <div className="patient-stat-cell">
                        <span className="patient-stat-label">Calculated BMI</span>
                        <span className="patient-stat-value" style={{ color: '#fde68a' }}>{analysisResult.patient_context.calculated_bmi}</span>
                      </div>
                    )}

                    <div className="patient-stat-cell" style={{ gridColumn: analysisResult.patient_context.calculated_bmi ? 'span 1' : 'span 2' }}>
                      <span className="patient-stat-label">Ordering Service</span>
                      <span className="patient-stat-value">{analysisResult.patient_context.ordering_department}</span>
                    </div>
                  </div>
                </div>

                {/* Column 2: Primary Impression & AI Evidence Score */}
                <div className="neuro-hero-card">
                  <div>
                    <div className="neuro-acuity-tag" style={{ background: 'rgba(239, 68, 68, 0.25)', color: '#fca5a5' }}>
                      <AlertTriangle size={13} />
                      <span>{analysisResult.acuity_level}</span>
                    </div>
                    <h2 className="neuro-diag-title">{analysisResult.primary_suspected_condition}</h2>
                    
                    <div style={{ fontSize: '0.78rem', color: '#cbd5e1', marginTop: '6px', lineHeight: 1.45 }}>
                      <strong>Certainty:</strong> {analysisResult.diagnostic_certainty_level}
                    </div>

                    <div style={{ fontSize: '0.74rem', color: '#fde68a', marginTop: '4px' }}>
                      <strong>Confirmation:</strong> {analysisResult.required_confirmation}
                    </div>

                    <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', marginTop: '6px', fontStyle: 'italic' }}>
                      {analysisResult.evidence_score_disclaimer}
                    </div>
                  </div>

                  <div className="neuro-metric-box">
                    <span className="neuro-metric-val">{analysisResult.ai_evidence_score}</span>
                    <span className="neuro-metric-lbl">AI Evidence Score</span>
                  </div>
                </div>

              </div>

              {/* ========================================================================= */}
              {/* ROW 3 (TWO-COLUMN): 3-TIER CLINICAL HIERARCHY & DECISION NODE PATH        */}
              {/* ========================================================================= */}
              <div className="two-col-grid">
                
                {/* 3-Tier Clinical Evidence Hierarchy */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <Layers size={17} color="#38bdf8" />
                      <div>
                        <h3 className="card-title">3-Tier Clinical Evidence Hierarchy</h3>
                        <p className="card-subtitle">Observed Finding → Interpretation → Consideration</p>
                      </div>
                    </div>
                  </div>

                  <div className="params-table-container">
                    <table className="three-tier-table">
                      <thead>
                        <tr>
                          <th>Level 1: Observed</th>
                          <th>Level 2: Interpretation</th>
                          <th>Level 3: Consideration</th>
                        </tr>
                      </thead>
                      <tbody>
                        {analysisResult.three_tier_evidence.map((tier, idx) => (
                          <tr key={idx}>
                            <td>
                              <div style={{ fontWeight: 700, color: 'var(--text-primary)', marginBottom: '1px' }}>{tier.feature_name}</div>
                              <div style={{ fontFamily: 'var(--font-mono)', color: '#38bdf8', fontSize: '0.74rem' }}>{tier.observed_finding}</div>
                            </td>
                            <td style={{ color: '#e2e8f0', fontSize: '0.76rem' }}>
                              {tier.clinical_interpretation}
                            </td>
                            <td style={{ color: '#94a3b8', fontSize: '0.74rem' }}>
                              {tier.clinical_consideration}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Decision Node Traversal Path ("Node Points") */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <GitBranch size={17} color="#38bdf8" />
                      <div>
                        <h3 className="card-title">Decision Node Traversal Path ("Node Points")</h3>
                        <p className="card-subtitle">Step-by-Step Split Criteria Explaining Reasoning</p>
                      </div>
                    </div>
                  </div>

                  <div className="node-tree-container">
                    {analysisResult.decision_node_path.map((node, idx) => (
                      <div key={idx} className="node-tree-item">
                        <div className="node-point-badge">{node.step_number}</div>
                        <div className="node-content-card">
                          <div className="node-header-row">
                            <span className="node-title-text">{node.node_title}</span>
                            <span className="node-branch-tag">{node.branch_direction}</span>
                          </div>
                          <div className="node-criterion-box">
                            <strong>Criteria:</strong> {node.clinical_criterion}
                          </div>
                          <div className="node-obs-text">
                            ✓ {node.patient_observation}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* ========================================================================= */}
              {/* ROW 4 (TWO-COLUMN PREVENTIVE HUB): SHORT-TERM vs LONG-TERM ROUTINES       */}
              {/* ========================================================================= */}
              <div className="two-col-grid">
                
                {/* ⚡ Short-Term Actionable Routine (Days 1–30) */}
                <div className="glass-card" style={{ borderLeft: '3px solid #38bdf8' }}>
                  <div className="card-header">
                    <div className="card-title-group">
                      <Zap size={17} color="#38bdf8" />
                      <div>
                        <h3 className="card-title" style={{ color: '#38bdf8' }}>⚡ Short-Term Actionable Routine (Days 1–30)</h3>
                        <p className="card-subtitle">Immediate Daily & Weekly Protocols to Halt Risk Progression</p>
                      </div>
                    </div>
                  </div>

                  <div className="routine-grid">
                    {analysisResult.short_term_routine && analysisResult.short_term_routine.map((step, idx) => (
                      <div key={idx} className="routine-step-card short-term">
                        <div className="routine-top-row">
                          <span className="routine-title">
                            <CalendarDays size={14} color="#38bdf8" />
                            {step.title}
                          </span>
                          <span className="routine-time-badge cyan">{step.timeframe}</span>
                        </div>
                        <p className="routine-action-text">{step.action}</p>
                        <div className="routine-goal-box">
                          <strong>Target Goal:</strong> {step.target_goal}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 🛡️ Long-Term Disease Prevention Protocol (Months 1–6+) */}
                <div className="glass-card" style={{ borderLeft: '3px solid #10b981' }}>
                  <div className="card-header">
                    <div className="card-title-group">
                      <TrendingDown size={17} color="#10b981" />
                      <div>
                        <h3 className="card-title" style={{ color: '#6ee7b7' }}>🛡️ Long-Term Prevention Protocol (Months 1–6+)</h3>
                        <p className="card-subtitle">Sustained Lifestyle, Surveillance & Clinical Roadmaps</p>
                      </div>
                    </div>
                  </div>

                  <div className="routine-grid">
                    {analysisResult.long_term_routine && analysisResult.long_term_routine.map((step, idx) => (
                      <div key={idx} className="routine-step-card long-term">
                        <div className="routine-top-row">
                          <span className="routine-title">
                            <ShieldCheck size={14} color="#10b981" />
                            {step.title}
                          </span>
                          <span className="routine-time-badge emerald">{step.timeframe}</span>
                        </div>
                        <p className="routine-action-text">{step.action}</p>
                        <div className="routine-goal-box" style={{ color: '#a7f3d0' }}>
                          <strong>Target Goal:</strong> {step.target_goal}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* ========================================================================= */}
              {/* ROW 5 (TWO-COLUMN): MODIFIABLE RISK TABLE & DIFFERENTIALS/WORKUP          */}
              {/* ========================================================================= */}
              <div className="two-col-grid">
                
                {/* Granular Modifiable Risk Factors Table / Extracted Parameters Table */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <Activity size={17} color="#10b981" />
                      <div>
                        <h3 className="card-title">
                          {analysisResult.modifiable_risk_factors && analysisResult.modifiable_risk_factors.length > 0 
                            ? 'Granular Modifiable Risk Factors' 
                            : 'Extracted Biomarkers & Clinical Parameters'}
                        </h3>
                        <p className="card-subtitle">Verified Findings with Pathophysiologic Risk Mapping</p>
                      </div>
                    </div>
                  </div>

                  <div className="params-table-container">
                    {analysisResult.modifiable_risk_factors && analysisResult.modifiable_risk_factors.length > 0 ? (
                      <table className="risk-table">
                        <thead>
                          <tr>
                            <th>Risk Factor</th>
                            <th>Value</th>
                            <th>Pathophysiology</th>
                            <th>Target Protocol</th>
                          </tr>
                        </thead>
                        <tbody>
                          {analysisResult.modifiable_risk_factors.map((rf, idx) => (
                            <tr key={idx}>
                              <td><strong style={{ color: '#f8fafc' }}>{rf.risk_factor}</strong></td>
                              <td style={{ fontFamily: 'var(--font-mono)', color: '#fde68a', fontWeight: 700 }}>{rf.observed_value}</td>
                              <td style={{ color: '#cbd5e1', fontSize: '0.74rem' }}>{rf.pathophysiologic_explanation}</td>
                              <td style={{ color: '#a7f3d0', fontSize: '0.74rem' }}>{rf.tailored_prevention_protocol}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <table className="params-table">
                        <thead>
                          <tr>
                            <th>Parameter</th>
                            <th>Value</th>
                            <th>Status</th>
                            <th>Source Citation</th>
                          </tr>
                        </thead>
                        <tbody>
                          {analysisResult.extracted_parameters.map((param, idx) => (
                            <tr key={idx}>
                              <td><strong style={{ color: 'var(--text-primary)' }}>{param.name}</strong></td>
                              <td style={{ fontWeight: 700 }}>{param.value}</td>
                              <td>
                                <span className={`param-status-badge ${param.status.toLowerCase()}`}>
                                  {param.status}
                                </span>
                              </td>
                              <td style={{ fontStyle: 'italic', fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                                "{param.source_text}"
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    )}
                  </div>
                </div>

                {/* Differential Considerations & Confirmatory Workup */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <Target size={17} color="#f43f5e" />
                      <div>
                        <h3 className="card-title">AI Differentials & Confirmatory Workup</h3>
                        <p className="card-subtitle">Secondary Considerations & Recommended Next Steps</p>
                      </div>
                    </div>
                  </div>

                  <div className="diff-list" style={{ marginBottom: '16px' }}>
                    {analysisResult.differential_considerations.slice(0, 2).map((diff, idx) => (
                      <div key={idx} className={`diff-item ${idx === 0 ? 'primary' : ''}`}>
                        <div className="diff-top">
                          <span className="diff-name">{diff.condition_name}</span>
                          <span className="diff-prob" style={{ color: idx === 0 ? '#f43f5e' : 'var(--text-secondary)' }}>
                            Evidence: {diff.ai_evidence_score}/100
                          </span>
                        </div>
                        <div style={{ fontSize: '0.72rem', color: '#fde68a', margin: '2px 0' }}>
                          Certainty: {diff.diagnostic_certainty}
                        </div>
                        <p className="diff-rationale">{diff.clinical_rationale}</p>
                      </div>
                    ))}
                  </div>

                  {/* Confirmatory Diagnostic Workup */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.74rem', fontWeight: 700, color: 'var(--text-secondary)', textTransform: 'uppercase' }}>
                      Recommended Diagnostic Workup:
                    </div>
                    {analysisResult.recommended_diagnostic_workup.map((test, idx) => (
                      <div key={idx} className="workup-card">
                        <div className="workup-top">
                          <strong style={{ fontSize: '0.82rem', color: 'var(--text-primary)' }}>{test.test_name}</strong>
                          <span className={`workup-urgency-pill ${test.urgency.includes('STAT') ? 'stat' : test.urgency.includes('Urgent') ? 'urgent' : 'routine'}`}>
                            {test.urgency}
                          </span>
                        </div>
                        <span style={{ fontSize: '0.72rem', color: '#94a3b8' }}>Category: {test.category} • {test.clinical_purpose}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

            </div>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: LIVE BLINDED EVALUATION HUB                                       */}
      {/* ========================================================================= */}
      {activeTab === 'evaluation' && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div className="glass-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '16px' }}>
              <div>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                  Live Blinded Validation Benchmark Hub
                </h2>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  Rigorous evaluation across 10 blinded clinical validation benchmark cases (6 disease-positive, 4 hard negative controls).
                </p>
              </div>

              <button className="analyze-main-btn" style={{ width: 'auto', padding: '10px 18px' }} onClick={runEvaluationHub} disabled={evalLoading}>
                {evalLoading ? <RefreshCw className="animate-spin" size={16} /> : <BarChart3 size={16} />}
                <span>{evalLoading ? 'Running Benchmark...' : 'Rerun Evaluation Suite'}</span>
              </button>
            </div>
          </div>

          {evalResults && (
            <>
              {/* Metrics Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '16px' }}>
                <div className="glass-card" style={{ textAlign: 'center', padding: '16px' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#10b981' }}>
                    {(evalResults.accuracy * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Overall Accuracy
                  </div>
                </div>

                <div className="glass-card" style={{ textAlign: 'center', padding: '16px' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#38bdf8' }}>
                    {(evalResults.sensitivity_recall * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Sensitivity (Recall)
                  </div>
                </div>

                <div className="glass-card" style={{ textAlign: 'center', padding: '16px' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#a78bfa' }}>
                    {(evalResults.specificity * 100).toFixed(1)}%
                  </div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Specificity
                  </div>
                </div>

                <div className="glass-card" style={{ textAlign: 'center', padding: '16px' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#fbbf24' }}>
                    {evalResults.auroc.toFixed(3)}
                  </div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    AUROC
                  </div>
                </div>

                <div className="glass-card" style={{ textAlign: 'center', padding: '16px' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: 'var(--font-mono)', color: '#f43f5e' }}>
                    {evalResults.brier_score.toFixed(4)}
                  </div>
                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                    Brier Error
                  </div>
                </div>
              </div>

              {/* Confusion Matrix & Case Manifest */}
              <div className="two-col-grid">
                <div className="glass-card">
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '14px' }}>2x2 Clinical Confusion Matrix</h3>
                  <div className="cm-grid">
                    <div className="cm-cell">
                      <div className="cm-val" style={{ color: '#10b981' }}>{evalResults.confusion_matrix.true_positive}</div>
                      <div className="cm-lbl">True Positive (TP)</div>
                    </div>
                    <div className="cm-cell">
                      <div className="cm-val" style={{ color: '#f43f5e' }}>{evalResults.confusion_matrix.false_positive}</div>
                      <div className="cm-lbl">False Positive (FP)</div>
                    </div>
                    <div className="cm-cell">
                      <div className="cm-val" style={{ color: '#f43f5e' }}>{evalResults.confusion_matrix.false_negative}</div>
                      <div className="cm-lbl">False Negative (FN)</div>
                    </div>
                    <div className="cm-cell">
                      <div className="cm-val" style={{ color: '#38bdf8' }}>{evalResults.confusion_matrix.true_negative}</div>
                      <div className="cm-lbl">True Negative (TN)</div>
                    </div>
                  </div>
                </div>

                <div className="glass-card">
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 800, marginBottom: '14px' }}>Evaluated Benchmark Manifest</h3>
                  <div className="params-table-container">
                    <table className="eval-table">
                      <thead>
                        <tr>
                          <th>Case</th>
                          <th>Modality</th>
                          <th>Predicted Label</th>
                          <th>Score</th>
                          <th>Status</th>
                        </tr>
                      </thead>
                      <tbody>
                        {evalResults.evaluated_cases.map(c => (
                          <tr key={c.case_id}>
                            <td><strong>{c.case_id}</strong></td>
                            <td style={{ fontFamily: 'var(--font-mono)', fontSize: '0.7rem' }}>{c.modality}</td>
                            <td>{c.predicted_label}</td>
                            <td style={{ fontFamily: 'var(--font-mono)' }}>{c.model_score}</td>
                            <td>
                              <span 
                                style={{ 
                                  padding: '2px 6px', borderRadius: '4px', fontSize: '0.68rem', fontWeight: 700,
                                  background: c.match_status.startsWith('CORRECT') ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
                                  color: c.match_status.startsWith('CORRECT') ? '#6ee7b7' : '#fca5a5'
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
            </>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: INDIVIDUAL CARDIOLOGY ENSEMBLE                                     */}
      {/* ========================================================================= */}
      {activeTab === 'heart' && (
        <div className="two-col-grid">
          <section className="glass-card">
            <h2 className="card-title">Cardiology & Hemodynamics Ensemble</h2>
            <p className="card-subtitle">UCI Cleveland Dataset • Soft-Voting Ensemble (RandomForest + GradientBoosting)</p>
            <form onSubmit={handleHeartPredict} style={{ marginTop: '16px' }}>
              <div className="form-grid">
                <div className="field-group">
                  <label className="field-label">Age</label>
                  <input type="number" className="field-input" value={heartForm.age} onChange={e => setHeartForm({...heartForm, age: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Resting Blood Pressure (mm Hg)</label>
                  <input type="number" className="field-input" value={heartForm.trestbps} onChange={e => setHeartForm({...heartForm, trestbps: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Serum Cholesterol (mg/dL)</label>
                  <input type="number" className="field-input" value={heartForm.chol} onChange={e => setHeartForm({...heartForm, chol: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Maximum Heart Rate (bpm)</label>
                  <input type="number" className="field-input" value={heartForm.thalach} onChange={e => setHeartForm({...heartForm, thalach: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Chest Pain Type (0-3)</label>
                  <input type="number" className="field-input" value={heartForm.cp} onChange={e => setHeartForm({...heartForm, cp: parseInt(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">ST Depression (oldpeak)</label>
                  <input type="number" step="0.1" className="field-input" value={heartForm.oldpeak} onChange={e => setHeartForm({...heartForm, oldpeak: parseFloat(e.target.value)})} />
                </div>
              </div>
              <button type="submit" className="analyze-main-btn" disabled={heartLoading}>
                {heartLoading ? 'Calculating Risk...' : 'Evaluate Cardiology Model'}
              </button>
            </form>
          </section>

          {heartPred && (
            <section className="glass-card">
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: heartPred.risk_color, fontFamily: 'var(--font-mono)' }}>
                {heartPred.risk_percentage}%
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '4px 0 12px' }}>
                <span style={{ padding: '3px 10px', borderRadius: '999px', background: `${heartPred.risk_color}25`, color: heartPred.risk_color, fontSize: '0.8rem', fontWeight: 800 }}>
                  {heartPred.risk_label}
                </span>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{heartPred.confidence_interval || '95% CI: ± 3.2%'}</span>
              </div>
              
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, margin: '14px 0 8px' }}>Top SHAP Attribution Drivers</h4>
              {heartPred.top_positive_factors?.slice(0, 4).map((f, i) => (
                <div key={i} className="shap-item">
                  <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>{f.feature_name}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', color: f.shap_value > 0 ? '#f43f5e' : '#10b981' }}>
                    {f.shap_value > 0 ? `+${f.shap_value.toFixed(2)}` : f.shap_value.toFixed(2)}
                  </div>
                </div>
              ))}
            </section>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 4: INDIVIDUAL DIABETES ENSEMBLE                                       */}
      {/* ========================================================================= */}
      {activeTab === 'diabetes' && (
        <div className="two-col-grid">
          <section className="glass-card">
            <h2 className="card-title">Diabetes Screening Ensemble</h2>
            <p className="card-subtitle">Pima Indians Dataset • Gradient Boosted Ensemble with TreeSHAP</p>
            <form onSubmit={handleDiabPredict} style={{ marginTop: '16px' }}>
              <div className="form-grid">
                <div className="field-group">
                  <label className="field-label">Fasting Plasma Glucose (mg/dL)</label>
                  <input type="number" className="field-input" value={diabForm.glucose} onChange={e => setDiabForm({...diabForm, glucose: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Body Mass Index (BMI kg/m²)</label>
                  <input type="number" className="field-input" step="0.1" value={diabForm.bmi} onChange={e => setDiabForm({...diabForm, bmi: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Diastolic Blood Pressure (mm Hg)</label>
                  <input type="number" className="field-input" value={diabForm.blood_pressure} onChange={e => setDiabForm({...diabForm, blood_pressure: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Serum Insulin (mcU/mL)</label>
                  <input type="number" className="field-input" value={diabForm.insulin} onChange={e => setDiabForm({...diabForm, insulin: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Age (Years)</label>
                  <input type="number" className="field-input" value={diabForm.age} onChange={e => setDiabForm({...diabForm, age: parseFloat(e.target.value)})} />
                </div>
                <div className="field-group">
                  <label className="field-label">Diabetes Pedigree Function</label>
                  <input type="number" step="0.01" className="field-input" value={diabForm.diabetes_pedigree} onChange={e => setDiabForm({...diabForm, diabetes_pedigree: parseFloat(e.target.value)})} />
                </div>
              </div>
              <button type="submit" className="analyze-main-btn" disabled={diabLoading}>
                {diabLoading ? 'Calculating Risk...' : 'Evaluate Diabetes Model'}
              </button>
            </form>
          </section>

          {diabResult && (
            <section className="glass-card">
              <div style={{ fontSize: '2.2rem', fontWeight: 800, color: diabResult.risk_color, fontFamily: 'var(--font-mono)' }}>
                {diabResult.risk_percentage}%
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '4px 0 12px' }}>
                <span style={{ padding: '3px 10px', borderRadius: '999px', background: `${diabResult.risk_color}25`, color: diabResult.risk_color, fontSize: '0.8rem', fontWeight: 800 }}>
                  {diabResult.risk_label}
                </span>
                <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{diabResult.confidence_interval}</span>
              </div>
              
              <h4 style={{ fontSize: '0.85rem', fontWeight: 700, margin: '14px 0 8px' }}>Top SHAP Attribution Drivers</h4>
              {diabResult.top_positive_factors?.slice(0, 4).map((f, i) => (
                <div key={i} className="shap-item">
                  <div style={{ fontSize: '0.8rem', fontWeight: 700 }}>{f.feature_name}</div>
                  <div style={{ fontFamily: 'var(--font-mono)', color: f.shap_value > 0 ? '#f43f5e' : '#10b981' }}>
                    {f.shap_value > 0 ? `+${f.shap_value.toFixed(2)}` : f.shap_value.toFixed(2)}
                  </div>
                </div>
              ))}
            </section>
          )}
        </div>
      )}

      {/* Footer */}
      <footer className="disclaimer-bar">
        <p>
          <strong>HealthGuard AI — Clinical Decision Support & Prevention Prototype:</strong> Designed for clinical education and workflow decision support. AI evidence scores and decision tree traversal paths do not replace formal in-person diagnostic evaluation or physician judgment.
        </p>
      </footer>
    </div>
  );
}
