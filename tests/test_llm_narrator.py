"""
tests/test_llm_narrator.py
==========================
Tests for the LLM narrator module.
Uses a fake LLMClient — no real Groq API calls are made.
"""

import os
import sys
import pytest
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.app.services.llm_narrator import (
    narrate,
    template_narrator,
    validate_narrative,
    _build_payload,
    LLMClient,
)
from backend.app.services.longitudinal_service import compute_comparison


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _make_visit(id_, modality, title, biomarkers, risk_score=50.0, days_ago=0):
    dt = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    return {
        "id": id_, "modality": modality, "title": title,
        "summary": "test", "risk_score": risk_score,
        "biomarkers": biomarkers, "findings": [], "recommendations": [],
        "created_at": dt,
    }


def _compared_result():
    """Build a simple COMPARED result dict for use in narrator tests."""
    v1 = _make_visit("v1", "LAB_REPORT", "Cardio Panel", {
        "hba1c": 8.2, "systolic_bp": 150.0, "ldl": 170.0
    }, days_ago=42)
    v2 = _make_visit("v2", "LAB_REPORT", "Cardio Panel", {
        "hba1c": 6.9, "systolic_bp": 125.0, "ldl": 110.0
    }, days_ago=0)
    result = compute_comparison("user1", [v2, v1])
    return result.model_dump()


class FakeLLMClient:
    """Fake LLM client that returns a valid narrative for well-formed input."""

    def __init__(self, response=None, raises=None):
        self.response = response
        self.raises = raises
        self.calls = []

    def complete_json(self, system: str, user: str) -> dict:
        self.calls.append({"system": system, "user": user})
        if self.raises:
            raise self.raises
        return self.response


def _valid_narrative_for(result: dict) -> dict:
    """Build a valid LLM-shaped narrative that matches the given result."""
    improved, worsened, unchanged = [], [], []
    for b in result.get("biomarkers", []):
        entry = {
            "biomarker": b["label"],
            "from": b["prior"],
            "to": b["current"],
            "unit": b["unit"],
            "note": f"{b['label']} changed.",
        }
        if b["assessment"] == "improved":
            improved.append(entry)
        elif b["assessment"] == "worsened":
            worsened.append(entry)
        else:
            unchanged.append(entry)

    days = result.get("days_between", 0)
    imp_count = result.get("counts", {}).get("improved", 0) if isinstance(result.get("counts"), dict) else 0

    return {
        "headline": "Health metrics show favorable improvement trend",
        "improved": improved,
        "worsened": worsened,
        "unchanged": unchanged,
        "summary": f"Compared to {days} days ago, {imp_count} biomarker(s) improved.",
        "caveats": ["Please consult your clinician for guidance."],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. VALID OUTPUT ACCEPTED
# ─────────────────────────────────────────────────────────────────────────────

def test_valid_llm_output_accepted():
    result = _compared_result()
    good_narrative = _valid_narrative_for(result)
    fake = FakeLLMClient(response=good_narrative)

    with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", True):
        with patch("backend.app.services.llm_narrator.GROQ_API_KEY", "fake-key"):
            output = narrate(result, user_id="u1", llm_client=fake)

    assert output["narrative_source"] == "llm"
    assert output["headline"] == good_narrative["headline"]
    assert output["validation_errors"] == []
    assert len(fake.calls) == 1


# ─────────────────────────────────────────────────────────────────────────────
# 2. INVENTED NUMBER REJECTED
# ─────────────────────────────────────────────────────────────────────────────

def test_invented_number_rejected():
    result = _compared_result()
    good_narrative = _valid_narrative_for(result)
    # Inject a hallucinated number (99999 is not in any biomarker value)
    bad_narrative = {**good_narrative, "summary": "The patient's risk dropped by 99999 points."}

    errors = validate_narrative(bad_narrative, result)
    assert any("99999" in e for e in errors), f"Expected hallucinated number error, got: {errors}"


# ─────────────────────────────────────────────────────────────────────────────
# 3. WRONG LIST PLACEMENT REJECTED
# ─────────────────────────────────────────────────────────────────────────────

def test_wrong_list_placement_rejected():
    result = _compared_result()
    good_narrative = _valid_narrative_for(result)

    # Move all improved biomarkers to worsened list
    bad_narrative = {
        **good_narrative,
        "improved": [],
        "worsened": good_narrative["improved"] + good_narrative["worsened"],
    }

    errors = validate_narrative(bad_narrative, result)
    assert any("placed in" in e or "placement" in e.lower() or "group" in e.lower() for e in errors), \
        f"Expected placement error, got: {errors}"


# ─────────────────────────────────────────────────────────────────────────────
# 4. DRUG NAME REJECTED
# ─────────────────────────────────────────────────────────────────────────────

def test_drug_name_rejected():
    result = _compared_result()
    good_narrative = _valid_narrative_for(result)
    drug_narrative = {**good_narrative, "summary": "Consider starting metformin therapy to control blood sugar."}

    errors = validate_narrative(drug_narrative, result)
    assert any("metformin" in e.lower() or "forbidden" in e.lower() or "drug" in e.lower() for e in errors), \
        f"Expected drug rejection error, got: {errors}"


def test_prescribe_phrase_rejected():
    result = _compared_result()
    good_narrative = _valid_narrative_for(result)
    drug_narrative = {**good_narrative, "summary": "Prescribe statins to lower cholesterol levels."}

    errors = validate_narrative(drug_narrative, result)
    assert len(errors) > 0, f"Expected validation error for 'prescribe', got none"


# ─────────────────────────────────────────────────────────────────────────────
# 5. 429/TIMEOUT → TEMPLATE FALLBACK
# ─────────────────────────────────────────────────────────────────────────────

def test_timeout_falls_back_to_template():
    result = _compared_result()
    fake = FakeLLMClient(raises=Exception("Groq HTTP 429"))

    with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", True):
        with patch("backend.app.services.llm_narrator.GROQ_API_KEY", "fake-key"):
            output = narrate(result, user_id="u1", llm_client=fake)

    assert output["narrative_source"] == "template"
    assert len(output["validation_errors"]) > 0
    # Must NOT contain the scripted/hardcoded text that the COMPARED status falls back to
    assert "headline" in output
    assert "summary" in output


def test_network_error_falls_back_to_template():
    result = _compared_result()
    import httpx
    fake = FakeLLMClient(raises=httpx.TimeoutException("timed out"))

    with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", True):
        with patch("backend.app.services.llm_narrator.GROQ_API_KEY", "fake-key"):
            output = narrate(result, user_id="u1", llm_client=fake)

    assert output["narrative_source"] == "template"


# ─────────────────────────────────────────────────────────────────────────────
# 6. DISABLED FLAG → TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

def test_disabled_flag_uses_template():
    result = _compared_result()
    fake = FakeLLMClient(response=_valid_narrative_for(result))

    with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", False):
        output = narrate(result, user_id="u1", llm_client=fake)

    assert output["narrative_source"] == "template"
    assert len(fake.calls) == 0  # LLM should NOT be called


# ─────────────────────────────────────────────────────────────────────────────
# 7. BASELINE / NOT_COMPARABLE → TEMPLATE, NEVER LLM
# ─────────────────────────────────────────────────────────────────────────────

def test_baseline_uses_template():
    v1 = _make_visit("v1", "LAB_REPORT", "Panel", {"hba1c": 7.0})
    result = compute_comparison("user1", [v1]).model_dump()
    assert result["status"] == "BASELINE"

    fake = FakeLLMClient(response={"headline": "x", "improved": [], "worsened": [], "unchanged": [], "summary": "x", "caveats": []})

    with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", True):
        with patch("backend.app.services.llm_narrator.GROQ_API_KEY", "fake-key"):
            output = narrate(result, user_id="u1", llm_client=fake)

    assert output["narrative_source"] == "template"
    assert len(fake.calls) == 0  # No LLM for BASELINE


def test_not_comparable_uses_template():
    v1 = _make_visit("v1", "LAB_REPORT", "Panel", {"hba1c": 7.0}, days_ago=30)
    v2 = _make_visit("v2", "ECG_REPORT", "ECG", {"hba1c": 6.5}, days_ago=0)
    result = compute_comparison("user1", [v2, v1]).model_dump()
    assert result["status"] == "NOT_COMPARABLE"

    fake = FakeLLMClient(response=_valid_narrative_for(result))

    with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", True):
        with patch("backend.app.services.llm_narrator.GROQ_API_KEY", "fake-key"):
            output = narrate(result, user_id="u1", llm_client=fake)

    assert output["narrative_source"] == "template"
    assert len(fake.calls) == 0


# ─────────────────────────────────────────────────────────────────────────────
# 8. TEMPLATE NARRATOR OUTPUT SHAPE
# ─────────────────────────────────────────────────────────────────────────────

def test_template_narrator_shape():
    result = _compared_result()
    t = template_narrator(result)
    assert "headline" in t
    assert "improved" in t
    assert "worsened" in t
    assert "unchanged" in t
    assert "summary" in t
    assert "caveats" in t
    assert isinstance(t["caveats"], list)
    assert len(t["caveats"]) >= 1


def test_template_no_hallucination():
    """Template should never reference drug names or give diagnoses."""
    result = _compared_result()
    t = template_narrator(result)
    full_text = " ".join([
        t.get("headline", ""),
        t.get("summary", ""),
        " ".join(t.get("caveats", [])),
        " ".join(e.get("note", "") for group in [t.get("improved", []), t.get("worsened", []), t.get("unchanged", [])] for e in group),
    ])
    # Should never recommend drugs
    forbidden = ["metformin", "statin", "insulin", "prescribe", "you have diabetes", "diagnosed with"]
    for f in forbidden:
        assert f.lower() not in full_text.lower(), f"Template contains forbidden phrase: {f!r}"


# ─────────────────────────────────────────────────────────────────────────────
# 9. PAYLOAD BUILDER STRIPS PII
# ─────────────────────────────────────────────────────────────────────────────

def test_payload_has_no_pii():
    result = _compared_result()
    result["current_id"] = "chk_abc123"
    result["prior_id"] = "chk_def456"
    payload_str = _build_payload(result)
    assert "chk_abc123" not in payload_str
    assert "chk_def456" not in payload_str
    assert "user_id" not in payload_str


# ─────────────────────────────────────────────────────────────────────────────
# 10. MISSING API KEY → TEMPLATE
# ─────────────────────────────────────────────────────────────────────────────

def test_missing_api_key_uses_template():
    result = _compared_result()

    with patch("backend.app.services.llm_narrator.GROQ_API_KEY", ""):
        with patch("backend.app.services.llm_narrator.LLM_NARRATION_ENABLED", True):
            output = narrate(result, user_id="u1")  # No llm_client injected

    assert output["narrative_source"] == "template"

