
import React, { useState, useEffect } from 'react';
import App from './App.jsx';
import AuthPage from './components/AuthPage.jsx';

const API_BASE = 'http://localhost:8000';

/**
 * AuthGate
 * ────────
 * - Persists access_token in sessionStorage (tab-scoped, not shared between tabs)
 * - On mount, calls /api/auth/me to hydrate the user object from the token
 * - Passes { user, token, onSignOut } down to App so history & greetings work
 */
export default function AuthGate() {
    const [token, setToken] = useState(
        () => sessionStorage.getItem('healthguard_access_token') || null
    );
    const [user, setUser] = useState(null);
    const [hydrating, setHydrating] = useState(Boolean(token));

    // Hydrate user from existing token on mount / token change
    useEffect(() => {
        if (!token) {
            setUser(null);
            setHydrating(false);
            return;
        }

        setHydrating(true);
        fetch(`${API_BASE}/api/auth/me`, {
            headers: { Authorization: `Bearer ${token}` }
        })
            .then(res => {
                if (!res.ok) throw new Error('invalid');
                return res.json();
            })
            .then(data => {
                setUser(data);
                setHydrating(false);
            })
            .catch(() => {
                // Token invalid or server offline — clear it
                sessionStorage.removeItem('healthguard_access_token');
                setToken(null);
                setUser(null);
                setHydrating(false);
            });
    }, [token]);

    const handleAuthenticated = (newToken, userInfo) => {
        sessionStorage.setItem('healthguard_access_token', newToken);
        setToken(newToken);
        setUser(userInfo);
    };

    const handleSignOut = async () => {
        try {
            await fetch(`${API_BASE}/api/auth/logout`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` }
            });
        } catch { /* server may be offline */ }
        sessionStorage.removeItem('healthguard_access_token');
        setToken(null);
        setUser(null);
    };

    if (hydrating) {
        return (
            <div style={{
                minHeight: '100vh',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background: 'var(--bg-base, #0f1a17)',
                color: 'var(--text-muted, #8B948E)',
                fontFamily: 'Inter, system-ui, sans-serif',
                fontSize: '14px',
                gap: '10px'
            }}>
                <span style={{ opacity: 0.6 }}>Restoring session…</span>
            </div>
        );
    }

    if (!token || !user) {
        return <AuthPage onAuthenticated={handleAuthenticated} />;
    }

    return <App user={user} token={token} onSignOut={handleSignOut} />;
}