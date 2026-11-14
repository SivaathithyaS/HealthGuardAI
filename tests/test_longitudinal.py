"""
tests/test_longitudinal.py
==========================
Tests for the longitudinal comparison engine.
No LLM calls. No secrets required.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.longitudinal_service import (
    canonicalize,
    compute_comparison,
    find_comparable_prior,
    _assess_biomarker,
    _convert_to_canonical_unit,
    _KEY_TO_SPEC,
    _baseline_result,
)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_visit(
    id_: str,
    modality: str,
    title: str,
    biomarkers: dict,
    risk_score: float = 50.0,
    days_ago: int = 0,
):
    dt = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    return {
        "id": id_,
        "modality": modality,
        "title": title,
        "summary": "test",
        "risk_score": risk_score,
        "biomarkers": biomarkers,
        "findings": [],
        "recommendations": [],
        "created_at": dt,
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. CANONICALIZATION — every real key from Part 1 spec
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize("raw,expected_key", [
    # Real extracted keys
    ("fasting_plasma_glucose", "fasting_glucose"),
    ("glycated_hemoglobin_(hba1c)", "hba1c"),
    ("serum_creatinine_(preserved)", "creatinine"),
    ("calculated_bmi", "bmi"),
    ("blood_pressure_(single_reading)", "systolic_bp"),
    ("ldl_cholesterol_(atherogenic)", "ldl"),
    ("hemoglobin_(hb)", "hemoglobin"),
    ("mean_corpuscular_volume_(mcv)", "mcv"),
    ("serum_ferritin", "ferritin"),
    ("total_iron_binding_capacity_(tibc)", "tibc"),
    # Seeded demo keys
    ("blood_pressure_systolic", "systolic_bp"),
    ("total_cholesterol", "total_cholesterol"),
    ("ldl", "ldl"),
    ("fasting_glucose", "fasting_glucose"),
    ("hba1c", "hba1c"),
    ("bmi", "bmi"),
    # Legacy keys from old engine
    ("glucose", "fasting_glucose"),
    ("cholesterol", "total_cholesterol"),
    ("trestbps", "systolic_bp"),
    ("creatinine", "creatinine"),
    # With underscores
    ("hemoglobin", "hemoglobin"),
    ("mcv", "mcv"),
    ("ferritin", "ferritin"),
    ("tibc", "tibc"),
    # Uppercase input
    ("HBA1C", "hba1c"),
    ("LDL", "ldl"),
])
def test_canonicalize(raw, expected_key):
    assert canonicalize(raw) == expected_key, f"canonicalize({raw!r}) should be {expected_key!r}"


def test_canonicalize_unknown():
    assert canonicalize("platelet_volume_distribution") is None
    assert canonicalize("") is None
    assert canonicalize(None) is None


# ─────────────────────────────────────────────────────────────────────────────
# 2. UNIT CONVERSIONS
# ─────────────────────────────────────────────────────────────────────────────

def test_glucose_mmol_to_mgdl():
    # 7.0 mmol/L * 18.016 = 126.112
    result = _convert_to_canonical_unit("fasting_glucose", 7.0, "mmol/L")
    assert abs(result - 126.11) < 0.1

def test_cholesterol_mmol_to_mgdl():
    # 5.0 mmol/L * 38.67 = 193.35
    result = _convert_to_canonical_unit("total_cholesterol", 5.0, "mmol/L")
    assert abs(result - 193.35) < 0.1

def test_creatinine_umol_to_mgdl():
    # 88.4 umol/L / 88.4 = 1.0 mg/dL
    result = _convert_to_canonical_unit("creatinine", 88.4, "umol/L")
    assert abs(result - 1.0) < 0.01

def test_hba1c_mmol_mol_to_pct():
    # 50 mmol/mol -> 0.0915*50 + 2.15 = 6.725%
    result = _convert_to_canonical_unit("hba1c", 50, "mmol/mol")
    assert abs(result - 6.725) < 0.05

def test_no_conversion_needed():
    # Already in mg/dL — should be unchanged
    result = _convert_to_canonical_unit("fasting_glucose", 100.0, "mg/dL")
    assert result == 100.0


# ─────────────────────────────────────────────────────────────────────────────
# 3. BIOMARKER ASSESSMENT
# ─────────────────────────────────────────────────────────────────────────────

def test_hba1c_improved():
    spec = _KEY_TO_SPEC["hba1c"]
    # 8.2 -> 6.9: moved from diabetic range (>6.5) toward ref; meaningful (delta=1.3 > 0.5)
    assessment, meaningful = _assess_biomarker(spec, 8.2, 6.9)
    assert assessment == "improved", f"Expected improved, got {assessment}"
    assert meaningful is True

def test_creatinine_worsened():
    spec = _KEY_TO_SPEC["creatinine"]
    # 1.2 -> 2.4: moved from ref high into high territory; delta=1.2 > 0.3
    assessment, meaningful = _assess_biomarker(spec, 1.2, 2.4)
    assert assessment == "worsened", f"Expected worsened, got {assessment}"
    assert meaningful is True

def test_glucose_unchanged():
    spec = _KEY_TO_SPEC["fasting_glucose"]
    # 90 -> 95: both within normal (<100); delta=5 < 10 (min_meaningful_change)
    assessment, meaningful = _assess_biomarker(spec, 90, 95)
    assert assessment == "unchanged", f"Expected unchanged, got {assessment}"
    assert meaningful is False

def test_ldl_improved():
    spec = _KEY_TO_SPEC["ldl"]
    # 160 -> 130: moved from high toward ref (<100); delta=30 > 15
    assessment, meaningful = _assess_biomarker(spec, 160, 130)
    assert assessment == "improved", f"Expected improved, got {assessment}"
    assert meaningful is True

def test_bp_worsened():
    spec = _KEY_TO_SPEC["systolic_bp"]
    # 130 -> 150: moved further from ref (<120)
    assessment, meaningful = _assess_biomarker(spec, 130, 150)
    assert assessment == "worsened", f"Expected worsened, got {assessment}"
    assert meaningful is True


# ─────────────────────────────────────────────────────────────────────────────
# 4. MIXED CASE
# ─────────────────────────────────────────────────────────────────────────────

def test_mixed_trajectory():
    v1 = _make_visit("v1", "LAB_REPORT", "Cardio Panel", {
        "hba1c": 8.2,
        "systolic_bp": 130.0,
        "total_cholesterol": 240.0,
    }, days_ago=42)
    v2 = _make_visit("v2", "LAB_REPORT", "Cardio Panel", {
        "hba1c": 6.9,        # improved
        "systolic_bp": 150.0, # worsened
        "total_cholesterol": 240.0,  # unchanged (no meaningful change)
    }, days_ago=0)

    result = compute_comparison("user1", [v2, v1])
    assert result.status == "COMPARED"
    assert result.trajectory == "MIXED"
    assert result.counts.improved >= 1
    assert result.counts.worsened >= 1


# ─────────────────────────────────────────────────────────────────────────────
# 5. CENSORED VALUES SKIPPED FOR DELTA
# ─────────────────────────────────────────────────────────────────────────────

def test_censored_values_skipped():
    v1 = _make_visit("v1", "LAB_REPORT", "Iron Panel", {"serum_ferritin": "<5"}, days_ago=30)
    v2 = _make_visit("v2", "LAB_REPORT", "Iron Panel", {"serum_ferritin": ">200"}, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    # Should be COMPARED but ferritin delta should be skipped
    ferritin_rows = [b for b in result.biomarkers if b.get("key") == "ferritin"]
    if ferritin_rows:
        assert ferritin_rows[0]["assessment"] == "censored_skipped"


# ─────────────────────────────────────────────────────────────────────────────
# 6. DIFFERENT MODALITY → NOT_COMPARABLE
# ─────────────────────────────────────────────────────────────────────────────

def test_different_modality_not_comparable():
    v1 = _make_visit("v1", "LAB_REPORT", "Cardio", {"hba1c": 7.0, "ldl": 150.0}, days_ago=30)
    v2 = _make_visit("v2", "ECG_REPORT", "ECG Study", {"hba1c": 6.5, "ldl": 130.0}, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    assert result.status == "NOT_COMPARABLE"
    assert result.trajectory == "NOT_COMPARABLE"


# ─────────────────────────────────────────────────────────────────────────────
# 7. FIRST VISIT → BASELINE
# ─────────────────────────────────────────────────────────────────────────────

def test_first_visit_baseline():
    v1 = _make_visit("v1", "LAB_REPORT", "Screening", {"hba1c": 6.5})
    result = compute_comparison("user1", [v1])
    assert result.status == "BASELINE"
    assert result.trajectory == "BASELINE_ESTABLISHED"
    assert result.has_prior_history is False


def test_no_visits_baseline():
    result = compute_comparison("user1", [])
    assert result.status == "BASELINE"


# ─────────────────────────────────────────────────────────────────────────────
# 8. DUPLICATE DETECTION
# ─────────────────────────────────────────────────────────────────────────────

def test_duplicate_detection_same_values():
    bio = {"hba1c": 7.0, "ldl": 150.0, "systolic_bp": 130.0}
    v1 = _make_visit("v1", "LAB_REPORT", "Cardio", bio, days_ago=30)
    v2 = _make_visit("v2", "LAB_REPORT", "Cardio", bio, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    # Same biomarker values → possible_duplicate
    assert result.possible_duplicate is True

def test_duplicate_detection_same_day():
    from datetime import datetime, timedelta
    now = datetime.utcnow().isoformat()
    v1 = {**_make_visit("v1", "LAB_REPORT", "Panel", {"hba1c": 7.0}), "created_at": now}
    v2 = {**_make_visit("v2", "LAB_REPORT", "Panel", {"hba1c": 6.9}), "created_at": now}
    result = compute_comparison("user1", [v2, v1])
    assert result.possible_duplicate is True


# ─────────────────────────────────────────────────────────────────────────────
# 9. TREND WITH 3+ VISITS
# ─────────────────────────────────────────────────────────────────────────────

def test_trend_three_plus_visits():
    v1 = _make_visit("v1", "LAB_REPORT", "Cardio", {"hba1c": 9.0}, days_ago=84)
    v2 = _make_visit("v2", "LAB_REPORT", "Cardio", {"hba1c": 8.0}, days_ago=42)
    v3 = _make_visit("v3", "LAB_REPORT", "Cardio", {"hba1c": 7.0}, days_ago=0)

    result = compute_comparison("user1", [v3, v2, v1])
    assert result.status == "COMPARED"

    hba1c_rows = [b for b in result.biomarkers if b.get("key") == "hba1c"]
    assert hba1c_rows, "Expected hba1c in biomarkers"
    # Trend should have >= 3 values
    trend = hba1c_rows[0].get("trend")
    assert trend is not None, "Expected trend data for 3+ visits"
    assert len(trend) >= 3


# ─────────────────────────────────────────────────────────────────────────────
# 10. FAVORABLE / ATTENTION_REQUIRED TRAJECTORIES
# ─────────────────────────────────────────────────────────────────────────────

def test_favorable_trajectory():
    v1 = _make_visit("v1", "LAB_REPORT", "Panel", {
        "hba1c": 8.2, "systolic_bp": 150.0, "ldl": 170.0
    }, days_ago=42)
    v2 = _make_visit("v2", "LAB_REPORT", "Panel", {
        "hba1c": 6.9, "systolic_bp": 125.0, "ldl": 110.0
    }, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    assert result.trajectory == "FAVORABLE_TRAJECTORY"
    assert result.counts.improved >= 2
    assert result.counts.worsened == 0

def test_attention_required_trajectory():
    v1 = _make_visit("v1", "LAB_REPORT", "Panel", {
        "hba1c": 6.5, "systolic_bp": 125.0, "ldl": 110.0
    }, days_ago=42)
    v2 = _make_visit("v2", "LAB_REPORT", "Panel", {
        "hba1c": 8.5, "systolic_bp": 155.0, "ldl": 170.0
    }, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    assert result.trajectory == "ATTENTION_REQUIRED"
    assert result.counts.worsened >= 2
    assert result.counts.improved == 0


# ─────────────────────────────────────────────────────────────────────────────
# 11. LEGACY KEYS PRESERVED (backward compat)
# ─────────────────────────────────────────────────────────────────────────────

def test_legacy_keys_present():
    v1 = _make_visit("v1", "LAB_REPORT", "Panel", {"hba1c": 8.0}, days_ago=30)
    v2 = _make_visit("v2", "LAB_REPORT", "Panel", {"hba1c": 6.8}, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    d = result.model_dump()
    assert "has_prior_history" in d
    assert "trajectory_status" in d
    assert "days_since_prior" in d
    assert "summary_advice" in d
    assert "deltas" in d
    assert "total_visits_recorded" in d

def test_delta_badges_shape():
    """Each delta dict must have the keys DeltaBadge expects."""
    v1 = _make_visit("v1", "LAB_REPORT", "Panel", {"hba1c": 8.0, "systolic_bp": 150.0}, days_ago=30)
    v2 = _make_visit("v2", "LAB_REPORT", "Panel", {"hba1c": 6.8, "systolic_bp": 155.0}, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    for d in result.deltas:
        assert "biomarker" in d
        assert "prior_value" in d
        assert "current_value" in d
        assert "delta" in d
        assert "unit" in d
        assert "impact" in d
        assert "direction" in d


# ─────────────────────────────────────────────────────────────────────────────
# 12. SEEDED DEMO DATA PRODUCES COMPARED RESULT
# ─────────────────────────────────────────────────────────────────────────────

def test_seeded_demo_data_produces_compared():
    """Simulate the two seeded checkups and verify COMPARED with several deltas."""
    v1 = _make_visit("seed1", "LAB_REPORT", "Baseline Comprehensive Health Screening", {
        "blood_pressure_systolic": 146.0,
        "blood_pressure_diastolic": 92.0,
        "total_cholesterol": 235.0,
        "ldl": 154.0,
        "fasting_glucose": 112.0,
        "hba1c": 6.1,
        "bmi": 29.8,
    }, risk_score=68.0, days_ago=42)

    v2 = _make_visit("seed2", "LAB_REPORT", "6-Week Follow-Up Cardiometabolic Evaluation", {
        "blood_pressure_systolic": 126.0,
        "blood_pressure_diastolic": 80.0,
        "total_cholesterol": 198.0,
        "ldl": 122.0,
        "fasting_glucose": 96.0,
        "hba1c": 5.6,
        "bmi": 28.5,
    }, risk_score=28.0, days_ago=0)

    result = compute_comparison("user_demo", [v2, v1])
    assert result.status == "COMPARED", f"Expected COMPARED, got {result.status}"
    assert len(result.biomarkers) >= 3, f"Expected >=3 biomarker deltas, got {len(result.biomarkers)}"
    # At least some should be improved (all went down toward normal)
    assert result.counts.improved >= 2, f"Expected >=2 improved, got {result.counts.improved}"

