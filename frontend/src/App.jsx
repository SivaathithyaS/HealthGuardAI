import { useState } from 'react';

const INITIAL_STATE = {
  age: 50,
  sex: 1,
  cp: 0,
  trestbps: 120,
  chol: 200,
  fbs: 0,
  restecg: 0,
  thalach: 150,
  exang: 0,
  oldpeak: 1.0,
  slope: 1,
  ca: 0,
  thal: 2,
};

export default function App() {
  const [formData, setFormData] = useState(INITIAL_STATE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === 'oldpeak' ? parseFloat(value) : parseInt(value, 10),
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const [predictRes, roadmapRes] = await Promise.all([
        fetch('http://localhost:8000/predict/heart', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        }),
        fetch('http://localhost:8000/roadmap/heart', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(formData),
        })
      ]);

      if (!predictRes.ok) {
        throw new Error(`Predict API Error: ${predictRes.statusText}`);
      }
      if (!roadmapRes.ok) {
        throw new Error(`Roadmap API Error: ${roadmapRes.statusText}`);
      }

      const predictData = await predictRes.json();
      const roadmapData = await roadmapRes.json();

      setResults({ predict: predictData, roadmap: roadmapData });
    } catch (err) {
      setError(err.message || 'An error occurred while fetching data');
    } finally {
      setLoading(false);
    }
  };

  const renderRiskRing = () => {
    if (!results) return null;
    const { risk_score, risk_label } = results.predict;
    
    const percentage = risk_score * 100;
    const radius = 38;
    const circumference = 2 * Math.PI * radius;
    const strokeDashoffset = circumference - (percentage / 100) * circumference;

    let color = 'var(--teal)';
    if (risk_label.toLowerCase() === 'moderate') color = 'var(--amber)';
    if (risk_label.toLowerCase() === 'high') color = 'var(--coral)';

    return (
      <div className="risk-header">
        <div className="risk-ring">
          <svg width="84" height="84" viewBox="0 0 84 84">
            <circle cx="42" cy="42" r={radius} fill="none" stroke="var(--line)" strokeWidth="6" />
            <circle 
              cx="42" 
              cy="42" 
              r={radius} 
              fill="none" 
              stroke={color} 
              strokeWidth="6" 
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
            />
          </svg>
          <div className="risk-ring-value">
            {Math.round(percentage)}%
          </div>
        </div>
        <div>
          <span className={`risk-label ${risk_label.toLowerCase()}`}>{risk_label} Risk</span>
          <p className="risk-copy">Based on your cardiovascular profile.</p>
        </div>
      </div>
    );
  };

  const renderShapFactors = () => {
    if (!results || !results.predict.top_factors) return null;
    const { top_factors } = results.predict;
    
    const top5 = [...top_factors]
      .sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value))
      .slice(0, 5);

    const maxVal = Math.max(...top5.map(f => Math.abs(f.shap_value)));

    return (
      <div className="results-stack">
        <div>
          <h2>Top Risk Factors</h2>
          <p className="card-sub">What's driving your score</p>
          {top5.map((factor, idx) => {
            const isPositive = factor.shap_value > 0;
            const widthPct = maxVal > 0 ? (Math.abs(factor.shap_value) / maxVal) * 50 : 0;
            
            return (
              <div key={idx} className="shap-row">
                <div className="shap-feature">{factor.feature}</div>
                <div className="shap-bar-track">
                  {isPositive ? (
                    <div className="shap-bar-fill up" style={{ width: `${widthPct}%` }}></div>
                  ) : (
                    <div className="shap-bar-fill down" style={{ width: `${widthPct}%` }}></div>
                  )}
                </div>
                <div className="shap-value">
                  {isPositive ? '+' : ''}{factor.shap_value.toFixed(2)}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  const renderRoadmap = () => {
    if (!results || !results.roadmap) return null;
    const { what_if, goals } = results.roadmap;

    return (
      <div className="results-stack" style={{ marginTop: '24px' }}>
        <div>
          <h2>Risk Reduction Roadmap</h2>
          <p className="roadmap-intro">Potential improvements based on your profile.</p>
          
          {what_if && what_if.length > 0 && (
            <div style={{ marginBottom: '24px' }}>
              {what_if.map((item, idx) => {
                const isNegativeReduction = item.risk_reduction < 0;
                return (
                  <div key={idx} className="whatif-row">
                    <div>
                      <div className="whatif-change">{item.change}</div>
                    </div>
                    <div className={`whatif-delta ${isNegativeReduction ? 'negative' : ''}`}>
                      {item.risk_reduction > 0 ? '-' : '+'}{Math.abs(Math.round(item.risk_reduction * 100))}% risk
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {goals && (
            <div className="timeline">
              {goals.short_term && goals.short_term.length > 0 && (
                <div className="timeline-stage">
                  <h3>Short Term</h3>
                  <ul>
                    {goals.short_term.map((g, i) => <li key={i}>{g}</li>)}
                  </ul>
                </div>
              )}
              {goals.medium_term && goals.medium_term.length > 0 && (
                <div className="timeline-stage medium">
                  <h3>Medium Term</h3>
                  <ul>
                    {goals.medium_term.map((g, i) => <li key={i}>{g}</li>)}
                  </ul>
                </div>
              )}
              {goals.long_term && goals.long_term.length > 0 && (
                <div className="timeline-stage long">
                  <h3>Long Term</h3>
                  <ul>
                    {goals.long_term.map((g, i) => <li key={i}>{g}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="app-shell">
      <div className="brand">
        <div className="brand-mark">HealthGuard AI</div>
        <div className="brand-tag">v1.0</div>
      </div>
      <p className="subhead">
        Advanced cardiovascular risk assessment powered by machine learning. 
        Enter patient vitals below for an instant predictive analysis and customized reduction roadmap.
      </p>

      <div className="layout">
        <div className="card">
          <h2>Patient Profile</h2>
          <p className="card-sub">Enter the 13 clinical features.</p>
          
          <form onSubmit={handleSubmit}>
            <div className="field-grid">
              <div className="field">
                <label>Age</label>
                <input type="number" name="age" value={formData.age} onChange={handleChange} min="1" max="120" required />
              </div>
              <div className="field">
                <label>Sex</label>
                <select name="sex" value={formData.sex} onChange={handleChange}>
                  <option value={1}>Male</option>
                  <option value={0}>Female</option>
                </select>
              </div>
              <div className="field">
                <label>Chest Pain Type (0-3)</label>
                <input type="number" name="cp" value={formData.cp} onChange={handleChange} min="0" max="3" required />
              </div>
              <div className="field">
                <label>Resting BP (trestbps)</label>
                <input type="number" name="trestbps" value={formData.trestbps} onChange={handleChange} min="60" max="250" required />
              </div>
              <div className="field">
                <label>Cholesterol (mg/dl)</label>
                <input type="number" name="chol" value={formData.chol} onChange={handleChange} min="100" max="600" required />
              </div>
              <div className="field">
                <label>Fasting Blood Sugar &gt; 120 mg/dl</label>
                <select name="fbs" value={formData.fbs} onChange={handleChange}>
                  <option value={0}>No</option>
                  <option value={1}>Yes</option>
                </select>
              </div>
              <div className="field">
                <label>Resting ECG (0-2)</label>
                <input type="number" name="restecg" value={formData.restecg} onChange={handleChange} min="0" max="2" required />
              </div>
              <div className="field">
                <label>Max Heart Rate (thalach)</label>
                <input type="number" name="thalach" value={formData.thalach} onChange={handleChange} min="60" max="250" required />
              </div>
              <div className="field">
                <label>Exercise Angina (exang)</label>
                <select name="exang" value={formData.exang} onChange={handleChange}>
                  <option value={0}>No</option>
                  <option value={1}>Yes</option>
                </select>
              </div>
              <div className="field">
                <label>ST Depression (oldpeak)</label>
                <input type="number" step="0.1" name="oldpeak" value={formData.oldpeak} onChange={handleChange} min="0" max="10" required />
              </div>
              <div className="field">
                <label>Slope (0-2)</label>
                <input type="number" name="slope" value={formData.slope} onChange={handleChange} min="0" max="2" required />
              </div>
              <div className="field">
                <label>Major Vessels (ca) (0-4)</label>
                <input type="number" name="ca" value={formData.ca} onChange={handleChange} min="0" max="4" required />
              </div>
              <div className="field full">
                <label>Thalassemia (thal) (0-3)</label>
                <input type="number" name="thal" value={formData.thal} onChange={handleChange} min="0" max="3" required />
              </div>
            </div>

            <button type="submit" className="submit-btn" disabled={loading}>
              {loading ? 'Analyzing...' : 'Predict Risk'}
            </button>
          </form>
        </div>

        <div>
          {error && <div className="error-banner">{error}</div>}
          
          {!results && !error && !loading && (
            <div className="empty-state">
              Submit the form to view predictive analysis and risk reduction roadmap.
            </div>
          )}

          {results && (
            <div className="card">
              <div className="results-stack">
                {renderRiskRing()}
                {renderShapFactors()}
              </div>
              {renderRoadmap()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
