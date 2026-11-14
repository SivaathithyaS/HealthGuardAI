import React from 'react';
import ReactDOM from 'react-dom/client';
import AuthGate from './AuthGate.jsx';
import './index.css';
import './components/AuthPage.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  componentDidCatch(error, errorInfo) {
    console.error("HealthGuard AI ErrorBoundary caught an error:", error, errorInfo);
  }
  handleReset = () => {
    sessionStorage.clear();
    window.location.reload();
  };
  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          background: '#0f1a17',
          color: '#e2e8f0',
          fontFamily: 'Inter, system-ui, sans-serif',
          padding: '20px',
          textAlign: 'center'
        }}>
          <h2 style={{ color: '#ef4444', marginBottom: '8px' }}>HealthGuard AI</h2>
          <p style={{ color: '#94a3b8', maxWidth: '480px', marginBottom: '20px', fontSize: '14px' }}>
            {this.state.error?.message || "An unexpected error occurred while rendering the workspace."}
          </p>
          <button 
            onClick={this.handleReset}
            style={{
              padding: '10px 22px',
              borderRadius: '8px',
              background: '#0e3b38',
              color: '#ffffff',
              border: 'none',
              cursor: 'pointer',
              fontWeight: 600,
              fontSize: '14px'
            }}
          >
            Clear Session & Reload
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <AuthGate />
    </ErrorBoundary>
  </React.StrictMode>
);