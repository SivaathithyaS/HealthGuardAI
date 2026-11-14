"""
llm_narrator.py
===============
LLM narration layer for HealthGuard AI longitudinal comparisons.

Architecture:
  - LLMClient protocol (abstract)
  - GroqClient: calls Groq Llama 3.3 70B with structured JSON output
  - Validator: schema + hallucination guard
  - template_narrator: deterministic fallback, always correct
  - narrate(result): main entry point
"""

from __future__ import annotations

import os
import re
import json
import time
import logging
import threading
from typing import Any, Dict, List, Optional, Protocol

import httpx

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
LLM_NARRATION_ENABLED = os.getenv("LLM_NARRATION_ENABLED", "true").lower() not in ("false", "0", "no")

# Rate limiting: max 2 concurrent LLM calls, 20 calls/user/day
_LLM_SEMAPHORE = threading.Semaphore(2)

# Per-user daily call tracking {user_id: (date_str, count)}
_USER_CALL_TRACKER: Dict[str, tuple] = {}
_TRACKER_LOCK = threading.Lock()
MAX_CALLS_PER_USER_PER_DAY = 20


def _check_rate_limit(user_id: str) -> bool:
    """Returns True if the user is within daily rate limit."""
    today = time.strftime("%Y-%m-%d")
    with _TRACKER_LOCK:
        date_str, count = _USER_CALL_TRACKER.get(user_id, (today, 0))
        if date_str != today:
            date_str, count = today, 0
        if count >= MAX_CALLS_PER_USER_PER_DAY:
            return False
        _USER_CALL_TRACKER[user_id] = (date_str, count + 1)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# LLMClient Protocol
# ─────────────────────────────────────────────────────────────────────────────

class LLMClient(Protocol):
    def complete_json(self, system: str, user: str) -> dict:
        """Call the LLM and return parsed JSON dict."""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# GroqClient
# ─────────────────────────────────────────────────────────────────────────────

class GroqClient:
    """Groq Llama 3.3 70B client with retry logic and structured JSON output."""

    API_URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, api_key: str = GROQ_API_KEY, model: str = GROQ_MODEL):
        self.api_key = api_key
        self.model = model

    def complete_json(self, system: str, user: str) -> dict:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
            "max_tokens": 1500,
        }

        last_exc = None
        for attempt in range(3):
            try:
                with httpx.Client(timeout=15.0) as client:
                    r = client.post(self.API_URL, headers=headers, json=payload)

                if r.status_code == 200:
                    data = r.json()
                    text = data["choices"][0]["message"]["content"]
                    return json.loads(text)

                # Retryable errors
                if r.status_code in (429, 500, 502, 503, 504):
                    retry_after = float(r.headers.get("Retry-After", 2 ** attempt))
                    logger.warning("Groq returned %s, retrying in %.1fs", r.status_code, retry_after)
                    time.sleep(retry_after)
                    last_exc = Exception(f"Groq HTTP {r.status_code}")
                    continue

                raise Exception(f"Groq HTTP {r.status_code}: {r.text[:200]}")

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                logger.warning("Groq network error (attempt %d): %s", attempt + 1, e)
                last_exc = e
                time.sleep(1.5 ** attempt)
                continue

        raise last_exc or Exception("Groq call failed after retries")


# ─────────────────────────────────────────────────────────────────────────────
# System Prompt
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = """
You are a plain-language health summary assistant for HealthGuard AI.

RULES — read carefully:
1. Use ONLY the numbers in the provided input JSON. Do NOT compute new numbers, averages, or percentages not already given.
2. Do NOT diagnose with certainty. Do NOT declare the patient has any incurable disease or confirmed condition (e.g. avoid phrases like "you have diabetes" or "diagnosed with").
3. Give NO medication, dosage, or treatment advice. Never name specific prescription drugs or dosing regimens.
4. Do NOT use the words "cured" or "healthy" as absolute declarations, but DO explain what healthy target ranges and positive physiological trends represent.
5. If trajectory is "MIXED", mention BOTH directions — improvements AND worsenings.
6. Use plain, empathetic language that a non-clinician can easily understand.
7. End the summary by recommending discussion with a clinician.
8. Each biomarker must appear in the correct group matching its "assessment" field (improved/worsened/unchanged/changed_within_range/changed_unclear).
9. Never hallucinate biomarker names not in the input.
10. ALWAYS include all 8 top-level keys in the JSON output, using empty arrays [] or strings "" if none apply: "headline", "improved", "worsened", "unchanged", "summary", "overall_assessment", "health_tips", "caveats".
11. CLINICAL SIGNIFICANCE: For each biomarker in improved, worsened, and unchanged, provide BOTH:
    - "note": A concise 1-sentence summary of the exact change (e.g. "Decreased by 46 mg/dL moving into target range.").
    - "clinical_significance": A clear 1-2 sentence explanation starting directly with what this biomarker does and what this change actually means for the patient's body (e.g., why a drop in sugar/cholesterol is good for blood vessels and heart, or why a rise in creatinine/blood pressure stresses the kidneys and cardiovascular system).
12. OVERALL CONDITION & HEALTH TIPS:
    - "overall_assessment": A 1-2 sentence evaluation of the patient's current overall health condition, clearly describing how much it has developed (improved) or worsened between visits.
    - "health_tips": An array of 2-3 practical, evidence-based lifestyle/preventive tips (nutrition, activity, sleep, hydration, monitoring) to support health improvement based on the specific metrics observed.

REQUIRED JSON OUTPUT FORMAT (strict, no extra keys):
{
  "headline": "<max 15 words describing the overall trajectory>",
  "improved": [
    {
      "biomarker": "<label>",
      "from": <number>,
      "to": <number>,
      "unit": "<unit>",
      "note": "<concise change summary>",
      "clinical_significance": "<1-2 sentences: what this biomarker does and why this improvement benefits health>"
    }
  ],
  "worsened": [
    {
      "biomarker": "<label>",
      "from": <number>,
      "to": <number>,
      "unit": "<unit>",
      "note": "<concise change summary>",
      "clinical_significance": "<1-2 sentences: what this biomarker does and what health risk or stress this worsening signals>"
    }
  ],
  "unchanged": [
    {
      "biomarker": "<label>",
      "from": <number>,
      "to": <number>,
      "unit": "<unit>",
      "note": "<concise change summary>",
      "clinical_significance": "<1 sentence: what this biomarker does and why stability is maintained>"
    }
  ],
  "summary": "<2-4 sentences covering what improved, what worsened, why these changes matter for the body, and recommending clinician consultation>",
  "overall_assessment": "<1-2 sentences giving an overall idea of the patient's current health condition and how much it developed or worsened>",
  "health_tips": [
    "<practical lifestyle or preventive tip 1>",
    "<practical lifestyle or preventive tip 2>",
    "<practical lifestyle or preventive tip 3>"
  ],
  "caveats": ["<caveat 1>", "<caveat 2>"]
}
""".strip()


# ─────────────────────────────────────────────────────────────────────────────
# Payload Builder (strips identifiers)
# ─────────────────────────────────────────────────────────────────────────────

_FORBIDDEN_DRUG_PATTERN = re.compile(
    r"\b(take\s+\w+|start\s+\w+|stop\s+\w+|dose|mg daily|prescribe|prescription|metformin|statin|statins|insulin|"
    r"lisinopril|amlodipine|atorvastatin|aspirin|warfarin)\b",
    re.IGNORECASE,
)

_FORBIDDEN_DIAGNOSE_PATTERN = re.compile(
    r"\b(diagnosed with|confirmed diagnosis|confirmed case of|you have diabetes|you have hypertension|you suffer from)\b",
    re.IGNORECASE,
)


def _build_payload(result: dict) -> str:
    """Build a sanitized payload dict for the LLM (no PII, no IDs, no dates)."""
    biomarkers = result.get("biomarkers") or []
    # Only include biomarkers that have meaningful data
    bio_list = []
    for b in biomarkers:
        bio_list.append({
            "biomarker": b.get("label") or b.get("biomarker"),
            "unit": b.get("unit"),
            "from": b.get("prior"),
            "to": b.get("current"),
            "delta": b.get("delta"),
            "pct_change": b.get("pct_change"),
            "assessment": b.get("assessment"),
            "ref_low": b.get("ref_low"),
            "ref_high": b.get("ref_high"),
        })

    payload = {
        "modality": result.get("modality"),
        "condition": result.get("condition"),
        "days_between": result.get("days_between"),
        "trajectory": result.get("trajectory"),
        "risk_score": result.get("risk_score"),
        "biomarkers": bio_list,
        "counts": result.get("counts"),
    }
    return json.dumps(payload, indent=2)


# ─────────────────────────────────────────────────────────────────────────────
# Validator
# ─────────────────────────────────────────────────────────────────────────────

class ValidationError(Exception):
    pass


def _collect_allowed_numbers(result: dict) -> set:
    """Collect all numeric values from the ComparisonResult that the LLM is allowed to use."""
    allowed = set()
    for b in (result.get("biomarkers") or []):
        for field in ("prior", "current", "delta", "pct_change", "ref_low", "ref_high"):
            v = b.get(field)
            if v is not None:
                val = float(v)
                allowed.add(round(val, 1))
                allowed.add(round(val, 0))
                allowed.add(round(abs(val), 1))
                allowed.add(round(abs(val), 0))
    if result.get("days_between") is not None:
        allowed.add(float(result["days_between"]))
    counts = result.get("counts") or {}
    for v in counts.values() if isinstance(counts, dict) else []:
        if v is not None:
            allowed.add(float(v))
    rs = result.get("risk_score") or {}
    for field in ("prior", "current", "delta"):
        v = (rs if isinstance(rs, dict) else {}).get(field)
        if v is not None:
            allowed.add(round(float(v), 1))
    return allowed


def _get_input_biomarker_labels(result: dict) -> set:
    labels = set()
    for b in (result.get("biomarkers") or []):
        label = b.get("label") or b.get("biomarker")
        if label:
            labels.add(label.lower())
    return labels


def validate_narrative(narrative: dict, result: dict) -> List[str]:
    """
    Validates an LLM narrative dict against the input result.
    Returns a list of error strings (empty = valid).
    """
    errors = []

    # Default empty arrays or strings if omitted
    for k in ("improved", "worsened", "unchanged", "caveats", "health_tips"):
        if k not in narrative or narrative[k] is None:
            narrative[k] = []
    if "overall_assessment" not in narrative or narrative["overall_assessment"] is None:
        narrative["overall_assessment"] = ""

    # Schema check
    required_keys = {"headline", "improved", "worsened", "unchanged", "summary", "caveats"}
    missing = required_keys - set(narrative.keys())
    if missing:
        errors.append(f"Missing required keys: {missing}")
        return errors  # Can't continue without structure

    # Headline length
    if len(narrative.get("headline", "").split()) > 15:
        errors.append("Headline exceeds 15 words")

    # Summary length
    summary = narrative.get("summary", "")
    if len(summary) > 1200:
        errors.append("Summary too long (>1200 chars)")

    # Drug / diagnosis phrases
    text_fields = (
        [summary, narrative.get("overall_assessment", "")]
        + narrative.get("caveats", [])
        + narrative.get("health_tips", [])
    )
    for text_field in text_fields:
        if _FORBIDDEN_DRUG_PATTERN.search(str(text_field)):
            errors.append(f"Forbidden drug/treatment language in: {str(text_field)[:80]}")
        if _FORBIDDEN_DIAGNOSE_PATTERN.search(str(text_field)):
            errors.append(f"Forbidden diagnosis language in: {str(text_field)[:80]}")

    # Build input biomarker lookup (label → assessment)
    input_bio_map = {}
    for b in (result.get("biomarkers") or []):
        label = (b.get("label") or b.get("biomarker") or "").lower()
        if label:
            input_bio_map[label] = b.get("assessment", "")

    # Check each listed biomarker exists in input and is in the correct group
    group_to_assessments = {
        "improved": {"improved"},
        "worsened": {"worsened"},
        "unchanged": {"unchanged", "changed_within_range", "stable", "censored_skipped", "changed_unclear"},
    }
    for group, expected_assessments in group_to_assessments.items():
        for entry in narrative.get(group, []):
            bio_name = (entry.get("biomarker") or "").lower()
            if bio_name not in input_bio_map:
                errors.append(f"Biomarker '{bio_name}' in group '{group}' not found in input")
                continue
            actual_assessment = input_bio_map.get(bio_name, "")
            if actual_assessment not in expected_assessments:
                errors.append(
                    f"Biomarker '{bio_name}' placed in '{group}' but input assessment is '{actual_assessment}'"
                )

    # Hallucinated numbers: scan summary and notes for numbers not in allowed set
    allowed = _collect_allowed_numbers(result)
    # Allow small integers (counts, etc.) and common time/physiology windows (24h, 30d, 90d, 120d)
    allowed.update({float(i) for i in range(0, 10)})
    allowed.update({24.0, 30.0, 60.0, 90.0, 120.0})

    def _check_text_for_hallucinated_numbers(text: str, field: str):
        numbers_in_text = re.findall(r"-?\d+(?:\.\d+)?", text)
        for num_str in numbers_in_text:
            num = float(num_str)
            # Allow if within 0.5 of any allowed number (rounding tolerance)
            if not any(abs(num - a) <= 0.5 for a in allowed):
                errors.append(f"Possibly hallucinated number {num} in field '{field}'")

    _check_text_for_hallucinated_numbers(summary, "summary")
    for entry in narrative.get("improved", []) + narrative.get("worsened", []) + narrative.get("unchanged", []):
        _check_text_for_hallucinated_numbers(entry.get("note", ""), "note")
        if entry.get("clinical_significance"):
            _check_text_for_hallucinated_numbers(entry.get("clinical_significance", ""), "clinical_significance")

    return errors


# ─────────────────────────────────────────────────────────────────────────────
# Template Narrator (deterministic fallback)
# ─────────────────────────────────────────────────────────────────────────────

def template_narrator(result: dict) -> dict:
    """
    Build a narrative from the ComparisonResult using plain f-strings.
    Always correct (deterministic). Used as fallback and for BASELINE/NOT_COMPARABLE.
    """
    status = result.get("status", "")
    trajectory = result.get("trajectory", "")
    days = result.get("days_between")
    modality = result.get("modality") or "clinical"
    condition = result.get("condition") or "this visit"
    counts = result.get("counts") or {}
    if isinstance(counts, dict):
        n_improved = counts.get("improved", 0)
        n_worsened = counts.get("worsened", 0)
        n_unchanged = counts.get("unchanged", 0)
    else:
        n_improved = getattr(counts, "improved", 0)
        n_worsened = getattr(counts, "worsened", 0)
        n_unchanged = getattr(counts, "unchanged", 0)

    # Build grouped biomarker lists
    improved_list, worsened_list, unchanged_list = [], [], []
    for b in (result.get("biomarkers") or []):
        label = b.get("label") or b.get("biomarker") or "Unknown"
        unit = b.get("unit") or ""
        frm = b.get("prior")
        to = b.get("current")
        assessment = b.get("assessment", "")
        entry = {
            "biomarker": label,
            "from": frm,
            "to": to,
            "unit": unit,
            "note": _template_note(label, frm, to, unit, assessment),
            "clinical_significance": _template_clinical_significance(label, assessment),
        }
        if assessment == "improved":
            improved_list.append(entry)
        elif assessment == "worsened":
            worsened_list.append(entry)
        else:
            unchanged_list.append(entry)

    # Headline
    if status == "BASELINE":
        headline = f"First {modality.lower()} visit recorded — baseline established"
    elif status == "NOT_COMPARABLE":
        headline = "No comparable prior visit found for trajectory comparison"
    elif trajectory == "FAVORABLE_TRAJECTORY":
        headline = f"Positive trend: {n_improved} biomarker(s) improved over {days or '?'} days"
    elif trajectory == "ATTENTION_REQUIRED":
        headline = f"Attention needed: {n_worsened} biomarker(s) show worsening trend"
    elif trajectory == "MIXED":
        headline = f"Mixed results: {n_improved} improved, {n_worsened} worsened over {days or '?'} days"
    else:
        headline = f"Stable metrics over {days or '?'} days"

    # Summary
    if status == "BASELINE":
        summary = (
            f"This is your first recorded {modality.lower()} visit for {condition}. "
            "Baseline values have been captured for future comparison. "
            "Please discuss these results with your clinician."
        )
    elif status == "NOT_COMPARABLE":
        reason = result.get("not_comparable_reason") or result.get("summary_advice") or ""
        summary = (
            f"A direct visit-over-visit comparison could not be performed. {reason} "
            "Please discuss your clinical history with your healthcare provider."
        )
    elif trajectory == "FAVORABLE_TRAJECTORY":
        bio_names = ", ".join(b["biomarker"] for b in improved_list[:3])
        summary = (
            f"Compared to the prior visit {days} days ago, {n_improved} biomarker(s) "
            f"show meaningful improvement ({bio_names}). "
            f"{n_unchanged} biomarker(s) remain stable. "
            "Continue your current management plan and discuss these results with your clinician."
        )
    elif trajectory == "ATTENTION_REQUIRED":
        bio_names = ", ".join(b["biomarker"] for b in worsened_list[:3])
        summary = (
            f"Compared to the prior visit {days} days ago, {n_worsened} biomarker(s) "
            f"show worsening trends ({bio_names}). "
            "Prompt clinical follow-up is recommended to review and adjust your management plan."
        )
    elif trajectory == "MIXED":
        imp_names = ", ".join(b["biomarker"] for b in improved_list[:2])
        wor_names = ", ".join(b["biomarker"] for b in worsened_list[:2])
        summary = (
            f"Compared to the prior visit {days} days ago, results are mixed. "
            f"Improvements seen in {imp_names}. "
            f"Attention needed for {wor_names}. "
            "Discuss both trends with your clinician."
        )
    else:
        summary = (
            f"Compared to the prior visit {days} days ago, health metrics are broadly stable. "
            "Maintain your current preventive regimen and schedule routine follow-up."
        )

    caveats = [
        "This summary is generated automatically and does not replace clinical judgment.",
        "Please discuss all findings with a qualified healthcare clinician.",
    ]
    if result.get("stale_comparison"):
        caveats.append("This comparison spans more than 2 years; individual circumstances may have changed significantly.")
    if result.get("possible_duplicate"):
        caveats.append("This visit appears very similar to the prior one; values may be duplicate entries.")

    # Overall condition idea (how much it developed or worsened)
    if status == "BASELINE":
        overall_assessment = "Baseline health assessment established; metrics provide a foundational benchmark for tracking your health trajectory over future visits."
    elif status == "NOT_COMPARABLE":
        overall_assessment = "Health metrics recorded for this clinical modality; regular longitudinal follow-ups will establish comparative development."
    elif trajectory == "FAVORABLE_TRAJECTORY":
        overall_assessment = f"Overall, your health condition shows significant positive development, with {n_improved} key metric(s) improving toward healthy targets over {days or 'recent'} days."
    elif trajectory == "ATTENTION_REQUIRED":
        overall_assessment = f"Overall, your health condition shows signs of increased strain, with {n_worsened} biomarker(s) worsening and indicating a need for proactive clinical adjustments."
    elif trajectory == "MIXED":
        overall_assessment = f"Overall, your health condition reflects mixed development: notable improvements in {n_improved} metric(s) are balanced by {n_worsened} area(s) showing upward strain that need attention."
    else:
        overall_assessment = f"Overall, your health condition has remained consistent and stable over {days or 'recent'} days, maintaining baseline equilibrium."

    # Practical lifestyle tips
    health_tips = []
    bio_names_lower = " ".join(b.get("biomarker", "").lower() for b in (improved_list + worsened_list))
    if any(k in bio_names_lower for k in ["glucose", "hba1c", "sugar"]):
        health_tips.append("Focus on high-fiber foods, lean proteins, and consistent meal timing to support steady glucose regulation.")
    if any(k in bio_names_lower for k in ["blood pressure", "systolic", "diastolic"]):
        health_tips.append("Incorporate 20-30 minutes of daily aerobic movement and moderate sodium intake to support vascular elasticity.")
    if any(k in bio_names_lower for k in ["cholesterol", "ldl", "lipid"]):
        health_tips.append("Choose heart-healthy unsaturated fats (olive oil, avocados, nuts) and limit saturated fats to support optimal lipid clearance.")
    if any(k in bio_names_lower for k in ["creatinine", "kidney", "renal"]):
        health_tips.append("Maintain optimal daily hydration and avoid overuse of non-steroidal anti-inflammatory drugs (NSAIDs) to protect renal function.")
    if not health_tips:
        health_tips = [
            "Maintain consistent daily hydration and aim for 7-8 hours of quality sleep to support cellular recovery.",
            "Incorporate 150 minutes of moderate physical activity throughout the week for comprehensive cardiovascular support.",
            "Schedule regular periodic follow-up screenings with your clinician to monitor your long-term health trajectory."
        ]

    return {
        "headline": headline,
        "improved": improved_list,
        "worsened": worsened_list,
        "unchanged": unchanged_list,
        "summary": summary,
        "overall_assessment": overall_assessment,
        "health_tips": health_tips,
        "caveats": caveats,
        "narrative_source": "template",
        "llm_model": None,
        "validation_errors": [],
    }


_CLINICAL_SIGNIFICANCE_MAP = {
    "hba1c": {
        "improved": "Reflects average 3-month blood sugar. Lowering toward target reduces long-term strain on blood vessels, nerves, and organs.",
        "worsened": "Indicates rising average blood sugar over the last 3 months, increasing risk of microvascular and metabolic complications.",
        "unchanged": "Reflects stable 3-month blood sugar regulation.",
    },
    "glucose": {
        "improved": "Fasting blood sugar normalized toward target, indicating better insulin efficiency and reduced metabolic strain.",
        "worsened": "Fasting blood sugar has elevated, indicating increased metabolic stress and insulin resistance.",
        "unchanged": "Fasting blood sugar remains stable within current management.",
    },
    "fasting": {
        "improved": "Fasting blood sugar normalized toward target, indicating better insulin efficiency and reduced metabolic strain.",
        "worsened": "Fasting blood sugar has elevated, indicating increased metabolic stress and insulin resistance.",
        "unchanged": "Fasting blood sugar remains stable within current management.",
    },
    "systolic": {
        "improved": "Lower arterial pressure during heartbeat reduces mechanical strain on blood vessel walls and lowers cardiovascular risk.",
        "worsened": "Elevated arterial pressure increases workload on the heart and arterial walls, warranting blood pressure monitoring.",
        "unchanged": "Arterial systolic pressure remains stable.",
    },
    "diastolic": {
        "improved": "Lower resting arterial pressure reduces chronic strain on the vascular system.",
        "worsened": "Elevated resting arterial pressure indicates greater vascular resistance between heartbeats.",
        "unchanged": "Resting arterial pressure remains stable.",
    },
    "ldl": {
        "improved": "Lowering atherogenic LDL cholesterol reduces plaque buildup in arteries, protecting cardiovascular health.",
        "worsened": "Higher LDL cholesterol promotes arterial plaque accumulation and increases cardiovascular risk.",
        "unchanged": "LDL cholesterol remains stable at current levels.",
    },
    "cholesterol": {
        "improved": "Overall blood lipid levels have decreased toward desirable ranges, supporting healthy blood circulation.",
        "worsened": "Overall blood lipid levels have increased, signaling higher lipid load in circulation.",
        "unchanged": "Total cholesterol levels remain stable.",
    },
    "creatinine": {
        "improved": "Serum creatinine level has decreased toward normal, indicating efficient kidney waste filtration.",
        "worsened": "Serum creatinine level has risen, signaling increased filtration workload or stress on the kidneys.",
        "unchanged": "Kidney filtration waste markers remain stable.",
    },
    "platelet": {
        "improved": "Platelet counts have recovered toward normal, restoring healthy blood clotting and reducing bleeding risk.",
        "worsened": "Platelet counts have decreased, increasing risk of easy bruising or bleeding complications.",
        "unchanged": "Platelet levels remain stable.",
    },
    "ast": {
        "improved": "Liver enzyme levels have decreased toward baseline, reflecting reduced hepatic cellular stress.",
        "worsened": "Liver enzyme levels have elevated, suggesting increased stress or inflammation in liver cells.",
        "unchanged": "Liver transaminase levels remain stable.",
    },
    "alt": {
        "improved": "Liver enzyme levels have normalized, indicating recovery from hepatocellular stress.",
        "worsened": "Liver enzyme levels have risen, indicating active liver cell inflammation or stress.",
        "unchanged": "Liver transaminase levels remain stable.",
    },
    "hemoglobin": {
        "improved": "Hemoglobin has improved toward normal, enhancing oxygen delivery to tissues throughout the body.",
        "worsened": "Hemoglobin has dropped, which may cause fatigue and reduced oxygen carrying capacity.",
        "unchanged": "Oxygen-carrying hemoglobin levels remain stable.",
    },
    "bmi": {
        "improved": "BMI reduction toward normal ranges decreases metabolic stress and reduces cardiovascular workload.",
        "worsened": "BMI increase places additional metabolic and joint workload on the body.",
        "unchanged": "Body mass index remains stable.",
    },
}


def _template_clinical_significance(label: str, assessment: str) -> str:
    key = (label or "").lower()
    for pattern, mapping in _CLINICAL_SIGNIFICANCE_MAP.items():
        if pattern in key:
            if assessment in mapping:
                return mapping[assessment]
            return mapping.get("unchanged", "")
    if assessment == "improved":
        return f"Moving {label} toward its reference range supports healthy physiological balance."
    elif assessment == "worsened":
        return f"Worsening in {label} indicates physiological strain that warrants review with a clinician."
    else:
        return f"{label} remains within an expected range under observation."


def _template_note(label: str, frm, to, unit: str, assessment: str) -> str:
    if frm is None or to is None:
        return f"{label} data recorded."
    delta = to - frm
    direction = "increased" if delta > 0 else "decreased"
    abs_d = abs(delta)
    if assessment == "improved":
        return f"{label} {direction} by {abs_d:.1f} {unit}, moving toward the reference range."
    elif assessment == "worsened":
        return f"{label} {direction} by {abs_d:.1f} {unit}, moving further from the reference range."
    elif assessment == "changed_within_range":
        return f"{label} changed by {abs_d:.1f} {unit} but remains within the reference range."
    else:
        return f"{label} {direction} by {abs_d:.1f} {unit}."


# ─────────────────────────────────────────────────────────────────────────────
# Main Narrate Entry Point
# ─────────────────────────────────────────────────────────────────────────────

def narrate(
    result: dict,
    user_id: Optional[str] = None,
    llm_client: Optional[LLMClient] = None,
) -> dict:
    """
    Generate a narrative for a ComparisonResult dict.

    - For BASELINE or NOT_COMPARABLE: always returns template (no LLM call).
    - For COMPARED: attempts LLM if enabled, falls back to template on failure.

    Returns the narrative dict with added fields:
      narrative_source: "llm" | "template"
      llm_model: str or None
      validation_errors: list
    """
    status = result.get("status", "")

    # Always use template for non-COMPARED statuses
    if status != "COMPARED":
        return template_narrator(result)

    # Check if LLM is enabled
    if not LLM_NARRATION_ENABLED:
        t = template_narrator(result)
        t["narrative_source"] = "template"
        return t

    if not GROQ_API_KEY and llm_client is None:
        t = template_narrator(result)
        t["narrative_source"] = "template"
        return t

    # Rate limit check
    if user_id and not _check_rate_limit(user_id):
        logger.warning("LLM rate limit exceeded for user %s, using template", user_id)
        t = template_narrator(result)
        t["narrative_source"] = "template"
        t["validation_errors"] = ["Rate limit exceeded — template used"]
        return t

    # Build LLM client if not injected
    if llm_client is None:
        llm_client = GroqClient()

    payload_str = _build_payload(result)
    user_prompt = f"Narrate this health comparison:\n\n{payload_str}"

    validation_errors: List[str] = []

    with _LLM_SEMAPHORE:
        for attempt in range(2):
            try:
                extra = ""
                if attempt > 0 and validation_errors:
                    extra = f"\n\nPrevious attempt had these validation errors — fix them:\n{json.dumps(validation_errors)}"
                narrative = llm_client.complete_json(_SYSTEM_PROMPT, user_prompt + extra)
                validation_errors = validate_narrative(narrative, result)
                if not validation_errors:
                    narrative["narrative_source"] = "llm"
                    narrative["llm_model"] = GROQ_MODEL
                    narrative["validation_errors"] = []
                    return narrative
                logger.warning("LLM validation failed (attempt %d): %s", attempt + 1, validation_errors)
            except Exception as e:
                logger.error("LLM call failed (attempt %d): %s", attempt + 1, e)
                validation_errors = [str(e)]
                break

    # Fallback to template
    logger.info("Falling back to template narrator after LLM failure/validation error")
    t = template_narrator(result)
    t["narrative_source"] = "template"
    t["validation_errors"] = validation_errors
    return t

