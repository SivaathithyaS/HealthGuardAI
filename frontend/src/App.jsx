import React, { useState, useEffect, useRef, useCallback } from 'react';
import { 
  FileText, Upload, Sparkles, AlertCircle, CheckCircle2, AlertTriangle, 
  TrendingDown, Zap, Heart, Activity, Stethoscope, Droplet, 
  RefreshCw, ShieldAlert, Check, Calendar, ArrowRight, Layers, User, Award, Brain, Target, ShieldCheck, BarChart3, Database, FileCheck, GitBranch, Compass, TestTube, Users, Clock, Shield, AlertOctagon, Flame, ChevronDown, ChevronUp, Sun, Moon, CalendarDays, Info, Edit3, Flag, BookOpen, Eye, HelpCircle, LogOut,
  PanelLeft, PanelLeftClose, PanelLeftOpen, ChevronLeft, X
} from 'lucide-react';

import RubricModal from './components/RubricModal';
import SummaryView from './components/SummaryView';
import ModelCardView from './components/ModelCardView';
import AuditLogModal from './components/AuditLogModal';
import OverrideModal from './components/OverrideModal';
import ImagingView from './components/ImagingView';
import HealthHistory from './components/HealthHistory';
import PresetCasesView from './components/PresetCasesView';

const API_BASE = 'http://localhost:8000';

export default function App({ user = null, token = null, onSignOut = null }) {
  const [activeTab, setActiveTab] = useState('universal');
  const [serverOnline, setServerOnline] = useState(false);
  
  // Dual View Mode State: 'clinician' (default full detail) or 'summary' (streamlined)
  const [viewMode, setViewMode] = useState(() => localStorage.getItem('healthguard_view_mode') || 'clinician');
  
  // Collapsible Sidebar Mode: 'expanded' (full 270px) | 'collapsed' (compact 72px icon rail) | 'hidden' (0px)
  const [sidebarMode, setSidebarMode] = useState(() => localStorage.getItem('healthguard_sidebar_mode') || 'expanded');

  const handleSetSidebarMode = (mode) => {
    setSidebarMode(mode);
    localStorage.setItem('healthguard_sidebar_mode', mode);
  };
  
  // Progressive Disclosure States
  const [showAllParams, setShowAllParams] = useState(false);
  const [showAllDiffs, setShowAllDiffs] = useState(false);

  // Modal Dialog States
  const [rubricModalData, setRubricModalData] = useState(null);
  const [auditLogModalOpen, setAuditLogModalOpen] = useState(false);
  const [overrideModalData, setOverrideModalData] = useState(null);

  // Account Menu State
  const [accountMenuOpen, setAccountMenuOpen] = useState(false);
  const accountMenuRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (accountMenuRef.current && !accountMenuRef.current.contains(e.target)) {
        setAccountMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // ── Per-user storage key helpers ──────────────────────────────────────────
  const userKey = (key) => `healthguard_${user?.email || 'guest'}_${key}`;

  // Human-in-the-Loop Feedback Log — scoped per user
  const [feedbackLog, setFeedbackLog] = useState(() => {
    try {
      const stored = localStorage.getItem(userKey('feedback_log'));
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  });

  // Universal Report Scanner State
  const [pipelineStage, setPipelineStage] = useState('IDLE');
  const [clinicalText, setClinicalText] = useState('');
  const [selectedPresetId, setSelectedPresetId] = useState('');
  // Restore last scan result for returning users; new users start blank
  const [analysisResult, setAnalysisResult] = useState(() => {
    try {
      const stored = localStorage.getItem(userKey('last_result'));
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  });
  const [analysisError, setAnalysisError] = useState(null);
  const [sampleReports, setSampleReports] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const fileInputRef = useRef(null);

  // Individual Cardiology Ensemble State
  const [heartForm, setHeartForm] = useState({
    age: 50, sex: 1, cp: 0, trestbps: 120, chol: 200, fbs: 0,
    restecg: 0, thalach: 150, exang: 0, oldpeak: 1.0, slope: 1, ca: 0, thal: 2
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

  const fetchFeedbackHistory = useCallback(() => {
    fetch(`${API_BASE}/api/feedback/history`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {}
    })
      .then(res => res.json())
      .then(data => {
        if (data && Array.isArray(data.history)) {
          setFeedbackLog(data.history);
          localStorage.setItem(userKey('feedback_log'), JSON.stringify(data.history));
        }
      })
      .catch(() => {});
  }, [token, user?.email]);

  useEffect(() => {
    // Server health check only — no auto-sample fetch or auto-analysis
    fetch(`${API_BASE}/health`)
      .then(res => res.json())
      .then(() => setServerOnline(true))
      .catch(() => setServerOnline(false));

    // Load sample list for the Presets tab (but do NOT auto-run anything)
    fetch(`${API_BASE}/api/documents/samples`)
      .then(res => res.json())
      .then(data => { if (data.samples) setSampleReports(data.samples); })
      .catch(() => {});

    // Sync feedback history from backend for authenticated user
    fetchFeedbackHistory();
  }, [fetchFeedbackHistory]);

  const handleViewModeChange = (mode) => {
    setViewMode(mode);
    localStorage.setItem('healthguard_view_mode', mode);
  };

  const handleConfirmFeedback = async (diffItem) => {
    const entry = {
      id: `fb-${Date.now()}`,
      case_id: analysisResult?.patient_context?.mrn || 'CASE-EXTRACTED',
      patient_name: analysisResult?.patient_context?.name || 'Patient',
      condition_name: diffItem.condition_name,
      original_score: diffItem.ai_evidence_score,
      action: 'CONFIRMED',
      override_text: null,
      override_reason: 'Clinician confirmed and accepted AI diagnostic finding.',
      clinician_id: 'Dr. M. Chen, MD (Attending)',
      timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
    };

    const updated = [entry, ...feedbackLog];
    setFeedbackLog(updated);
    localStorage.setItem(userKey('feedback_log'), JSON.stringify(updated));

    try {
      await fetch(`${API_BASE}/api/feedback/log`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(entry)
      });
    } catch (err) {
      console.warn("Feedback sync failed (saved locally):", err);
    }
  };

  const handleOpenOverride = (diffItem) => {
    setOverrideModalData({
      action: 'OVERRIDDEN',
      diffItem,
      patientName: analysisResult?.patient_context?.name,
      caseId: analysisResult?.patient_context?.mrn
    });
  };

  const handleOpenFlag = (diffItem) => {
    setOverrideModalData({
      action: 'FLAGGED',
      diffItem,
      patientName: analysisResult?.patient_context?.name,
      caseId: analysisResult?.patient_context?.mrn
    });
  };

  const handleCommitFeedback = async ({ action, diffItem, correctedCondition, rationale, clinicianId }) => {
    const entry = {
      id: `fb-${Date.now()}`,
      case_id: analysisResult?.patient_context?.mrn || 'CASE-EXTRACTED',
      patient_name: analysisResult?.patient_context?.name || 'Patient',
      condition_name: diffItem.condition_name,
      original_score: diffItem.ai_evidence_score,
      action: action,
      override_text: correctedCondition,
      override_reason: rationale,
      clinician_id: clinicianId,
      timestamp: new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC'
    };

    const updated = [entry, ...feedbackLog];
    setFeedbackLog(updated);
    localStorage.setItem(userKey('feedback_log'), JSON.stringify(updated));

    try {
      await fetch(`${API_BASE}/api/feedback/log`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {})
        },
        body: JSON.stringify(entry)
      });
    } catch (err) {
      console.warn("Feedback sync failed (saved locally):", err);
    }
  };

  const handleClearAuditLog = async () => {
    setFeedbackLog([]);
    localStorage.removeItem(userKey('feedback_log'));
    try {
      await fetch(`${API_BASE}/api/feedback/clear`, { 
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {}
      });
    } catch {}
  };

  // Persist result per-user whenever it changes
  useEffect(() => {
    if (analysisResult) {
      localStorage.setItem(userKey('last_result'), JSON.stringify(analysisResult));
    }
  }, [analysisResult]);

  // Clear current session's scan result (not stored history)
  const handleClearScanResult = () => {
    setAnalysisResult(null);
    setClinicalText('');
    setSelectedFile(null);
    setPipelineStage('IDLE');
    setAnalysisError(null);
    localStorage.removeItem(userKey('last_result'));
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const executeUniversalAnalysis = async (textToScan = clinicalText, saveToHistory = false) => {
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
      const effectiveToken = token || sessionStorage.getItem('healthguard_access_token');
      const headers = { 'Content-Type': 'application/json' };
      if (effectiveToken) {
        headers['Authorization'] = `Bearer ${effectiveToken}`;
      }

      const queryParam = saveToHistory ? '?save_to_history=true' : '?save_to_history=false';
      const res = await fetch(`${API_BASE}/api/analysis/universal${queryParam}`, {
        method: 'POST',
        headers,
        body: JSON.stringify({ text: textToScan })
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'Diagnostic analysis failed.');
      }
      const data = await res.json();
      setAnalysisResult(data);
      localStorage.setItem(userKey('last_result'), JSON.stringify(data));
      setPipelineStage('COMPLETE');
      // Refresh audit log so scanned document shows immediately in the audit trail
      fetchFeedbackHistory();
    } catch (err) {
      setAnalysisError(err.message);
      setPipelineStage('IDLE');
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setSelectedFile(file);
    setAnalysisError(null);
    setSelectedPresetId('');

    // If text file, preview into clinical text
    if (file.type.includes('text') || file.name.endsWith('.txt')) {
      const reader = new FileReader();
      reader.onload = (evt) => {
        setClinicalText(evt.target.result || '');
      };
      reader.readAsText(file);
    }
  };

  const executeFileUploadAnalysis = async (fileToUpload) => {
    const file = fileToUpload || selectedFile;
    if (!file) return;

    setAnalysisError(null);
    setPipelineStage('CLASSIFYING');
    setSelectedPresetId('');

    const formData = new FormData();
    formData.append('file', file);

    try {
      setPipelineStage('TRAVERSING_NODES');
      const effectiveToken = token || sessionStorage.getItem('healthguard_access_token');
      const headers = {};
      if (effectiveToken) {
        headers['Authorization'] = `Bearer ${effectiveToken}`;
      }

      const res = await fetch(`${API_BASE}/api/analysis/upload?save_to_history=true`, {
        method: 'POST',
        headers,
        body: formData
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || 'File ingestion failed.');
      }
      const data = await res.json();
      setAnalysisResult(data);
      localStorage.setItem(userKey('last_result'), JSON.stringify(data));
      setPipelineStage('COMPLETE');

      // Refresh feedback history immediately to increment audit log
      fetchFeedbackHistory();
    } catch (err) {
      setAnalysisError(err.message);
      setPipelineStage('IDLE');
    }
  };

  const handleRunAnalysis = async () => {
    if (selectedFile) {
      await executeFileUploadAnalysis(selectedFile);
    } else if (clinicalText && clinicalText.trim().length >= 10) {
      await executeUniversalAnalysis(clinicalText, true);
    } else {
      setAnalysisError('Please select a report file to upload or enter clinical notes/findings.');
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
    <div className="dashboard-layout">
      {/* Sidebar Navigation */}
      <aside className={`dashboard-sidebar mode-${sidebarMode}`}>
        <div className="sidebar-brand">
          {sidebarMode !== 'collapsed' ? (
            <>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flex: 1, minWidth: 0 }}>
                <div className="sidebar-brand-icon">
                  <Shield size={20} strokeWidth={1.5} />
                </div>
                <div className="sidebar-brand-text">
                  <span className="sidebar-brand-title">HealthGuard AI</span>
                  <span className="sidebar-brand-badge">Clinical Decision Support</span>
                </div>
              </div>
              <div className="sidebar-header-actions">
                <button 
                  type="button" 
                  className="sidebar-action-btn"
                  onClick={() => handleSetSidebarMode('collapsed')}
                  title="Retract to compact icon rail"
                  aria-label="Collapse sidebar"
                >
                  <PanelLeftClose size={15} />
                </button>
                <button 
                  type="button" 
                  className="sidebar-action-btn"
                  onClick={() => handleSetSidebarMode('hidden')}
                  title="Hide sidebar completely"
                  aria-label="Hide sidebar"
                >
                  <ChevronLeft size={15} />
                </button>
              </div>
            </>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
              <div className="sidebar-brand-icon" title="HealthGuard AI">
                <Shield size={20} strokeWidth={1.5} />
              </div>
              <button 
                type="button" 
                className="sidebar-action-btn"
                onClick={() => handleSetSidebarMode('expanded')}
                title="Expand sidebar navigation"
                aria-label="Expand sidebar"
              >
                <PanelLeftOpen size={16} />
              </button>
            </div>
          )}
        </div>

        <nav className="sidebar-nav">
          <div className="sidebar-nav-section-title">Diagnostic Screening</div>
          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'universal' ? 'active' : ''}`}
            onClick={() => setActiveTab('universal')}
            title="Universal Scanner"
          >
            <FileText size={16} strokeWidth={1.5} />
            <span>Universal Scanner</span>
          </button>

          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'imaging' ? 'active' : ''}`}
            onClick={() => setActiveTab('imaging')}
            title="Imaging & Waveforms"
          >
            <Activity size={16} strokeWidth={1.5} />
            <span>Imaging & Waveforms</span>
          </button>

          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'presets' ? 'active' : ''}`}
            onClick={() => setActiveTab('presets')}
            title="Pre-configured Reports"
          >
            <BookOpen size={16} strokeWidth={1.5} />
            <span>Pre-configured Reports</span>
          </button>

          <div className="sidebar-nav-section-title">Specialty Ensembles</div>
          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'heart' ? 'active' : ''}`}
            onClick={() => { setActiveTab('heart'); if (!heartPred) handleHeartPredict(); }}
            title="Cardiology Risk"
          >
            <Heart size={16} strokeWidth={1.5} />
            <span>Cardiology Risk</span>
          </button>

          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'diabetes' ? 'active' : ''}`}
            onClick={() => { setActiveTab('diabetes'); if (!diabResult) handleDiabPredict(); }}
            title="Diabetes Risk"
          >
            <Droplet size={16} strokeWidth={1.5} />
            <span>Diabetes Risk</span>
          </button>

          <div className="sidebar-nav-section-title">Clinical Records & Governance</div>
          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
            title="Patient Health History"
          >
            <CalendarDays size={16} strokeWidth={1.5} />
            <span>Patient Health History</span>
          </button>

          <button 
            type="button"
            className={`sidebar-nav-item ${activeTab === 'model-card' ? 'active' : ''}`}
            onClick={() => setActiveTab('model-card')}
            title="Clinical Model Card"
          >
            <FileCheck size={16} strokeWidth={1.5} />
            <span>Clinical Model Card</span>
          </button>
        </nav>


      </aside>

      {/* Main Content Area */}
      <div className="dashboard-main">
        {/* Top Header Bar */}
        <header className="navbar">
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', minWidth: 0 }}>
            <button
              type="button"
              className={`navbar-sidebar-toggle-btn ${sidebarMode === 'hidden' ? 'pulse-attention' : ''}`}
              onClick={() => {
                if (sidebarMode === 'hidden') handleSetSidebarMode('expanded');
                else if (sidebarMode === 'expanded') handleSetSidebarMode('collapsed');
                else handleSetSidebarMode('expanded');
              }}
              title={sidebarMode === 'hidden' ? "Show sidebar navigation" : (sidebarMode === 'collapsed' ? "Expand sidebar tabs" : "Retract sidebar tabs")}
              aria-label="Toggle sidebar navigation"
            >
              {sidebarMode === 'hidden' ? <PanelLeft size={18} /> : (sidebarMode === 'collapsed' ? <PanelLeftOpen size={18} /> : <PanelLeftClose size={18} />)}
            </button>

            <div>
              <h1 className="navbar-page-title">
                {activeTab === 'universal' && 'Universal Report Scanner & Prevention'}
                {activeTab === 'imaging' && 'Clinical Imaging & Waveforms'}
                {activeTab === 'presets' && 'Pre-configured Clinical Cases'}
                {activeTab === 'heart' && 'Cardiology Risk Assessment'}
                {activeTab === 'diabetes' && 'Diabetes Metabolic Risk Assessment'}
                {activeTab === 'model-card' && 'Clinical Model Card Specification'}
                {activeTab === 'history' && 'Personal Health History'}
              </h1>
              <p className="navbar-page-subtitle">
                {activeTab === 'universal' && 'Multi-line entity extraction, 3-tier clinical hierarchy, and evidence-based prevention roadmaps.'}
                {activeTab === 'imaging' && '1D-CNN ECG waveform analysis and DenseNet-121 Brain MRI GradCAM inference.'}
                {activeTab === 'presets' && 'Standardized multi-specialty clinical benchmark scenarios with verified findings.'}
                {activeTab === 'heart' && 'Cleveland Clinic 13-feature ensemble with TreeSHAP risk factor attribution.'}
                {activeTab === 'diabetes' && 'Pima Indians metabolic biomarker ensemble with empirical confidence intervals.'}
                {activeTab === 'model-card' && 'Specification of model architectures, training datasets, intended use, and limitations.'}
                {activeTab === 'history' && 'Per-user isolated timeline with visit-over-visit biomarker trajectory tracking.'}
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
            {/* Dual View Mode Toggle */}
            <div className="view-mode-toggle">
              <button 
                type="button"
                className={`view-mode-btn ${viewMode === 'clinician' ? 'active' : ''}`}
                onClick={() => handleViewModeChange('clinician')}
                title="Clinician View: Full multi-tier clinical evidence, decision trees, and parameters"
              >
                <Activity size={13} strokeWidth={1.5} />
                <span>Clinician View</span>
              </button>
              <button 
                type="button"
                className={`view-mode-btn ${viewMode === 'summary' ? 'active' : ''}`}
                onClick={() => handleViewModeChange('summary')}
                title="Summary View: Streamlined executive plain-language view without jargon"
              >
                <Eye size={13} strokeWidth={1.5} />
                <span>Summary View</span>
              </button>
            </div>

            {/* Clinician Review & Audit Trail Pill */}
            <button 
              type="button"
              className="status-pill"
              style={{ cursor: 'pointer' }}
              onClick={() => setAuditLogModalOpen(true)}
              title="Open Clinician Feedback & Audit Trail"
            >
              <ShieldCheck size={14} strokeWidth={1.5} />
              <span>Audit Log ({feedbackLog.length})</span>
            </button>

            {/* User Account Menu with Click-to-Open Signout Dropdown */}
            <div className="account-dropdown-wrap" ref={accountMenuRef}>
              <button
                type="button"
                className="account-trigger-btn"
                onClick={() => setAccountMenuOpen(!accountMenuOpen)}
                title="Account menu"
              >
                <div className="account-avatar">
                  {(user?.name ? user.name[0] : (user?.email ? user.email[0] : 'U')).toUpperCase()}
                </div>
                <span className="account-label">
                  {user?.name || user?.email || 'Dr. Sarah Lin'}
                </span>
                <ChevronDown size={13} className={`account-caret ${accountMenuOpen ? 'open' : ''}`} />
              </button>

              {accountMenuOpen && (
                <div className="account-menu-popover">
                  <div className="account-popover-info">
                    <div className="account-popover-name">{user?.name || 'Dr. Sarah Lin, MD'}</div>
                    <div className="account-popover-email">{user?.email || 'clinician@healthguard.ai'}</div>
                    <span className="account-popover-role">{user?.role || 'Clinician'}</span>
                  </div>
                  <div className="account-popover-divider" />
                  <button 
                    type="button" 
                    className="account-popover-item"
                    onClick={() => { setActiveTab('history'); setAccountMenuOpen(false); }}
                  >
                    <CalendarDays size={14} />
                    <span>My Health History</span>
                  </button>
                  <button 
                    type="button" 
                    className="account-popover-item"
                    onClick={() => { setAuditLogModalOpen(true); setAccountMenuOpen(false); }}
                  >
                    <ShieldCheck size={14} />
                    <span>Audit Trail Log</span>
                  </button>
                  <div className="account-popover-divider" />
                  {onSignOut && (
                    <button 
                      type="button" 
                      className="account-popover-item signout"
                      onClick={() => { setAccountMenuOpen(false); onSignOut(); }}
                    >
                      <LogOut size={14} />
                      <span>Sign out</span>
                    </button>
                  )}
                </div>
              )}
            </div>

          </div>
        </header>

        {/* ========================================================================= */}
        {/* TAB 1: UNIVERSAL MULTI-DISEASE DIAGNOSTIC & REPORT SCANNER                */}
        {/* ========================================================================= */}
        {activeTab === 'universal' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            
            {/* INTAKE CARD: CLEAN WORKSPACE WITHOUT OVERCROWDED PRESET CHIPS */}
            <div className="intake-card">
              <div className="intake-controls-row">
                {/* Upload Drop Zone */}
                <div 
                  className="upload-mini-btn"
                  onClick={() => fileInputRef.current?.click()}
                  title="Upload PDF, Image (PNG/JPG), or Text Report"
                >
                  <Upload size={18} />
                  <div style={{ textAlign: 'left' }}>
                    <div style={{ fontWeight: 600, fontSize: '0.85rem' }}>Upload PDF / Report</div>
                    <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>PDF, JPG, PNG, TXT</div>
                  </div>
                  <input 
                    ref={fileInputRef}
                    type="file" 
                    accept=".pdf,.png,.jpg,.jpeg,.txt" 
                    style={{ display: 'none' }}
                    onChange={handleFileSelect}
                  />
                </div>

                {/* Action Button */}
                <button 
                  type="button"
                  className="analyze-main-btn"
                  onClick={handleRunAnalysis}
                  disabled={['CLASSIFYING', 'EXTRACTING', 'TRAVERSING_NODES'].includes(pipelineStage)}
                >
                  {['CLASSIFYING', 'EXTRACTING', 'TRAVERSING_NODES'].includes(pipelineStage) ? (
                    <>
                      <RefreshCw className="animate-spin" size={15} strokeWidth={1.5} />
                      <span>Analyzing...</span>
                    </>
                  ) : (
                    <>
                      <FileText size={15} strokeWidth={1.5} />
                      <span>Run Analysis</span>
                    </>
                  )}
                </button>
              </div>

              {/* Uploaded File Preview Below Upload Section */}
              {selectedFile && (
                <div style={{
                  marginTop: '12px',
                  padding: '10px 14px',
                  borderRadius: 'var(--radius-sm, 8px)',
                  background: 'var(--bg-surface, #15221e)',
                  border: '1px solid var(--border-default, #2a3832)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '12px'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', minWidth: 0 }}>
                    <FileText size={18} color="var(--brand-accent, #3b82f6)" style={{ flexShrink: 0 }} />
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.84rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                        {selectedFile.name}
                      </div>
                      <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
                        {(selectedFile.size / 1024).toFixed(1)} KB • Staged for scanning. Click "Run Analysis" to proceed.
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={() => {
                      setSelectedFile(null);
                      if (fileInputRef.current) fileInputRef.current.value = '';
                    }}
                    title="Remove file"
                    style={{
                      background: 'transparent',
                      border: 'none',
                      color: 'var(--text-muted)',
                      cursor: 'pointer',
                      padding: '4px',
                      display: 'flex',
                      alignItems: 'center'
                    }}
                  >
                    <X size={16} />
                  </button>
                </div>
              )}

              {analysisError && (
                <div style={{ marginTop: '10px', padding: '10px 14px', background: 'var(--critical-bg)', border: '1px solid var(--critical-border)', borderRadius: '8px', color: 'var(--critical-text)', fontSize: '0.82rem' }}>
                  <AlertCircle size={15} style={{ display: 'inline', marginRight: '6px', verticalAlign: 'middle' }} />
                  {analysisError}
                </div>
              )}
            </div>

          {/* ========================================================================= */}
          {/* EMPTY STATE — shown when no scan has been run yet                         */}
          {/* ========================================================================= */}
          {!analysisResult && pipelineStage === 'IDLE' && (
            <div style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '64px 24px',
              gap: '16px',
              opacity: 0.45,
              userSelect: 'none',
              pointerEvents: 'none',
            }}>
              <FileText size={48} strokeWidth={1} style={{ color: 'var(--text-muted)' }} />
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
                  No report scanned yet
                </div>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', maxWidth: '320px', lineHeight: 1.6 }}>
                  Upload a PDF, image, or text report above to run the clinical analysis pipeline. Your results will appear here.
                </div>
              </div>
            </div>
          )}

          {/* ========================================================================= */}
          {/* FULL-WIDTH OUTPUT DASHBOARD (SPANS 100% OF SCREEN)                       */}
          {/* ========================================================================= */}
          {analysisResult && (
            <>
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '4px' }}>
                <button
                  type="button"
                  onClick={handleClearScanResult}
                  style={{
                    display: 'inline-flex', alignItems: 'center', gap: '6px',
                    background: 'transparent', border: '1px solid var(--border-default)',
                    borderRadius: 'var(--radius-md)', padding: '5px 12px',
                    fontSize: '0.75rem', color: 'var(--text-muted)', cursor: 'pointer',
                    transition: 'all 0.15s ease',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.borderColor = 'var(--critical-accent)'; e.currentTarget.style.color = 'var(--critical-accent)'; }}
                  onMouseLeave={e => { e.currentTarget.style.borderColor = 'var(--border-default)'; e.currentTarget.style.color = 'var(--text-muted)'; }}
                  title="Clear current scan and start fresh"
                >
                  <RefreshCw size={12} />
                  New Scan
                </button>
              </div>
            {viewMode === 'summary' ? (
              <SummaryView 
                analysisResult={analysisResult}
                onSwitchToClinicianView={() => handleViewModeChange('clinician')}
              />
            ) : (
            <div className="dashboard-grid" id="clinical-full-report">
              

              {analysisResult.conflicting_evidence_alert && analysisResult.conflicting_evidence_alert.conflict_detected && (
                <div className="conflicting-evidence-card">
                  <div className="conflict-header">
                    <AlertTriangle size={17} strokeWidth={1.5} color="var(--critical-accent)" />
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
                      <User size={18} strokeWidth={1.5} color="var(--brand-accent)" />
                      <span>{analysisResult.patient_context.name}</span>
                    </div>
                    <span style={{ fontSize: '0.72rem', background: 'var(--brand-accent-soft)', color: 'var(--brand-accent)', border: '1px solid var(--good-border)', padding: '2px 8px', borderRadius: '4px', fontWeight: 600 }}>
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
                        <span className="patient-stat-value">{analysisResult.patient_context.calculated_bmi}</span>
                      </div>
                    )}

                    <div className="patient-stat-cell" style={{ gridColumn: analysisResult.patient_context.calculated_bmi ? 'span 1' : 'span 2' }}>
                      <span className="patient-stat-label">Ordering Service</span>
                      <span className="patient-stat-value">{analysisResult.patient_context.ordering_department}</span>
                    </div>
                  </div>
                </div>

                {/* Column 2: Primary Impression & AI Evidence Score Gauge */}
                <div className="neuro-hero-card">
                  <div>
                    <div className="neuro-acuity-tag">
                      <AlertTriangle size={12} strokeWidth={1.5} />
                      <span>{analysisResult.acuity_level ? analysisResult.acuity_level.replace(/^[^\w\s—()\/]+/, '').trim() : ''}</span>
                    </div>
                    <h2 className="neuro-diag-title">{analysisResult.primary_suspected_condition}</h2>
                    
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: 1.45 }}>
                      <strong style={{ color: 'var(--text-primary)' }}>Certainty:</strong> {analysisResult.diagnostic_certainty_level}
                    </div>

                    <div style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                      <strong style={{ color: 'var(--text-primary)' }}>Confirmation:</strong> {analysisResult.required_confirmation}
                    </div>

                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                      {analysisResult.evidence_score_disclaimer}
                    </div>
                  </div>

                  {/* Horizontal Bar / Gauge per Section 4.6 */}
                  <div className="evidence-gauge-container">
                    <div className="evidence-gauge-header">
                      <div className="evidence-gauge-label">
                        <span>AI evidence score</span>
                        <button 
                          className="score-info-btn"
                          onClick={() => setRubricModalData({
                            conditionName: analysisResult.primary_suspected_condition,
                            score: analysisResult.ai_evidence_score,
                            rubric: analysisResult.rubric_breakdown
                          })}
                          title="View mathematical rubric breakdown"
                        >
                          ⓘ
                        </button>
                      </div>
                      <div className="evidence-gauge-value">
                        {analysisResult.ai_evidence_score}/100 — {
                          analysisResult.ai_evidence_score >= 76 ? 'High confidence' :
                          analysisResult.ai_evidence_score >= 41 ? 'Moderate confidence' : 'Low confidence'
                        }
                      </div>
                    </div>
                    <div className="evidence-gauge-track">
                      <div 
                        className="evidence-gauge-fill" 
                        style={{ 
                          width: `${Math.min(100, Math.max(5, analysisResult.ai_evidence_score))}%`,
                          background: analysisResult.ai_evidence_score >= 76 
                            ? 'var(--critical-accent)' 
                            : analysisResult.ai_evidence_score >= 41 
                              ? 'var(--moderate-accent)' 
                              : 'var(--good-accent)'
                        }}
                      />
                    </div>
                  </div>

                  {/* Human-in-the-Loop Feedback Controls per Section 4.11 */}
                  <div className="hitl-actions-container">
                    {feedbackLog.some(f => f.condition_name === analysisResult.primary_suspected_condition) ? (
                      (() => {
                        const logEntry = feedbackLog.find(f => f.condition_name === analysisResult.primary_suspected_condition);
                        return (
                          <div className={`hitl-logged-badge ${logEntry.action.toLowerCase()}`}>
                            {logEntry.action === 'CONFIRMED' && <Check size={12} strokeWidth={2} />}
                            {logEntry.action === 'OVERRIDDEN' && <Edit3 size={12} strokeWidth={1.5} />}
                            {logEntry.action === 'FLAGGED' && <Flag size={12} strokeWidth={1.5} />}
                            <span>{logEntry.action}: {logEntry.override_text || logEntry.clinician_id}</span>
                          </div>
                        );
                      })()
                    ) : (
                      <>
                        <button 
                          className="hitl-btn confirm"
                          onClick={() => handleConfirmFeedback({
                            condition_name: analysisResult.primary_suspected_condition,
                            ai_evidence_score: analysisResult.ai_evidence_score
                          })}
                        >
                          <Check size={13} strokeWidth={2} />
                          <span>Confirm</span>
                        </button>
                        <button 
                          className="hitl-btn override"
                          onClick={() => handleOpenOverride({
                            condition_name: analysisResult.primary_suspected_condition,
                            ai_evidence_score: analysisResult.ai_evidence_score
                          })}
                        >
                          <Edit3 size={13} strokeWidth={1.5} />
                          <span>Override</span>
                        </button>
                        <button 
                          className="hitl-btn flag"
                          onClick={() => handleOpenFlag({
                            condition_name: analysisResult.primary_suspected_condition,
                            ai_evidence_score: analysisResult.ai_evidence_score
                          })}
                        >
                          <Flag size={13} strokeWidth={1.5} />
                          <span>Flag as incorrect</span>
                        </button>
                      </>
                    )}
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
                      <Layers size={18} color="var(--accent-primary)" />
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
                              <div style={{ fontWeight: 700, color: 'var(--text-title)', marginBottom: '2px' }}>{tier.feature_name}</div>
                              <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent-terracotta)', fontSize: '0.76rem' }}>{tier.observed_finding}</div>
                            </td>
                            <td style={{ color: 'var(--text-primary)', fontSize: '0.8rem' }}>
                              {tier.clinical_interpretation}
                            </td>
                            <td style={{ color: 'var(--text-secondary)', fontSize: '0.78rem' }}>
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
                      <GitBranch size={16} strokeWidth={1.5} color="var(--brand-accent)" />
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
                            <Check size={13} strokeWidth={2} color="var(--good-accent)" />
                            <span>{node.patient_observation}</span>
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
                
                {/* Short-Term Actionable Routine (Days 1–30) */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <Zap size={16} strokeWidth={1.5} color="var(--accent-primary)" />
                      <div>
                        <h3 className="card-title">Short-Term Actionable Routine (Days 1–30)</h3>
                        <p className="card-subtitle">Immediate Daily & Weekly Protocols to Halt Risk Progression</p>
                      </div>
                    </div>
                  </div>

                  <div className="routine-grid">
                    {analysisResult.short_term_routine && analysisResult.short_term_routine.map((step, idx) => (
                      <div key={idx} className="routine-step-card short-term">
                        <div className="routine-top-row">
                          <span className="routine-title">
                            <CalendarDays size={14} strokeWidth={1.5} color="var(--text-secondary)" />
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

                {/* Long-Term Disease Prevention Protocol (Months 1–6+) */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <TrendingDown size={16} strokeWidth={1.5} color="var(--brand-accent)" />
                      <div>
                        <h3 className="card-title">Long-Term Prevention Protocol (Months 1–6+)</h3>
                        <p className="card-subtitle">Sustained Lifestyle, Surveillance & Clinical Roadmaps</p>
                      </div>
                    </div>
                  </div>

                  <div className="routine-grid">
                    {analysisResult.long_term_routine && analysisResult.long_term_routine.map((step, idx) => (
                      <div key={idx} className="routine-step-card long-term">
                        <div className="routine-top-row">
                          <span className="routine-title">
                            <ShieldCheck size={14} strokeWidth={1.5} color="var(--brand-accent)" />
                            {step.title}
                          </span>
                          <span className="routine-time-badge emerald">{step.timeframe}</span>
                        </div>
                        <p className="routine-action-text">{step.action}</p>
                        <div className="routine-goal-box">
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
                      <Activity size={16} strokeWidth={1.5} color="var(--brand-accent)" />
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
                              <td><strong>{rf.risk_factor}</strong></td>
                              <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--text-primary)', fontWeight: 600 }}>{rf.observed_value}</td>
                              <td style={{ color: 'var(--text-primary)', fontSize: '0.78rem' }}>{rf.pathophysiologic_explanation}</td>
                              <td style={{ color: 'var(--good-accent)', fontSize: '0.78rem', fontWeight: 600 }}>{rf.tailored_prevention_protocol}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    ) : (
                      <>
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
                            {(() => {
                              const allParams = analysisResult.extracted_parameters || [];
                              const criticalParams = allParams.filter(p => p.status === 'CRITICAL');
                              const displayed = showAllParams || criticalParams.length === 0 ? allParams : criticalParams;
                              return displayed.map((param, idx) => (
                                <tr key={idx}>
                                  <td><strong>{param.name}</strong></td>
                                  <td style={{ fontWeight: 600, fontFamily: 'var(--font-mono)' }}>{param.value}</td>
                                  <td>
                                    <span className={`param-status-badge ${param.status.toLowerCase()}`}>
                                      {param.status}
                                    </span>
                                  </td>
                                  <td className="param-source-citation">
                                    "{param.source_text}"
                                  </td>
                                </tr>
                              ));
                            })()}
                          </tbody>
                        </table>

                        {/* Collapsible toggle: Show all vs Show critical only */}
                        {(() => {
                          const allParams = analysisResult.extracted_parameters || [];
                          const criticalParams = allParams.filter(p => p.status === 'CRITICAL');
                          if (allParams.length > criticalParams.length && criticalParams.length > 0) {
                            return (
                              <button 
                                className="disclosure-toggle"
                                onClick={() => setShowAllParams(!showAllParams)}
                              >
                                {showAllParams ? <ChevronUp size={13} strokeWidth={1.5} /> : <ChevronDown size={13} strokeWidth={1.5} />}
                                <span>{showAllParams ? `Show critical only (${criticalParams.length} parameters)` : `Show all parameters (${allParams.length})`}</span>
                              </button>
                            );
                          }
                          return null;
                        })()}
                      </>
                    )}
                  </div>
                </div>

                {/* Differential Considerations & Confirmatory Workup */}
                <div className="glass-card">
                  <div className="card-header">
                    <div className="card-title-group">
                      <Target size={16} strokeWidth={1.5} color="var(--accent-primary)" />
                      <div>
                        <h3 className="card-title">AI Differentials & Confirmatory Workup</h3>
                        <p className="card-subtitle">Secondary Considerations & Recommended Next Steps</p>
                      </div>
                    </div>
                  </div>

                  <div className="diff-list" style={{ marginBottom: '14px' }}>
                    {analysisResult.differential_considerations.slice(0, 2).map((diff, idx) => (
                      <div key={idx} className="diff-item">
                        <div className="diff-top">
                          <span className="diff-name">{diff.condition_name}</span>
                          <span className="diff-prob" style={{ color: 'var(--text-primary)', fontWeight: 600 }}>
                            Evidence: {diff.ai_evidence_score}/100
                          </span>
                        </div>
                        <div style={{ fontSize: '0.74rem', color: 'var(--text-secondary)', margin: '2px 0' }}>
                          <strong style={{ color: 'var(--text-primary)' }}>Certainty:</strong> {diff.diagnostic_certainty}
                        </div>
                        <p className="diff-rationale">{diff.clinical_rationale}</p>
                      </div>
                    ))}
                  </div>

                  {/* Confirmatory Diagnostic Workup */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    <div style={{ fontSize: '0.72rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
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
                        <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Category: {test.category} • {test.clinical_purpose}</span>
                      </div>
                    ))}
                  </div>
                </div>

              </div>

              {/* ========================================================================= */}
              {/* BOTTOM DISCLAIMER: AI CLINICAL SAFETY NOTICE                              */}
              {/* ========================================================================= */}
              <div className="ai-safety-banner">
                <Info size={16} strokeWidth={1.5} className="ai-safety-icon" />
                <div>
                  <div className="ai-safety-title">AI Clinical Safety & Decision Support Notice</div>
                  <div className="ai-safety-text">
                    {analysisResult.ai_safety_notice}
                  </div>
                </div>
              </div>

            </div>
            )}
            </>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 2: INDIVIDUAL CARDIOLOGY ENSEMBLE (SCREENSHOT THEME & LAYOUT)         */}
      {/* ========================================================================= */}
      {activeTab === 'heart' && (
        <div className="two-col-grid">
          {/* Left Column: Form Profile */}
          <section className="glass-card">
            <h2 className="card-title">Patient Profile</h2>
            <p className="card-subtitle">Enter the 13 clinical features for predictive analysis.</p>
            
            <form onSubmit={handleHeartPredict} style={{ marginTop: '20px' }}>
              <div className="form-grid">
                <div className="field-group">
                  <label className="field-label">Age</label>
                  <input type="number" className="field-input" value={heartForm.age} onChange={e => setHeartForm({...heartForm, age: parseFloat(e.target.value)})} />
                </div>
                
                <div className="field-group">
                  <label className="field-label">Sex</label>
                  <select className="field-input" value={heartForm.sex} onChange={e => setHeartForm({...heartForm, sex: parseInt(e.target.value)})}>
                    <option value={1}>Male</option>
                    <option value={0}>Female</option>
                  </select>
                </div>

                <div className="field-group">
                  <label className="field-label">Chest Pain Type (0-3)</label>
                  <input type="number" className="field-input" value={heartForm.cp} onChange={e => setHeartForm({...heartForm, cp: parseInt(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Resting BP (trestbps)</label>
                  <input type="number" className="field-input" value={heartForm.trestbps} onChange={e => setHeartForm({...heartForm, trestbps: parseFloat(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Cholesterol (mg/dl)</label>
                  <input type="number" className="field-input" value={heartForm.chol} onChange={e => setHeartForm({...heartForm, chol: parseFloat(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Fasting Blood Sugar &gt; 120 mg/dl</label>
                  <select className="field-input" value={heartForm.fbs} onChange={e => setHeartForm({...heartForm, fbs: parseInt(e.target.value)})}>
                    <option value={0}>No</option>
                    <option value={1}>Yes</option>
                  </select>
                </div>

                <div className="field-group">
                  <label className="field-label">Resting ECG (0-2)</label>
                  <input type="number" className="field-input" value={heartForm.restecg} onChange={e => setHeartForm({...heartForm, restecg: parseInt(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Max Heart Rate (thalach)</label>
                  <input type="number" className="field-input" value={heartForm.thalach} onChange={e => setHeartForm({...heartForm, thalach: parseFloat(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Exercise Angina (exang)</label>
                  <select className="field-input" value={heartForm.exang} onChange={e => setHeartForm({...heartForm, exang: parseInt(e.target.value)})}>
                    <option value={0}>No</option>
                    <option value={1}>Yes</option>
                  </select>
                </div>

                <div className="field-group">
                  <label className="field-label">ST Depression (oldpeak)</label>
                  <input type="number" step="0.1" className="field-input" value={heartForm.oldpeak} onChange={e => setHeartForm({...heartForm, oldpeak: parseFloat(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Slope (0-2)</label>
                  <input type="number" className="field-input" value={heartForm.slope} onChange={e => setHeartForm({...heartForm, slope: parseInt(e.target.value)})} />
                </div>

                <div className="field-group">
                  <label className="field-label">Major Vessels (ca) (0-4)</label>
                  <input type="number" className="field-input" value={heartForm.ca} onChange={e => setHeartForm({...heartForm, ca: parseInt(e.target.value)})} />
                </div>

                <div className="field-group" style={{ gridColumn: 'span 2' }}>
                  <label className="field-label">Thalassemia (thal) (0-3)</label>
                  <input type="number" className="field-input" value={heartForm.thal} onChange={e => setHeartForm({...heartForm, thal: parseInt(e.target.value)})} />
                </div>
              </div>

              <button type="submit" className="analyze-main-btn" style={{ width: '100%' }} disabled={heartLoading}>
                {heartLoading ? 'Calculating Risk...' : 'Predict Risk'}
              </button>
            </form>
          </section>

          {/* Right Column: Circular Gauge, Top Factors & Roadmap */}
          {heartPred && (
            <section className="glass-card">
              {/* Circular Donut Gauge */}
              <div className="gauge-top-container">
                <div 
                  className="gauge-circle-wrap" 
                  style={{ '--risk-deg': `${(heartPred.risk_percentage * 3.6)}deg` }}
                >
                  <div className="gauge-circle-inner">
                    {heartPred.risk_percentage}%
                  </div>
                </div>

                <div className="gauge-meta-wrap">
                  <span className="gauge-risk-badge">
                    {heartPred.risk_label}
                  </span>
                  <p className="gauge-risk-desc">
                    Based on your cardiovascular profile ({heartPred.confidence_interval || '95% CI: ± 3.2%'}).
                  </p>
                </div>
              </div>

              {/* Top Risk Factors (Dual-Color Horizontal Split Bars) */}
              <div style={{ marginTop: '20px' }}>
                <h3 className="card-title" style={{ fontSize: '1.05rem', marginBottom: '2px' }}>Top Risk Factors</h3>
                <p className="card-subtitle" style={{ marginBottom: '16px' }}>What's driving your score</p>

                {heartPred.shap_factors?.slice(0, 5).map((f, i) => (
                  <div key={i} className="shap-bar-row">
                    <span className="shap-bar-label">{f.feature}</span>
                    <div className="shap-bar-track">
                      <div 
                        className="shap-bar-fill" 
                        style={{
                          width: `${Math.min(100, Math.abs(f.shap_value) * 35)}%`,
                          background: f.shap_value > 0 ? 'var(--accent-terracotta)' : 'var(--accent-forest)',
                          left: f.shap_value > 0 ? '50%' : undefined,
                          right: f.shap_value <= 0 ? '50%' : undefined
                        }}
                      />
                    </div>
                    <span 
                      className="shap-bar-val"
                      style={{ color: f.shap_value > 0 ? 'var(--accent-terracotta)' : 'var(--accent-forest)' }}
                    >
                      {f.shap_value > 0 ? `+${f.shap_value.toFixed(2)}` : f.shap_value.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>

              {/* 3-Column Risk Reduction Roadmap */}
              <div className="roadmap-container">
                <div className="roadmap-header-row">
                  <div>
                    <h3 className="card-title" style={{ fontSize: '1.05rem' }}>Risk Reduction Roadmap</h3>
                    <p className="card-subtitle">Potential improvements based on your profile.</p>
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.85rem', color: 'var(--text-muted)' }}>{heartForm.chol} → 170</span>
                    <span style={{ display: 'block', fontSize: '0.76rem', color: 'var(--accent-forest)', fontWeight: 700 }}>-36% risk</span>
                  </div>
                </div>

                <div className="roadmap-cols-grid">
                  <div className="roadmap-col short">
                    <div className="roadmap-col-title">SHORT TERM</div>
                    <p className="roadmap-col-text">
                      • Cut saturated fat intake; aim to lower cholesterol by 10-15 mg/dL in 4-6 weeks.
                    </p>
                  </div>

                  <div className="roadmap-col medium">
                    <div className="roadmap-col-title">MEDIUM TERM</div>
                    <p className="roadmap-col-text">
                      • Adopt a Mediterranean-style diet consistently for 3 months with 150 min/wk exercise.
                    </p>
                  </div>

                  <div className="roadmap-col long">
                    <div className="roadmap-col-title">LONG TERM</div>
                    <p className="roadmap-col-text">
                      • Target cholesterol under 200 mg/dL and sustained BP &lt; 120/80 within 6-12 months.
                    </p>
                  </div>
                </div>
              </div>

            </section>
          )}
        </div>
      )}

      {/* ========================================================================= */}
      {/* TAB 3: INDIVIDUAL DIABETES ENSEMBLE                                       */}
      {/* ========================================================================= */}
      {activeTab === 'diabetes' && (
        <div className="two-col-grid">
          <section className="glass-card">
            <h2 className="card-title">Diabetes Metabolic Profile</h2>
            <p className="card-subtitle">Pima Indians Dataset • Gradient Boosted Ensemble with TreeSHAP</p>
            
            <form onSubmit={handleDiabPredict} style={{ marginTop: '20px' }}>
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

              <button type="submit" className="analyze-main-btn" style={{ width: '100%' }} disabled={diabLoading}>
                {diabLoading ? 'Calculating Risk...' : 'Predict Diabetes Risk'}
              </button>
            </form>
          </section>

          {diabResult && (
            <section className="glass-card">
              <div className="gauge-top-container">
                <div 
                  className="gauge-circle-wrap" 
                  style={{ '--risk-deg': `${(diabResult.risk_percentage * 3.6)}deg` }}
                >
                  <div className="gauge-circle-inner">
                    {diabResult.risk_percentage}%
                  </div>
                </div>

                <div className="gauge-meta-wrap">
                  <span className="gauge-risk-badge">
                    {diabResult.risk_label}
                  </span>
                  <p className="gauge-risk-desc">
                    Based on metabolic biomarkers ({diabResult.confidence_interval}).
                  </p>
                </div>
              </div>

              <div style={{ marginTop: '20px' }}>
                <h3 className="card-title" style={{ fontSize: '1.05rem', marginBottom: '2px' }}>Top SHAP Attribution Drivers</h3>
                <p className="card-subtitle" style={{ marginBottom: '16px' }}>What's driving your score</p>

                {diabResult.top_positive_factors?.slice(0, 4).map((f, i) => (
                  <div key={i} className="shap-bar-row">
                    <span className="shap-bar-label">{f.feature_name}</span>
                    <div className="shap-bar-track">
                      <div 
                        className="shap-bar-fill" 
                        style={{
                          width: `${Math.min(100, Math.abs(f.shap_value) * 35)}%`,
                          background: f.shap_value > 0 ? 'var(--accent-terracotta)' : 'var(--accent-forest)',
                          left: f.shap_value > 0 ? '50%' : undefined,
                          right: f.shap_value <= 0 ? '50%' : undefined
                        }}
                      />
                    </div>
                    <span 
                      className="shap-bar-val"
                      style={{ color: f.shap_value > 0 ? 'var(--accent-terracotta)' : 'var(--accent-forest)' }}
                    >
                      {f.shap_value > 0 ? `+${f.shap_value.toFixed(2)}` : f.shap_value.toFixed(2)}
                    </span>
                  </div>
                ))}
              </div>
            </section>
          )}
        </div>
      )}



      {/* ========================================================================= */}
      {/* CLINICAL MODEL CARD SPECIFICATION                                         */}
      {/* ========================================================================= */}
      {activeTab === 'model-card' && (
        <ModelCardView 
          onNavigateToHistory={() => setActiveTab('history')} 
        />
      )}

      {/* ========================================================================= */}
      {/* TAB 6: CLINICAL IMAGING & WAVEFORMS (1D-CNN & DENSENET-121)               */}
      {/* ========================================================================= */}
      {activeTab === 'imaging' && (
        <ImagingView 
          apiBase={API_BASE} 
          token={token}
          user={user}
          onScanComplete={fetchFeedbackHistory}
        />
      )}

      {/* ========================================================================= */}
      {/* TAB: PRE-CONFIGURED CLINICAL CASES (SEPARATE DEDICATED TAB)              */}
      {/* ========================================================================= */}
      {activeTab === 'presets' && (
        <PresetCasesView 
          samples={sampleReports}
          onSelectCase={(sample) => {
            setSelectedPresetId(sample.id);
            setClinicalText(sample.text);
            setActiveTab('universal');
          }}
          onRunAnalysis={(sampleText) => {
            setClinicalText(sampleText);
            setActiveTab('universal');
            executeUniversalAnalysis(sampleText, true);
          }}
        />
      )}

      {/* ========================================================================= */}
      {/* TAB 7: PERSONAL HEALTH HISTORY (per-user, isolated)                       */}
      {/* ========================================================================= */}
      {activeTab === 'history' && (
        <HealthHistory 
          user={user} 
          token={token} 
          onNavigateToScanner={() => setActiveTab('universal')}
        />
      )}

      {/* Footer */}
      <footer className="disclaimer-bar">
        <p>
          <strong>HealthGuard AI — Clinical Decision Support & Prevention Prototype:</strong> Designed for clinical education and workflow decision support. AI evidence scores and decision tree traversal paths do not replace formal in-person diagnostic evaluation or physician judgment.
        </p>
      </footer>
      </div>

      {/* Modals & Dialogs */}
      <RubricModal 
        isOpen={!!rubricModalData} 
        onClose={() => setRubricModalData(null)} 
        data={rubricModalData}
        onNavigateToModelCard={() => {
          setRubricModalData(null);
          setActiveTab('model-card');
        }}
      />

      <AuditLogModal 
        isOpen={auditLogModalOpen} 
        onClose={() => setAuditLogModalOpen(false)} 
        feedbackLog={feedbackLog}
        onClearLog={handleClearAuditLog}
      />

      <OverrideModal 
        isOpen={!!overrideModalData} 
        onClose={() => setOverrideModalData(null)} 
        data={overrideModalData}
        onSubmitFeedback={handleCommitFeedback}
      />
    </div>
  );
}
