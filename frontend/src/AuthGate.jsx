
import React, { useState } from 'react';
import App from './App.jsx';
import AuthPage from './components/AuthPage.jsx';

export default function AuthGate() {
    const [authenticated, setAuthenticated] = useState(
        () => Boolean(sessionStorage.getItem('healthguard_access_token'))
    );

    if (!authenticated) {
        return <AuthPage onAuthenticated={() => setAuthenticated(true)} />;
    }

    return (
        <>
            <div className="auth-session-bar">
                <span>Signed in to HealthGuard AI</span>
                <button
                    type="button"
                    onClick={() => {
                        sessionStorage.removeItem('healthguard_access_token');
                        setAuthenticated(false);
                    }}
                >
                    Sign out
                </button>
            </div>
            <App />
        </>
    );
}