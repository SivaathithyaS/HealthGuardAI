
import React, { useState } from 'react';
import {
  ArrowLeft,
  ArrowRight,
  CheckCircle2,
  Eye,
  EyeOff,
  HeartPulse,
  KeyRound,
  LockKeyhole,
  Mail,
  ShieldCheck,
  UserRound
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

export default function AuthPage({ onAuthenticated }) {
  const [mode, setMode] = useState('signin');
  const [showPassword, setShowPassword] = useState(false);
  const [otpSent, setOtpSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState(null);

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    otp: ''
  });

  const update = (field) => (event) => {
    setForm((current) => ({
      ...current,
      [field]: event.target.value
    }));
    setNotice(null);
  };

  const changeMode = (nextMode) => {
    setMode(nextMode);
    setOtpSent(false);
    setShowPassword(false);
    setNotice(null);
    setForm({
      name: '',
      email: '',
      password: '',
      otp: ''
    });
  };

  const request = async (path, payload) => {
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
      throw new Error(
        data.detail ||
        data.message ||
        'The request could not be completed.'
      );
    }

    return data;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setBusy(true);
    setNotice(null);

    try {
      if (mode === 'register' && !otpSent) {
        await request('/api/auth/register/send-otp', {
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password
        });

        setOtpSent(true);
        setNotice({
          type: 'success',
          text: 'Verification code sent. Check your email and enter the code below.'
        });
      } else if (mode === 'register') {
        const data = await request(
          '/api/auth/register/verify-otp',
          {
            email: form.email.trim(),
            otp: form.otp.trim()
          }
        );

        setMode('signin');
        setOtpSent(false);
        setForm({
          name: '',
          email: form.email.trim(),
          password: '',
          otp: ''
        });

        setNotice({
          type: 'success',
          text: data.message ||
            'Email verified. Your account is ready. Please sign in.'
        });
      } else if (mode === 'signin') {
        const data = await request('/api/auth/login', {
          name: form.name.trim(),
          email: form.email.trim(),
          password: form.password
        });

        const token = data.access_token || data.token;

        if (!token) {
          throw new Error(
            'The server did not return an access token.'
          );
        }

        sessionStorage.setItem(
          'healthguard_access_token',
          token
        );

        onAuthenticated();
      } else if (mode === 'forgot') {
        const data = await request(
          '/api/auth/forgot-password',
          { email: form.email.trim() }
        );

        setNotice({
          type: 'success',
          text: data.message ||
            'If an account exists for this email, password-reset instructions have been sent.'
        });
      }
    } catch (error) {
      setNotice({
        type: 'error',
        text: error.message.includes('Failed to fetch')
          ? 'Cannot reach the authentication API. Check that FastAPI is running and the authentication endpoints are implemented.'
          : error.message
      });
    } finally {
      setBusy(false);
    }
  };

  const isRegister = mode === 'register';
  const isForgot = mode === 'forgot';

  const title = isRegister
    ? otpSent ? 'Verify your email' : 'Create your account'
    : isForgot
      ? 'Reset your password'
      : 'Welcome back';

  const subtitle = isRegister
    ? otpSent
      ? 'Enter the one-time code sent to your inbox.'
      : 'Create a secure account for your health workspace.'
    : isForgot
      ? 'We will send password-reset instructions if an account exists.'
      : 'Sign in to continue to your clinical intelligence workspace.';

  return (
    <main className="auth-page">
      <section className="auth-story">
        <div className="auth-story-top">
          <div className="auth-brand-mark">
            <HeartPulse size={25} />
          </div>

          <div>
            <div className="auth-brand-name">
              HealthGuard <span>AI</span>
            </div>
            <div className="auth-brand-caption">
              CLINICAL INTELLIGENCE PLATFORM
            </div>
          </div>
        </div>

        <div className="auth-story-content">
          <div className="auth-eyebrow">
            <span className="auth-live-dot" />
            PREVENTION, WITH CLARITY
          </div>

          <h1>
            Better insight.
            <br />
            <em>More informed</em>
            <br />
            care.
          </h1>

          <p className="auth-story-description">
            A clinical decision-support workspace bringing medical
            reports, explainable AI, and prevention insights together.
          </p>
        </div>

        <div className="auth-decoration auth-decoration-one" />
        <div className="auth-decoration auth-decoration-two" />
      </section>

      <section className="auth-form-side">
        <div className="auth-mobile-brand">
          <div className="auth-brand-mark">
            <HeartPulse size={22} />
          </div>
          <div className="auth-brand-name">
            HealthGuard <span>AI</span>
          </div>
        </div>

        <div className="auth-form-wrap">
          <div className="auth-form-kicker">
            {isRegister
              ? 'GET STARTED'
              : isForgot
                ? 'ACCOUNT RECOVERY'
                : 'SECURE ACCESS'}
          </div>

          <h2>{title}</h2>
          <p className="auth-form-subtitle">{subtitle}</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            {(mode === 'signin' ||
              (isRegister && !otpSent)) && (
              <label className="auth-field">
                <span>Full name</span>
                <div className="auth-input-wrap">
                  <UserRound size={18} aria-hidden="true" />
                  <input
                    autoComplete="name"
                    value={form.name}
                    onChange={update('name')}
                    placeholder="Enter your full name"
                    required
                  />
                </div>
              </label>
            )}

            {(!isRegister || !otpSent) && (
              <label className="auth-field">
                <span>Email address</span>
                <div className="auth-input-wrap">
                  <Mail size={18} aria-hidden="true" />
                  <input
                    type="email"
                    autoComplete="email"
                    value={form.email}
                    onChange={update('email')}
                    placeholder="you@example.com"
                    required
                  />
                </div>
              </label>
            )}

            {(mode === 'signin' ||
              (isRegister && !otpSent)) && (
              <label className="auth-field">
                <span>Password</span>
                <div className="auth-input-wrap">
                  <LockKeyhole size={18} aria-hidden="true" />
                  <input
                    type={showPassword ? 'text' : 'password'}
                    autoComplete={
                      isRegister ? 'new-password' : 'current-password'
                    }
                    minLength={8}
                    value={form.password}
                    onChange={update('password')}
                    placeholder={
                      isRegister
                        ? 'Create a password (8+ characters)'
                        : 'Enter your password'
                    }
                    required
                  />

                  <button
                    className="auth-password-toggle"
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    aria-label={
                      showPassword ? 'Hide password' : 'Show password'
                    }
                  >
                    {showPassword
                      ? <EyeOff size={17} />
                      : <Eye size={17} />}
                  </button>
                </div>
              </label>
            )}

            {isRegister && otpSent && (
              <label className="auth-field">
                <span>Email verification code</span>
                <div className="auth-input-wrap">
                  <KeyRound size={18} aria-hidden="true" />
                  <input
                    inputMode="numeric"
                    autoComplete="one-time-code"
                    maxLength={8}
                    value={form.otp}
                    onChange={update('otp')}
                    placeholder="Enter the code from your email"
                    required
                  />
                </div>
                <small className="auth-field-help">
                  Check your inbox and spam folder.
                </small>
              </label>
            )}

            {isForgot && (
              <div className="auth-reset-note">
                <ShieldCheck size={17} />
                <span>
                  For your security, we won't reveal whether an email
                  address has an account.
                </span>
              </div>
            )}

            {notice && (
              <div
                className={`auth-notice ${notice.type}`}
                role="status"
              >
                {notice.type === 'success'
                  ? <CheckCircle2 size={17} />
                  : <ShieldCheck size={17} />}
                <span>{notice.text}</span>
              </div>
            )}

            <button
              className="auth-submit"
              type="submit"
              disabled={busy}
            >
              <span>
                {busy
                  ? 'Please wait…'
                  : isRegister
                    ? otpSent
                      ? 'Verify email'
                      : 'Send verification code'
                    : isForgot
                      ? 'Send reset instructions'
                      : 'Sign in'}
              </span>
              {!busy && <ArrowRight size={18} />}
            </button>

            {mode === 'signin' && (
              <div className="auth-forgot-row">
                <button
                  type="button"
                  className="auth-text-link"
                  onClick={() => changeMode('forgot')}
                >
                  Forgot password?
                </button>
              </div>
            )}

            {isRegister && otpSent && (
              <button
                type="button"
                className="auth-resend-link"
                onClick={() => {
                  setOtpSent(false);
                  setNotice({
                    type: 'success',
                    text: 'You can request a new verification code.'
                  });
                }}
              >
                Back to registration
              </button>
            )}
          </form>

          <div className="auth-form-divider">
            <span />
            <small>
              {isRegister
                ? 'ALREADY HAVE AN ACCOUNT?'
                : isForgot
                  ? 'REMEMBER YOUR PASSWORD?'
                  : 'NEW TO HEALTHGUARD AI?'}
            </small>
            <span />
          </div>

          <button
            className="auth-switch"
            type="button"
            onClick={() =>
              changeMode(
                isRegister || isForgot ? 'signin' : 'register'
              )
            }
          >
            {isRegister || isForgot
              ? <><ArrowLeft size={16} /> Back to sign in</>
              : <>Create an account <ArrowRight size={16} /></>}
          </button>

        </div>

        <div className="auth-bottom-note">
          <span>© HealthGuard AI</span>
        </div>
      </section>
    </main>
  );
}
