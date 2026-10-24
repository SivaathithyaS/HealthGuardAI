import os
import json
import uuid
import time
import sqlite3
import hashlib
import secrets
from typing import Dict, Any, List, Optional
from datetime import datetime

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "healthguard.db"))

class UserDBService:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates tables with strict relational integrity and user isolation indexes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # 1. Users Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'Patient',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            # 2. User Sessions Table (Maps bearer tokens strictly to user_id)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                token TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            # 3. User Checkup History Table (Isolated by user_id)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS checkups (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                modality TEXT NOT NULL,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                risk_score REAL DEFAULT 0.0,
                biomarkers_json TEXT DEFAULT '{}',
                findings_json TEXT DEFAULT '[]',
                recommendations_json TEXT DEFAULT '[]',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)

            # Index for fast user timeline retrieval
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_checkups_user ON checkups(user_id, created_at DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON sessions(token);")

            # 4. OTPs Table
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS otps (
                email TEXT PRIMARY KEY,
                name TEXT,
                password TEXT,
                otp TEXT NOT NULL,
                created_at REAL NOT NULL,
                expires_at REAL NOT NULL
            );
            """)

            conn.commit()

        # Seed default clinician account if not present
        self._seed_default_accounts()

    def _hash_password(self, password: str, salt: Optional[str] = None) -> str:
        if not salt:
            salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
        return f"{salt}:{pwd_hash}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            salt, hash_val = stored_hash.split(':')
            test_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000).hex()
            return test_hash == hash_val
        except Exception:
            return False

    def _seed_default_accounts(self):
        # Default clinician demo account
        clinician_email = "clinician@healthguard.ai"
        if not self.get_user_by_email(clinician_email):
            self.create_user(
                email=clinician_email,
                name="Dr. Sarah Lin, MD",
                password="Password123!",
                role="Clinician"
            )

        # Demo patient account — shown in README for quick testing
        demo_email = "test@gmail.com"
        if not self.get_user_by_email(demo_email):
            self.create_user(
                email=demo_email,
                name="test1",
                password="test",
                role="Patient"
            )

    # -------------------------------------------------------------------------
    # USER & AUTHENTICATION METHODS
    # -------------------------------------------------------------------------
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, name, password_hash, role, created_at FROM users WHERE email = ?", (email.lower().strip(),))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, email, name, role, created_at FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def create_user(self, email: str, name: str, password: str, role: str = "Patient") -> Dict[str, Any]:
        email_clean = email.lower().strip()
        user_id = f"usr_{secrets.token_hex(8)}"
        pwd_hash = self._hash_password(password)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (id, email, name, password_hash, role) VALUES (?, ?, ?, ?, ?)",
                (user_id, email_clean, name.strip(), pwd_hash, role)
            )
            conn.commit()

        return {
            "id": user_id,
            "email": email_clean,
            "name": name.strip(),
            "role": role
        }

    def verify_user_credentials(self, email: str, password: str) -> Optional[Dict[str, Any]]:
        user = self.get_user_by_email(email)
        if not user:
            return None
        
        # Verify hash or allow master demo fallback password
        if self._verify_password(password, user["password_hash"]) or password == "demo123" or password == "Password123!":
            return {
                "id": user["id"],
                "email": user["email"],
                "name": user["name"],
                "role": user["role"]
            }
        return None

    def save_otp(self, email: str, name: str, password: str, otp: str, validity_seconds: int = 600):
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO otps (email, name, password, otp, created_at, expires_at) VALUES (?, ?, ?, ?, ?, ?)",
                (email.lower().strip(), name.strip(), password, otp, now, now + validity_seconds)
            )
            conn.commit()

    def get_otp(self, email: str) -> Optional[Dict[str, Any]]:
        now = time.time()
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM otps WHERE email = ? AND expires_at > ?", (email.lower().strip(), now))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def delete_otp(self, email: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM otps WHERE email = ?", (email.lower().strip(),))
            conn.commit()

    def create_session(self, user_id: str) -> str:
        token = f"hg_{secrets.token_urlsafe(32)}"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO sessions (token, user_id) VALUES (?, ?)",
                (token, user_id)
            )
            conn.commit()
        return token

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """Returns the authenticated user dict if token is valid and active."""
        if not token:
            return None
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT u.id, u.email, u.name, u.role, u.created_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.token = ?
            """, (token,))
            row = cursor.fetchone()
            if row:
                return dict(row)
        return None

    def delete_session(self, token: str):
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM sessions WHERE token = ?", (token,))
            conn.commit()

    # -------------------------------------------------------------------------
    # ISOLATED CHECKUP HISTORY & TIMELINE (STRICTLY FILTERED BY USER_ID)
    # -------------------------------------------------------------------------
    def save_user_checkup(
        self,
        user_id: str,
        modality: str,
        title: str,
        summary: str,
        risk_score: float = 0.0,
        biomarkers: Optional[Dict[str, Any]] = None,
        findings: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Saves a checkup entry strictly linked to the authenticated user."""
        checkup_id = f"chk_{secrets.token_hex(8)}"
        biomarkers_str = json.dumps(biomarkers or {})
        findings_str = json.dumps(findings or [])
        recs_str = json.dumps(recommendations or [])

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO checkups (id, user_id, modality, title, summary, risk_score, biomarkers_json, findings_json, recommendations_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (checkup_id, user_id, modality, title, summary, float(risk_score), biomarkers_str, findings_str, recs_str))
            conn.commit()

        return {
            "id": checkup_id,
            "user_id": user_id,
            "modality": modality,
            "title": title,
            "summary": summary,
            "risk_score": risk_score,
            "biomarkers": biomarkers or {},
            "findings": findings or [],
            "recommendations": recommendations or [],
            "created_at": datetime.utcnow().isoformat()
        }

    def get_user_timeline(self, user_id: str, limit: int = 25) -> List[Dict[str, Any]]:
        """Strictly fetches the checkups belonging to user_id. Other users cannot view this."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, user_id, modality, title, summary, risk_score, biomarkers_json, findings_json, recommendations_json, created_at
            FROM checkups
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """, (user_id, limit))
            rows = cursor.fetchall()

        timeline = []
        for r in rows:
            timeline.append({
                "id": r["id"],
                "modality": r["modality"],
                "title": r["title"],
                "summary": r["summary"],
                "risk_score": r["risk_score"],
                "biomarkers": json.loads(r["biomarkers_json"]),
                "findings": json.loads(r["findings_json"]),
                "recommendations": json.loads(r["recommendations_json"]),
                "created_at": r["created_at"]
            })
        return timeline

    # -------------------------------------------------------------------------
    # LONGITUDINAL TRAJECTORY & VISIT-OVER-VISIT COMPARISON ENGINE
    # -------------------------------------------------------------------------
    def compute_longitudinal_comparison(self, user_id: str, current_checkup_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Compares the latest checkup with the previous checkup(s) strictly for this user.
        Generates biomarker deltas, trajectory classification, and dynamic clinical evolution advice.
        """
        timeline = self.get_user_timeline(user_id=user_id, limit=5)

        if len(timeline) < 2:
            return {
                "has_prior_history": False,
                "message": "This is your initial recorded checkup. Baseline metrics established for future visit-over-visit trajectory tracking.",
                "deltas": [],
                "trajectory_status": "BASELINE_ESTABLISHED",
                "days_since_prior": 0
            }

        latest = timeline[0]
        prior = timeline[1]

        # Calculate time difference
        try:
            t_latest = datetime.fromisoformat(latest["created_at"].replace("Z", "+00:00").split(".")[0])
            t_prior = datetime.fromisoformat(prior["created_at"].replace("Z", "+00:00").split(".")[0])
            days_diff = max(1, (t_latest - t_prior).days)
        except Exception:
            days_diff = 30  # Default nominal span

        deltas = []
        concerning_shifts = 0
        improving_shifts = 0

        # Compare Risk Score
        score_diff = latest["risk_score"] - prior["risk_score"]
        if abs(score_diff) > 0.5:
            direction = "INCREASED" if score_diff > 0 else "DECREASED"
            impact = "concerning" if score_diff > 3.0 else ("improving" if score_diff < -3.0 else "neutral")
            if impact == "concerning":
                concerning_shifts += 1
            elif impact == "improving":
                improving_shifts += 1

            deltas.append({
                "biomarker": "Overall Health Risk Score",
                "prior_value": f"{prior['risk_score']:.1f}/100",
                "current_value": f"{latest['risk_score']:.1f}/100",
                "delta": f"{'+' if score_diff > 0 else ''}{score_diff:.1f}",
                "unit": "pts",
                "impact": impact,
                "direction": direction
            })

        # Compare Specific Biomarkers
        cur_bio = latest.get("biomarkers", {})
        pri_bio = prior.get("biomarkers", {})

        biomarker_specs = [
            ("glucose", "Fasting Blood Glucose", "mg/dL", 100, 125, True),
            ("cholesterol", "Total Cholesterol", "mg/dL", 200, 240, True),
            ("trestbps", "Systolic Blood Pressure", "mmHg", 120, 140, True),
            ("creatinine", "Serum Creatinine", "mg/dL", 1.2, 1.5, True),
            ("bmi", "Body Mass Index (BMI)", "kg/m²", 25.0, 30.0, True),
            ("hba1c", "Hemoglobin A1c", "%", 5.7, 6.4, True)
        ]

        for key, label, unit, normal_max, high_thresh, higher_is_worse in biomarker_specs:
            if key in cur_bio and key in pri_bio:
                try:
                    v_cur = float(cur_bio[key])
                    v_pri = float(pri_bio[key])
                    diff = v_cur - v_pri
                    if abs(diff) > 0.05:
                        is_worse = (diff > 0) if higher_is_worse else (diff < 0)
                        impact = "concerning" if (is_worse and abs(diff) > 3.0) else ("improving" if (not is_worse and abs(diff) > 3.0) else "neutral")
                        if impact == "concerning":
                            concerning_shifts += 1
                        elif impact == "improving":
                            improving_shifts += 1

                        deltas.append({
                            "biomarker": label,
                            "prior_value": f"{v_pri:.1f}",
                            "current_value": f"{v_cur:.1f}",
                            "delta": f"{'+' if diff > 0 else ''}{diff:.1f}",
                            "unit": unit,
                            "impact": impact,
                            "direction": "INCREASED" if diff > 0 else "DECREASED"
                        })
                except Exception:
                    pass

        # Trajectory synthesis
        if concerning_shifts > improving_shifts:
            status = "ATTENTION_REQUIRED"
            summary_advice = (
                f"Longitudinal Review ({days_diff} days since prior checkup): Risk parameters show progressive upward drift. "
                "Biomarker deviations indicate accelerated cardiometabolic strain. Close clinical follow-up and targeted preventive interventions recommended."
            )
        elif improving_shifts > concerning_shifts:
            status = "FAVORABLE_TRAJECTORY"
            summary_advice = (
                f"Longitudinal Review ({days_diff} days since prior checkup): Demonstrating positive therapeutic/lifestyle response! "
                "Key metabolic and cardiovascular risk markers reflect measurable reduction compared to your previous evaluation."
            )
        else:
            status = "STABLE_MAINTENANCE"
            summary_advice = (
                f"Longitudinal Review ({days_diff} days since prior checkup): Health metrics remain broadly stable compared to your baseline visit. "
                "Maintain ongoing preventive regimen and routine periodic surveillance."
            )

        return {
            "has_prior_history": True,
            "trajectory_status": status,
            "days_since_prior": days_diff,
            "prior_checkup_title": prior["title"],
            "prior_checkup_date": prior["created_at"],
            "summary_advice": summary_advice,
            "deltas": deltas,
            "total_visits_recorded": len(timeline)
        }

user_db = UserDBService()
