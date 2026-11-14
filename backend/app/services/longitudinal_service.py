"""
longitudinal_service.py
=======================
Visit-over-visit comparison engine for HealthGuard AI.

Fixes over the legacy compute_longitudinal_comparison:
  (a) Biomarker keys are canonicalized — handles both real extracted keys
      (fasting_plasma_glucose, glycated_hemoglobin_(hba1c), …) and seeded
      demo keys (blood_pressure_systolic, total_cholesterol, ldl, hba1c, …).
  (b) Comparisons are only made between visits of the SAME modality AND
      same normalized condition title OR >= 2 overlapping canonical biomarkers.
  (c) Per-biomarker min_meaningful_change instead of one global ±3.0 threshold.
  (d) Reference-range–first classification: improved/worsened measured as
      change in distance from the ref range, not raw direction alone.
"""

from __future__ import annotations

import re
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# 1. BIOMARKER REGISTRY
# ─────────────────────────────────────────────────────────────────────────────

class BiomarkerSpec:
    """Canonical description of a single biomarker."""
    def __init__(
        self,
        key: str,
        label: str,
        unit: str,
        aliases: List[str],
        ref_low: Optional[float],
        ref_high: Optional[float],
        higher_is_worse: Optional[bool],  # None = unknown direction
        min_meaningful_change: float,       # absolute units
        min_meaningful_pct: Optional[float] = None,  # percent change (use whichever is LARGER)
    ):
        self.key = key
        self.label = label
        self.unit = unit
        self.aliases = aliases
        self.ref_low = ref_low
        self.ref_high = ref_high
        self.higher_is_worse = higher_is_worse
        self.min_meaningful_change = min_meaningful_change
        self.min_meaningful_pct = min_meaningful_pct  # fraction, e.g. 0.10


# Registry — TODO: thresholds should be confirmed against ADA, ACC/AHA, KDIGO guidelines
_REGISTRY: List[BiomarkerSpec] = [
    BiomarkerSpec(
        key="hba1c",
        label="Hemoglobin A1c",
        unit="%",
        aliases=[
            "hba1c", "hba1c_%", "glycated_hemoglobin", "glycated_hemoglobin_(hba1c)",
            "hemoglobin_a1c", "a1c", "glycohemoglobin",
            "hgba1c", "hb_a1c",
        ],
        ref_low=None, ref_high=5.7,  # <5.7% normal, 5.7-6.4% pre-diabetic, ≥6.5% diabetic
        higher_is_worse=True,
        min_meaningful_change=0.5,  # TODO: ADA 2024 Standards — 0.5% clinically meaningful
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="fasting_glucose",
        label="Fasting Blood Glucose",
        unit="mg/dL",
        aliases=[
            "fasting_glucose", "fasting_plasma_glucose", "fasting_blood_glucose",
            "glucose", "blood_glucose_fasting", "fbg",
            "blood_glucose", "plasma_glucose",
        ],
        ref_low=None, ref_high=100.0,  # <100 normal, 100-125 IFG, ≥126 diabetic
        higher_is_worse=True,
        min_meaningful_change=10.0,  # TODO: ADA 2024 — ~10% or 10 mg/dL
        min_meaningful_pct=0.10,
    ),
    BiomarkerSpec(
        key="total_cholesterol",
        label="Total Cholesterol",
        unit="mg/dL",
        aliases=[
            "total_cholesterol", "cholesterol", "serum_cholesterol",
            "total_chol", "tc",
        ],
        ref_low=None, ref_high=200.0,  # <200 desirable, 200-239 borderline, ≥240 high
        higher_is_worse=True,
        min_meaningful_change=20.0,  # TODO: ACC/AHA 2019 — ~10% meaningful
        min_meaningful_pct=0.10,
    ),
    BiomarkerSpec(
        key="ldl",
        label="LDL Cholesterol",
        unit="mg/dL",
        aliases=[
            "ldl", "ldl_cholesterol", "ldl_c", "ldl-c",
            "ldl_cholesterol_(atherogenic)", "low_density_lipoprotein",
            "low-density_lipoprotein",
        ],
        ref_low=None, ref_high=100.0,  # <100 optimal, 100-129 near-optimal, ≥130 borderline high
        higher_is_worse=True,
        min_meaningful_change=15.0,  # TODO: ACC/AHA 2019 — 15 mg/dL or ≥15%
        min_meaningful_pct=0.15,
    ),
    BiomarkerSpec(
        key="hdl",
        label="HDL Cholesterol",
        unit="mg/dL",
        aliases=[
            "hdl", "hdl_cholesterol", "hdl_c", "hdl-c",
            "high_density_lipoprotein", "hdl_cholesterol_(protective)",
        ],
        ref_low=40.0, ref_high=None,  # >40 (M) / >50 (F) desirable, >60 optimal
        higher_is_worse=False,
        min_meaningful_change=5.0,  # TODO: ACC/AHA 2019
        min_meaningful_pct=0.10,
    ),
    BiomarkerSpec(
        key="systolic_bp",
        label="Systolic Blood Pressure",
        unit="mmHg",
        aliases=[
            "systolic_bp", "blood_pressure_systolic", "sbp",
            "blood_pressure_(single_reading)", "systolic_blood_pressure",
            "trestbps", "systolic",
        ],
        ref_low=None, ref_high=120.0,  # <120 normal, 120-129 elevated, 130-139 Stage1, ≥140 Stage2
        higher_is_worse=True,
        min_meaningful_change=10.0,  # TODO: JNC8 / ACC/AHA 2017 — 10 mmHg clinically meaningful
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="diastolic_bp",
        label="Diastolic Blood Pressure",
        unit="mmHg",
        aliases=[
            "diastolic_bp", "blood_pressure_diastolic", "dbp",
            "diastolic_blood_pressure", "diastolic",
        ],
        ref_low=None, ref_high=80.0,
        higher_is_worse=True,
        min_meaningful_change=6.0,  # TODO: ACC/AHA 2017
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="creatinine",
        label="Serum Creatinine",
        unit="mg/dL",
        aliases=[
            "creatinine", "serum_creatinine", "serum_creatinine_(preserved)",
            "s_creatinine", "s.creatinine", "creat",
        ],
        ref_low=0.6, ref_high=1.2,  # M: 0.74-1.35, F: 0.59-1.04 (using common 0.6-1.2)
        higher_is_worse=True,
        min_meaningful_change=0.3,  # TODO: KDIGO 2012 — 0.3 mg/dL or ≥50% increase for AKI
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="bmi",
        label="Body Mass Index",
        unit="kg/m²",
        aliases=[
            "bmi", "body_mass_index", "calculated_bmi",
        ],
        ref_low=18.5, ref_high=25.0,  # 18.5-24.9 normal, 25-29.9 overweight, ≥30 obese
        higher_is_worse=True,
        min_meaningful_change=1.0,  # TODO: Clinical guidelines — 1 BMI unit meaningful
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="hemoglobin",
        label="Hemoglobin",
        unit="g/dL",
        aliases=[
            "hemoglobin", "haemoglobin", "hemoglobin_(hb)", "hb",
            "hgb",
        ],
        ref_low=12.0, ref_high=17.5,  # F: 12-15.5, M: 13.5-17.5 (using F-inclusive range)
        higher_is_worse=False,  # low is bad (anemia)
        min_meaningful_change=1.0,  # TODO: WHO anemia criteria
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="mcv",
        label="Mean Corpuscular Volume",
        unit="fL",
        aliases=[
            "mcv", "mean_corpuscular_volume", "mean_corpuscular_volume_(mcv)",
        ],
        ref_low=80.0, ref_high=100.0,
        higher_is_worse=None,  # both micro and macro have different causes
        min_meaningful_change=5.0,  # TODO: Clinical judgment
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="ferritin",
        label="Serum Ferritin",
        unit="ng/mL",
        aliases=[
            "ferritin", "serum_ferritin", "s_ferritin",
        ],
        ref_low=15.0, ref_high=150.0,
        higher_is_worse=None,  # low = iron deficiency, very high = inflammation/overload
        min_meaningful_change=20.0,  # TODO: WHO iron deficiency — 25% or 20 ng/mL
        min_meaningful_pct=0.25,
    ),
    BiomarkerSpec(
        key="tibc",
        label="Total Iron Binding Capacity",
        unit="mcg/dL",
        aliases=[
            "tibc", "total_iron_binding_capacity", "total_iron_binding_capacity_(tibc)",
        ],
        ref_low=240.0, ref_high=450.0,
        higher_is_worse=None,
        min_meaningful_change=30.0,  # TODO: Clinical judgment
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="triglycerides",
        label="Triglycerides",
        unit="mg/dL",
        aliases=[
            "triglycerides", "trig", "trigs", "triglyceride",
        ],
        ref_low=None, ref_high=150.0,
        higher_is_worse=True,
        min_meaningful_change=20.0,  # TODO: ACC/AHA 2019
        min_meaningful_pct=0.15,
    ),
    BiomarkerSpec(
        key="egfr",
        label="eGFR",
        unit="mL/min/1.73m²",
        aliases=[
            "egfr", "estimated_gfr", "glomerular_filtration_rate",
            "gfr",
        ],
        ref_low=60.0, ref_high=None,  # ≥60 normal, 45-59 mild-moderate decrease
        higher_is_worse=False,
        min_meaningful_change=5.0,  # TODO: KDIGO 2012
        min_meaningful_pct=None,
    ),
    BiomarkerSpec(
        key="risk_score",
        label="Overall Health Risk Score",
        unit="pts",
        aliases=["risk_score", "ai_evidence_score", "ai_score"],
        ref_low=None, ref_high=40.0,
        higher_is_worse=True,
        min_meaningful_change=5.0,
        min_meaningful_pct=None,
    ),
]

# Build lookup maps
_KEY_TO_SPEC: Dict[str, BiomarkerSpec] = {spec.key: spec for spec in _REGISTRY}

_ALIAS_TO_KEY: Dict[str, str] = {}
for spec in _REGISTRY:
    for alias in spec.aliases:
        _ALIAS_TO_KEY[alias.lower()] = spec.key


def _strip_parentheticals(name: str) -> str:
    """Remove trailing parenthetical qualifiers: 'serum creatinine (preserved)' → 'serum creatinine'."""
    return re.sub(r"\s*\([^)]*\)\s*$", "", name).strip()


def canonicalize(raw_name: str) -> Optional[str]:
    """
    Map a raw biomarker name from extracted_parameters or biomarkers_json to
    a canonical key. Returns None if unknown.
    """
    if not raw_name:
        return None
    cleaned = raw_name.lower().strip()
    cleaned = cleaned.replace(" ", "_").replace("-", "_")
    cleaned = re.sub(r"[^a-z0-9_%/()]", "_", cleaned)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")

    # Direct alias match
    if cleaned in _ALIAS_TO_KEY:
        return _ALIAS_TO_KEY[cleaned]

    # Try stripping parentheticals
    stripped = re.sub(r"\s*\([^)]*\)\s*", "", cleaned).strip("_")
    stripped = re.sub(r"_+", "_", stripped)
    if stripped in _ALIAS_TO_KEY:
        return _ALIAS_TO_KEY[stripped]

    # Fuzzy: check if any alias is a prefix/suffix of cleaned
    for alias, key in _ALIAS_TO_KEY.items():
        if cleaned.startswith(alias) or cleaned.endswith(alias):
            return key

    return None


# ─────────────────────────────────────────────────────────────────────────────
# 2. VALUE PARSING (handles "112 mg/dL", ">200", "<0.5", bare numbers)
# ─────────────────────────────────────────────────────────────────────────────

_CENSORED_RE = re.compile(r"^([<>])\s*(\d+(?:\.\d+)?)")
_NUMBER_RE = re.compile(r"(-?\d+(?:\.\d+)?)")


def _parse_value(raw) -> Tuple[Optional[float], Optional[str], bool]:
    """
    Returns (numeric_value, unit_str, is_censored).
    is_censored = True for "<0.5" or ">200" (store value but skip delta).
    """
    if raw is None:
        return None, None, False
    s = str(raw).strip()
    if not s:
        return None, None, False

    # Censored
    m = _CENSORED_RE.match(s)
    if m:
        return float(m.group(2)), None, True

    # Try to extract number
    m2 = _NUMBER_RE.search(s)
    if not m2:
        return None, None, False
    num = float(m2.group(1))

    # Try to extract unit (text after the number)
    unit_str = s[m2.end():].strip() or None

    return num, unit_str, False


def _convert_to_canonical_unit(key: str, value: float, raw_unit: Optional[str]) -> float:
    """
    Convert common alternate units to the canonical unit for a biomarker.
    Returns the converted value (unchanged if unit is already canonical or unknown).
    """
    if raw_unit is None:
        return value
    u = raw_unit.lower().strip()

    if key == "fasting_glucose":
        # mmol/L → mg/dL
        if "mmol" in u:
            return round(value * 18.016, 2)
    elif key in ("total_cholesterol", "ldl", "hdl", "triglycerides"):
        # mmol/L → mg/dL
        if "mmol" in u:
            return round(value * 38.67, 2)
    elif key == "creatinine":
        # µmol/L → mg/dL
        if "umol" in u or "µmol" in u or "micromol" in u:
            return round(value / 88.4, 3)
    elif key == "hba1c":
        # mmol/mol (IFCC) → % (NGSP)
        if "mmol" in u and "mol" in u:
            return round(0.0915 * value + 2.15, 2)

    return value


# ─────────────────────────────────────────────────────────────────────────────
# 3. CLASSIFICATION
# ─────────────────────────────────────────────────────────────────────────────

def _distance_from_range(value: float, ref_low: Optional[float], ref_high: Optional[float]) -> float:
    """
    Returns how far outside the reference range the value is (always >= 0).
    0 means within range.
    """
    if ref_low is not None and value < ref_low:
        return ref_low - value
    if ref_high is not None and value > ref_high:
        return value - ref_high
    return 0.0


def _assess_biomarker(
    spec: BiomarkerSpec,
    prior: float,
    current: float,
) -> Tuple[str, bool]:
    """
    Returns (assessment, meaningful).
    assessment: 'improved' | 'worsened' | 'unchanged' | 'changed_within_range' | 'changed_unclear'
    meaningful: whether the change exceeds min_meaningful_change
    """
    delta = current - prior
    abs_delta = abs(delta)

    # Is the change meaningful?
    meaningful = abs_delta >= spec.min_meaningful_change
    if spec.min_meaningful_pct is not None:
        # Also meaningful if pct change exceeds threshold
        if prior != 0:
            pct = abs_delta / abs(prior)
            meaningful = meaningful or (pct >= spec.min_meaningful_pct)

    if not meaningful:
        return "unchanged", False

    has_range = spec.ref_low is not None or spec.ref_high is not None

    if has_range:
        d_prior = _distance_from_range(prior, spec.ref_low, spec.ref_high)
        d_current = _distance_from_range(current, spec.ref_low, spec.ref_high)

        # Both within range
        if d_prior == 0 and d_current == 0:
            return "changed_within_range", True

        # Moved closer to (or into) range
        if d_current < d_prior:
            return "improved", True

        # Moved further from range
        if d_current > d_prior:
            return "worsened", True

        # Same distance — tie-break by direction
    # No range or tied distance — use higher_is_worse direction
    if spec.higher_is_worse is True:
        return ("worsened" if delta > 0 else "improved"), True
    elif spec.higher_is_worse is False:
        return ("improved" if delta > 0 else "worsened"), True
    else:
        return "changed_unclear", True


# ─────────────────────────────────────────────────────────────────────────────
# 4. OUTPUT MODELS
# ─────────────────────────────────────────────────────────────────────────────

class BiomarkerDelta(BaseModel):
    key: str
    label: str
    unit: str
    prior: float
    current: float
    delta: float
    pct_change: Optional[float]
    assessment: str   # improved | worsened | unchanged | changed_within_range | changed_unclear
    meaningful: bool
    ref_low: Optional[float]
    ref_high: Optional[float]
    trend: Optional[List[float]] = None   # last N values (oldest→newest), populated for 3+ visits
    # Legacy keys for existing DeltaBadge
    biomarker: str = ""
    prior_value: str = ""
    current_value: str = ""
    impact: str = ""   # improving | concerning | neutral (mapped from assessment)
    direction: str = ""

    def model_post_init(self, __context: Any) -> None:
        self.biomarker = self.label
        self.prior_value = f"{self.prior:.1f}"
        self.current_value = f"{self.current:.1f}"
        sign = "+" if self.delta > 0 else ""
        self.delta_str = f"{sign}{self.delta:.1f}"
        self.impact = (
            "improving" if self.assessment == "improved"
            else "concerning" if self.assessment == "worsened"
            else "neutral"
        )
        self.direction = "INCREASED" if self.delta > 0 else "DECREASED"

    def legacy_dict(self) -> dict:
        sign = "+" if self.delta > 0 else ""
        return {
            "biomarker": self.label,
            "prior_value": f"{self.prior:.1f}",
            "current_value": f"{self.current:.1f}",
            "delta": f"{sign}{self.delta:.1f}",
            "unit": self.unit,
            "impact": self.impact,
            "direction": self.direction,
            "assessment": self.assessment,
            "meaningful": self.meaningful,
            "ref_low": self.ref_low,
            "ref_high": self.ref_high,
            "pct_change": round(self.pct_change, 1) if self.pct_change is not None else None,
            "trend": self.trend,
        }


class RiskScoreDelta(BaseModel):
    prior: Optional[float]
    current: Optional[float]
    delta: Optional[float]
    assessment: str  # improved | worsened | unchanged | n/a


class ComparisonCounts(BaseModel):
    improved: int = 0
    worsened: int = 0
    unchanged: int = 0
    unclear: int = 0


class ComparisonResult(BaseModel):
    status: str  # BASELINE | COMPARED | NOT_COMPARABLE
    current_id: Optional[str]
    prior_id: Optional[str]
    days_between: Optional[int]
    modality: Optional[str]
    condition: Optional[str]
    risk_score: RiskScoreDelta
    biomarkers: List[dict]  # list of BiomarkerDelta.legacy_dict()
    counts: ComparisonCounts
    trajectory: str  # FAVORABLE_TRAJECTORY | ATTENTION_REQUIRED | MIXED | STABLE_MAINTENANCE | BASELINE_ESTABLISHED | NOT_COMPARABLE
    not_comparable_reason: Optional[str] = None
    possible_duplicate: bool = False
    stale_comparison: bool = False   # True if > 2 years apart
    # Legacy keys (kept for backward compat)
    has_prior_history: bool = False
    trajectory_status: str = ""
    days_since_prior: int = 0
    prior_checkup_title: Optional[str] = None
    prior_checkup_date: Optional[str] = None
    summary_advice: str = ""
    deltas: List[dict] = Field(default_factory=list)
    total_visits_recorded: int = 0
    message: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# 5. COMPARABLE-PRIOR FINDER
# ─────────────────────────────────────────────────────────────────────────────

def _normalize_title(title: str) -> str:
    """Strip trailing suspected/follow-up qualifiers for title matching."""
    t = re.sub(r"\s*\(suspected\)\s*$", "", title.strip(), flags=re.IGNORECASE)
    t = re.sub(r"\s*\(follow[- ]?up\)\s*$", "", t, flags=re.IGNORECASE)
    return t.strip().lower()


def _canonical_biomarker_keys(biomarkers: dict) -> set:
    keys = set()
    for raw_name in biomarkers:
        ck = canonicalize(raw_name)
        if ck:
            keys.add(ck)
    return keys


def find_comparable_prior(
    current_visit: dict,
    all_visits: List[dict],  # sorted newest→oldest, current_visit excluded
) -> Tuple[Optional[dict], Optional[str]]:
    """
    Returns (prior_visit, None) if comparable prior found,
    or (None, reason_string) if not.
    """
    cur_modality = (current_visit.get("modality") or "").upper()
    cur_title_norm = _normalize_title(current_visit.get("title") or "")
    cur_bio_keys = _canonical_biomarker_keys(current_visit.get("biomarkers") or {})

    for visit in all_visits:
        v_modality = (visit.get("modality") or "").upper()

        # Must match modality
        if v_modality != cur_modality:
            continue

        v_title_norm = _normalize_title(visit.get("title") or "")
        v_bio_keys = _canonical_biomarker_keys(visit.get("biomarkers") or {})
        overlapping = cur_bio_keys & v_bio_keys

        title_matches = (cur_title_norm == v_title_norm)
        bio_matches = len(overlapping) >= 2

        if title_matches or bio_matches:
            return visit, None

    if cur_modality:
        return None, f"No prior visit found with the same modality '{cur_modality}' and comparable biomarkers or condition."
    return None, "No comparable prior visit found."


# ─────────────────────────────────────────────────────────────────────────────
# 6. TREND COMPUTATION (3+ visits)
# ─────────────────────────────────────────────────────────────────────────────

def _compute_trend(
    bio_key: str,
    all_visits: List[dict],  # sorted newest→oldest, up to 5
    current_value: float,
) -> Optional[List[float]]:
    """
    Returns the last-N (up to 5) values for this biomarker across visits,
    oldest first (so trend is visually ascending in time).
    Only returned when >= 3 data points exist.
    """
    values = []
    for visit in reversed(all_visits):  # oldest first
        bio = visit.get("biomarkers") or {}
        for raw_name, raw_val in bio.items():
            if canonicalize(raw_name) == bio_key:
                v, _, censored = _parse_value(raw_val)
                if v is not None and not censored:
                    values.append(v)
                break
    # Append current
    values.append(current_value)
    if len(values) >= 3:
        return values
    return None


# ─────────────────────────────────────────────────────────────────────────────
# 7. MAIN COMPARISON FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def compute_comparison(
    user_id: str,
    all_visits: List[dict],  # sorted newest→oldest (from get_user_timeline)
    current_checkup_id: Optional[str] = None,
) -> ComparisonResult:
    """
    Compute a structured visit-over-visit comparison for the most recent visit
    (or the visit matching current_checkup_id).
    """
    if not all_visits:
        return _baseline_result(None, 0)

    # Find current visit
    if current_checkup_id:
        current = next((v for v in all_visits if v["id"] == current_checkup_id), None)
        if current is None:
            current = all_visits[0]
    else:
        current = all_visits[0]

    if len(all_visits) < 2:
        return _baseline_result(current, len(all_visits))

    prior_candidates = [v for v in all_visits if v["id"] != current["id"]]
    prior, not_comparable_reason = find_comparable_prior(current, prior_candidates)

    if prior is None:
        return ComparisonResult(
            status="NOT_COMPARABLE",
            current_id=current.get("id"),
            prior_id=None,
            days_between=None,
            modality=current.get("modality"),
            condition=current.get("title"),
            risk_score=RiskScoreDelta(prior=None, current=current.get("risk_score"), delta=None, assessment="n/a"),
            biomarkers=[],
            counts=ComparisonCounts(),
            trajectory="NOT_COMPARABLE",
            not_comparable_reason=not_comparable_reason,
            has_prior_history=False,
            trajectory_status="NOT_COMPARABLE",
            days_since_prior=0,
            summary_advice=not_comparable_reason or "No comparable prior visit found.",
            deltas=[],
            total_visits_recorded=len(all_visits),
            message=not_comparable_reason,
        )

    # Time difference
    try:
        t_cur = datetime.fromisoformat(current["created_at"].replace("Z", "+00:00").split(".")[0])
        t_pri = datetime.fromisoformat(prior["created_at"].replace("Z", "+00:00").split(".")[0])
        days_between = abs((t_cur - t_pri).days)
    except Exception:
        days_between = 30

    # Duplicate detection
    possible_duplicate = days_between < 1
    stale_comparison = days_between > 730  # > 2 years

    # Same values check
    if not possible_duplicate and current.get("biomarkers") == prior.get("biomarkers"):
        possible_duplicate = True

    # Risk score comparison (only when modality+title match)
    cur_title_norm = _normalize_title(current.get("title") or "")
    pri_title_norm = _normalize_title(prior.get("title") or "")
    titles_match = (cur_title_norm == pri_title_norm)

    cur_risk = current.get("risk_score")
    pri_risk = prior.get("risk_score")
    if titles_match and cur_risk is not None and pri_risk is not None:
        risk_delta = float(cur_risk) - float(pri_risk)
        risk_spec = _KEY_TO_SPEC.get("risk_score")
        risk_assessment, _ = _assess_biomarker(risk_spec, float(pri_risk), float(cur_risk))
        risk_score_delta = RiskScoreDelta(
            prior=float(pri_risk),
            current=float(cur_risk),
            delta=round(risk_delta, 1),
            assessment=risk_assessment,
        )
    else:
        risk_score_delta = RiskScoreDelta(prior=pri_risk, current=cur_risk, delta=None, assessment="n/a")

    # Biomarker comparison
    cur_bio = current.get("biomarkers") or {}
    pri_bio = prior.get("biomarkers") or {}

    # Build canonical → (raw_key, raw_value) maps
    def _canonical_map(bio: dict) -> Dict[str, Tuple[str, Any]]:
        m = {}
        for raw_name, raw_val in bio.items():
            ck = canonicalize(raw_name)
            if ck and ck not in m:
                m[ck] = (raw_name, raw_val)
        return m

    cur_cmap = _canonical_map(cur_bio)
    pri_cmap = _canonical_map(pri_bio)

    # Visits for trend (oldest first, excluding current)
    trend_visits = [v for v in all_visits if v["id"] != current["id"]]

    biomarker_rows: List[dict] = []
    improved = worsened = unchanged = unclear = 0

    for bio_key in set(cur_cmap) & set(pri_cmap):
        spec = _KEY_TO_SPEC.get(bio_key)
        if spec is None:
            continue

        _, cur_raw_val = cur_cmap[bio_key]
        _, pri_raw_val = pri_cmap[bio_key]

        cur_num, cur_unit, cur_censored = _parse_value(cur_raw_val)
        pri_num, pri_unit, pri_censored = _parse_value(pri_raw_val)

        if cur_num is None or pri_num is None:
            continue

        # Unit conversion
        unit_to_use = cur_unit or pri_unit or spec.unit
        cur_num = _convert_to_canonical_unit(bio_key, cur_num, cur_unit)
        pri_num = _convert_to_canonical_unit(bio_key, pri_num, pri_unit)

        # Skip if either censored
        if cur_censored or pri_censored:
            # Still include in output but mark as changed_unclear
            row = {
                "key": bio_key,
                "label": spec.label,
                "unit": spec.unit,
                "prior": pri_num,
                "current": cur_num,
                "delta": 0.0,
                "pct_change": None,
                "assessment": "censored_skipped",
                "meaningful": False,
                "ref_low": spec.ref_low,
                "ref_high": spec.ref_high,
                "trend": None,
                # Legacy
                "biomarker": spec.label,
                "prior_value": f"{'<' if pri_censored else ''}{pri_num:.1f}",
                "current_value": f"{'<' if cur_censored else ''}{cur_num:.1f}",
                "delta": "—",
                "unit": spec.unit,
                "impact": "neutral",
                "direction": "—",
            }
            biomarker_rows.append(row)
            continue

        delta = cur_num - pri_num
        pct_change = (delta / abs(pri_num) * 100) if pri_num != 0 else None
        assessment, meaningful = _assess_biomarker(spec, pri_num, cur_num)

        if meaningful:
            if assessment == "improved":
                improved += 1
            elif assessment == "worsened":
                worsened += 1
            elif assessment == "changed_unclear":
                unclear += 1
            else:
                unchanged += 1
        else:
            unchanged += 1

        trend = _compute_trend(bio_key, trend_visits[:5], cur_num)

        sign = "+" if delta > 0 else ""
        impact = (
            "improving" if assessment == "improved"
            else "concerning" if assessment == "worsened"
            else "neutral"
        )

        row = {
            "key": bio_key,
            "label": spec.label,
            "unit": spec.unit,
            "prior": round(pri_num, 2),
            "current": round(cur_num, 2),
            "delta": round(delta, 2),
            "pct_change": round(pct_change, 1) if pct_change is not None else None,
            "assessment": assessment,
            "meaningful": meaningful,
            "ref_low": spec.ref_low,
            "ref_high": spec.ref_high,
            "trend": trend,
            # Legacy DeltaBadge keys
            "biomarker": spec.label,
            "prior_value": f"{pri_num:.1f}",
            "current_value": f"{cur_num:.1f}",
            "delta_str": f"{sign}{delta:.1f}",
            "unit_legacy": spec.unit,
            "impact": impact,
            "direction": "INCREASED" if delta > 0 else "DECREASED",
        }
        biomarker_rows.append(row)

    # Trajectory synthesis
    if worsened > 0 and improved == 0:
        trajectory = "ATTENTION_REQUIRED"
    elif improved > 0 and worsened == 0:
        trajectory = "FAVORABLE_TRAJECTORY"
    elif improved > 0 and worsened > 0:
        trajectory = "MIXED"
    else:
        trajectory = "STABLE_MAINTENANCE"

    counts = ComparisonCounts(
        improved=improved,
        worsened=worsened,
        unchanged=unchanged,
        unclear=unclear,
    )

    # Legacy summary_advice (plain text, no LLM)
    days_str = f"{days_between} days"
    if trajectory == "ATTENTION_REQUIRED":
        summary_advice = (
            f"Longitudinal Review ({days_str} since prior checkup): "
            f"{worsened} biomarker(s) show worsening trend. Close clinical follow-up recommended."
        )
    elif trajectory == "FAVORABLE_TRAJECTORY":
        summary_advice = (
            f"Longitudinal Review ({days_str} since prior checkup): "
            f"{improved} biomarker(s) show meaningful improvement. Continue current regimen."
        )
    elif trajectory == "MIXED":
        summary_advice = (
            f"Longitudinal Review ({days_str} since prior checkup): "
            f"Mixed results — {improved} improved, {worsened} worsened. Clinical review recommended."
        )
    else:
        summary_advice = (
            f"Longitudinal Review ({days_str} since prior checkup): "
            "Health metrics remain broadly stable. Maintain preventive regimen."
        )

    # Build legacy deltas list (shape DeltaBadge expects)
    legacy_deltas = []
    for row in biomarker_rows:
        legacy_deltas.append({
            "biomarker": row["biomarker"],
            "prior_value": row["prior_value"],
            "current_value": row["current_value"],
            "delta": row.get("delta_str", str(row.get("delta", ""))),
            "unit": row["unit"],
            "impact": row["impact"],
            "direction": row["direction"],
        })

    return ComparisonResult(
        status="COMPARED",
        current_id=current.get("id"),
        prior_id=prior.get("id"),
        days_between=days_between,
        modality=current.get("modality"),
        condition=current.get("title"),
        risk_score=risk_score_delta,
        biomarkers=biomarker_rows,
        counts=counts,
        trajectory=trajectory,
        possible_duplicate=possible_duplicate,
        stale_comparison=stale_comparison,
        # Legacy
        has_prior_history=True,
        trajectory_status=trajectory,
        days_since_prior=days_between,
        prior_checkup_title=prior.get("title"),
        prior_checkup_date=prior.get("created_at"),
        summary_advice=summary_advice,
        deltas=legacy_deltas,
        total_visits_recorded=len(all_visits),
    )


def _baseline_result(current: Optional[dict], total: int) -> ComparisonResult:
    return ComparisonResult(
        status="BASELINE",
        current_id=current.get("id") if current else None,
        prior_id=None,
        days_between=None,
        modality=current.get("modality") if current else None,
        condition=current.get("title") if current else None,
        risk_score=RiskScoreDelta(prior=None, current=None, delta=None, assessment="n/a"),
        biomarkers=[],
        counts=ComparisonCounts(),
        trajectory="BASELINE_ESTABLISHED",
        has_prior_history=False,
        trajectory_status="BASELINE_ESTABLISHED",
        days_since_prior=0,
        summary_advice="Baseline metrics established for future visit-over-visit trajectory tracking.",
        deltas=[],
        total_visits_recorded=total,
        message="This is your initial recorded checkup. Baseline metrics established for future visit-over-visit trajectory tracking.",
    )

