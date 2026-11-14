import os
import json
import uuid
import time
import sqlite3
import hashlib
import secrets
import threading
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

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

            # 4. Comparisons Table (visit-over-visit comparison + LLM narration)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS comparisons (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                current_checkup_id TEXT NOT NULL,
                prior_checkup_id TEXT,
                result_json TEXT NOT NULL,
                narrative_json TEXT,
                narrative_source TEXT DEFAULT 'template',
                llm_model TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(current_checkup_id),
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_comparisons_user ON comparisons(user_id, created_at DESC);")

            # 5. OTPs Table
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

            # 5. User Clinician Feedback & Audit Log Table (Isolated by user_id)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                case_id TEXT,
                patient_name TEXT,
                condition_name TEXT,
                original_score REAL,
                action TEXT,
                override_text TEXT,
                override_reason TEXT,
                clinician_id TEXT,
                timestamp TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            );
            """)
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id, created_at DESC);")

            conn.commit()

        # Guarded ALTER TABLE: add biomarkers_meta_json column if missing (nullable, harmless)
        try:
            with self._get_connection() as conn:
                conn.execute("ALTER TABLE checkups ADD COLUMN biomarkers_meta_json TEXT")
                conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists — harmless

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
        # No demo accounts are seeded; accounts start completely blank
        pass

    def _seed_sample_checkups(self, user_id: str):
        """Seeds two longitudinal checkup records (baseline + follow-up) so history tab shows trajectory analysis."""
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        t1 = (now - timedelta(days=42)).isoformat()
        t2 = (now - timedelta(days=7)).isoformat()

        # Visit 1: Baseline Visit
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            INSERT INTO checkups (id, user_id, modality, title, summary, risk_score, biomarkers_json, findings_json, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"chk_seed_1_{secrets.token_hex(4)}",
                user_id,
                "LAB_REPORT",
                "Baseline Comprehensive Health Screening",
                "Stage 1 systolic elevation and borderline dyslipidemia noted on initial clinical presentation.",
                68.0,
                json.dumps({
                    "blood_pressure_systolic": 146.0,
                    "blood_pressure_diastolic": 92.0,
                    "total_cholesterol": 235.0,
                    "ldl": 154.0,
                    "fasting_glucose": 112.0,
                    "hba1c": 6.1,
                    "bmi": 29.8
                }),
                json.dumps([
                    "Blood pressure elevated (146/92 mmHg) in Stage 1 hypertensive range",
                    "Atherogenic lipid profile with Total Cholesterol 235 mg/dL, LDL 154 mg/dL",
                    "Impaired fasting glucose (112 mg/dL) indicating pre-diabetes state"
                ]),
                json.dumps([
                    "Initiate DASH low-sodium nutritional protocol (<1500mg/day)",
                    "30 minutes moderate aerobic exercise 5x weekly",
                    "Repeat metabolic & lipid panel in 6 weeks"
                ]),
                t1
            ))

            # Visit 2: Follow-up Visit (Improved trajectory)
            cursor.execute("""
            INSERT INTO checkups (id, user_id, modality, title, summary, risk_score, biomarkers_json, findings_json, recommendations_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                f"chk_seed_2_{secrets.token_hex(4)}",
                user_id,
                "LAB_REPORT",
                "6-Week Follow-Up Cardiometabolic Evaluation",
                "Clinically meaningful reduction in arterial blood pressure and fasting glucose following lifestyle intervention.",
                28.0,
                json.dumps({
                    "blood_pressure_systolic": 126.0,
                    "blood_pressure_diastolic": 80.0,
                    "total_cholesterol": 198.0,
                    "ldl": 122.0,
                    "fasting_glucose": 96.0,
                    "hba1c": 5.6,
                    "bmi": 28.5
                }),
                json.dumps([
                    "Normotensive blood pressure stabilization (126/80 mmHg, -20 mmHg systolic drop)",
                    "Total cholesterol reduced to optimal range (<200 mg/dL)",
                    "Glycemic normalization: fasting glucose 96 mg/dL, HbA1c 5.6%"
                ]),
                json.dumps([
                    "Maintain current dietary modifications and weekly exercise regimen",
                    "Continue home BP monitoring 2x weekly",
                    "Routine annual clinical review in 12 months"
                ]),
                t2
            ))
            conn.commit()

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
        
        if self._verify_password(password, user["password_hash"]):
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

    def delete_user_checkup(self, user_id: str, checkup_id: str, is_clinician: bool = False) -> bool:
        """Deletes a specific checkup strictly belonging to user_id (or any checkup if clinician), and its comparison."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Delete associated comparisons first (current or prior)
            try:
                if is_clinician:
                    cursor.execute(
                        "DELETE FROM comparisons WHERE current_checkup_id = ? OR prior_checkup_id = ?",
                        (checkup_id, checkup_id)
                    )
                else:
                    cursor.execute(
                        "DELETE FROM comparisons WHERE user_id = ? AND (current_checkup_id = ? OR prior_checkup_id = ?)",
                        (user_id, checkup_id, checkup_id)
                    )
            except sqlite3.OperationalError:
                pass  # comparisons table may not exist in old DBs

            if is_clinician:
                cursor.execute("DELETE FROM checkups WHERE id = ?", (checkup_id,))
            else:
                cursor.execute("DELETE FROM checkups WHERE id = ? AND user_id = ?", (checkup_id, user_id))
            conn.commit()
            return cursor.rowcount > 0

    def clear_user_checkups(self, user_id: str) -> bool:
        """Clears all checkup history strictly belonging to user_id, and all comparisons."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("DELETE FROM comparisons WHERE user_id = ?", (user_id,))
            except sqlite3.OperationalError:
                pass
            cursor.execute("DELETE FROM checkups WHERE user_id = ?", (user_id,))
            conn.commit()
            return cursor.rowcount > 0

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
    # COMPARISON STORAGE
    # -------------------------------------------------------------------------
    def save_comparison(
        self,
        user_id: str,
        current_checkup_id: str,
        prior_checkup_id: Optional[str],
        result_dict: Dict[str, Any],
        narrative_dict: Optional[Dict[str, Any]] = None,
        narrative_source: str = "template",
        llm_model: Optional[str] = None,
    ) -> str:
        """Upsert a comparison record (UNIQUE on current_checkup_id)."""
        comp_id = f"cmp_{secrets.token_hex(8)}"
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO comparisons
                    (id, user_id, current_checkup_id, prior_checkup_id, result_json, narrative_json, narrative_source, llm_model)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(current_checkup_id) DO UPDATE SET
                    result_json=excluded.result_json,
                    narrative_json=excluded.narrative_json,
                    narrative_source=excluded.narrative_source,
                    llm_model=excluded.llm_model,
                    created_at=CURRENT_TIMESTAMP
                """, (
                    comp_id, user_id, current_checkup_id, prior_checkup_id,
                    json.dumps(result_dict),
                    json.dumps(narrative_dict) if narrative_dict else None,
                    narrative_source,
                    llm_model,
                ))
                conn.commit()
        except sqlite3.OperationalError as e:
            logger.warning("save_comparison failed (table may not exist): %s", e)
        return comp_id

    def get_comparison_for_checkup(self, checkup_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored comparison for a specific checkup."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT result_json, narrative_json, narrative_source, llm_model FROM comparisons WHERE current_checkup_id = ?",
                    (checkup_id,)
                )
                row = cursor.fetchone()
                if row:
                    result = json.loads(row[0]) if row[0] else {}
                    narrative = json.loads(row[1]) if row[1] else None
                    return {
                        "comparison": result,
                        "narrative": narrative,
                        "narrative_source": row[2],
                        "llm_model": row[3],
                    }
        except sqlite3.OperationalError:
            pass
        return None

    # -------------------------------------------------------------------------
    # LONGITUDINAL TRAJECTORY & VISIT-OVER-VISIT COMPARISON ENGINE
    # -------------------------------------------------------------------------
    def compute_longitudinal_comparison(self, user_id: str, current_checkup_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Returns a ComparisonResult dict for the latest (or specified) checkup.
        Uses the new longitudinal_service engine for correctness.
        Falls back to stored comparison if available.
        """
        # Try to get stored comparison for the latest checkup first
        timeline = self.get_user_timeline(user_id=user_id, limit=25)
        if not timeline:
            from backend.app.services.longitudinal_service import compute_comparison, _baseline_result
            return _baseline_result(None, 0).model_dump()

        current = timeline[0] if not current_checkup_id else next(
            (v for v in timeline if v["id"] == current_checkup_id), timeline[0]
        )

        stored = self.get_comparison_for_checkup(current["id"])
        if stored and stored.get("comparison"):
            result = stored["comparison"]
            result["_narrative"] = stored.get("narrative")
            result["_narrative_source"] = stored.get("narrative_source", "template")
            result["_llm_model"] = stored.get("llm_model")
            result["total_visits_recorded"] = len(timeline)
            return result

        # Compute on-the-fly using new engine
        from backend.app.services.longitudinal_service import compute_comparison
        result = compute_comparison(user_id, timeline, current_checkup_id)
        return result.model_dump()

    # -------------------------------------------------------------------------
    # CLINICIAN FEEDBACK & AUDIT LOG METHODS
    # -------------------------------------------------------------------------
    def save_user_feedback(self, user_id: str, entry: Dict[str, Any]) -> Dict[str, Any]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            feedback_id = entry.get("id") or f"fb-{secrets.token_hex(4)}"
            timestamp = entry.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            cursor.execute("""
            INSERT OR REPLACE INTO feedback (
                id, user_id, case_id, patient_name, condition_name,
                original_score, action, override_text, override_reason,
                clinician_id, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                feedback_id,
                user_id,
                entry.get("case_id"),
                entry.get("patient_name"),
                entry.get("condition_name"),
                entry.get("original_score", 0.0),
                entry.get("action"),
                entry.get("override_text"),
                entry.get("override_reason"),
                entry.get("clinician_id"),
                timestamp
            ))
            conn.commit()
            entry["id"] = feedback_id
            entry["timestamp"] = timestamp
            return entry

    def get_user_feedback(self, user_id: str) -> List[Dict[str, Any]]:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            SELECT id, case_id, patient_name, condition_name, original_score,
                   action, override_text, override_reason, clinician_id, timestamp
            FROM feedback
            WHERE user_id = ?
            ORDER BY created_at DESC
            """, (user_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def clear_user_feedback(self, user_id: str) -> bool:
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM feedback WHERE user_id = ?", (user_id,))
            conn.commit()
            return True

user_db = UserDBService()
