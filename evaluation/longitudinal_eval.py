"""
evaluation/longitudinal_eval.py
================================
Evaluation script for the longitudinal comparison engine and LLM narrator.

Usage:
  python evaluation/longitudinal_eval.py           # engine-only (no GROQ key needed)
  GROQ_API_KEY=... python evaluation/longitudinal_eval.py  # with LLM evaluation

Respects free-tier limits: at most 30 requests/minute, sleeps between calls.
Writes results to evaluation/results.json and prints a markdown table.
"""

from __future__ import annotations

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

logging.basicConfig(level=logging.WARNING)

from backend.app.services.longitudinal_service import compute_comparison, canonicalize
from backend.app.services.llm_narrator import narrate, validate_narrative, _FORBIDDEN_DRUG_PATTERN

# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
CASES_FILE = os.path.join(os.path.dirname(__file__), "cases.json")
RESULTS_FILE = os.path.join(os.path.dirname(__file__), "results.json")
MAX_REQUESTS_PER_MINUTE = 30

# ─────────────────────────────────────────────────────────────────────────────
# Case builder
# ─────────────────────────────────────────────────────────────────────────────

def _make_visit(id_: str, modality: str, title: str, biomarkers: dict, risk_score: float = 50.0, days_ago: int = 0):
    # Handle "value unit" strings in biomarkers
    bio_clean = {}
    for k, v in biomarkers.items():
        bio_clean[k] = v
    dt = (datetime.utcnow() - timedelta(days=days_ago)).isoformat()
    return {
        "id": id_, "modality": modality, "title": title,
        "summary": "eval", "risk_score": risk_score,
        "biomarkers": bio_clean, "findings": [], "recommendations": [],
        "created_at": dt,
    }


def _build_visits_from_case(case: dict):
    """Return (visits list newest→oldest, ground_truth, expected_trajectory)"""
    modality = case.get("modality", "LAB_REPORT")
    title = case.get("title", "Panel")

    # Multi-visit cases (3-visit trend)
    if "visits" in case:
        visits_bio = case["visits"]
        visits = []
        for i, bio in enumerate(reversed(visits_bio)):
            days_ago = len(visits_bio) - i - 1
            visits.append(_make_visit(
                f"v{i+1}", modality, title, bio,
                days_ago=days_ago * 42
            ))
        return visits, case.get("ground_truth", {}), case.get("trajectory", "STABLE_MAINTENANCE")

    # Modality mismatch case
    modality_prior = case.get("modality_prior", modality)
    modality_current = case.get("modality_current", modality)
    title_prior = case.get("title_prior", title)
    title_current = case.get("title_current", title)

    prior_bio = case.get("prior", {})
    current_bio = case.get("current", {})

    v_prior = _make_visit("v1", modality_prior, title_prior, prior_bio, days_ago=42)
    v_current = _make_visit("v2", modality_current, title_current, current_bio, days_ago=0)

    return [v_current, v_prior], case.get("ground_truth", {}), case.get("trajectory", "STABLE_MAINTENANCE")


# ─────────────────────────────────────────────────────────────────────────────
# Evaluation helpers
# ─────────────────────────────────────────────────────────────────────────────

def _direction_match(computed_assessment: str, expected: str) -> bool:
    """True if computed assessment matches the expected ground truth."""
    if expected == "improved":
        return computed_assessment == "improved"
    elif expected == "worsened":
        return computed_assessment == "worsened"
    elif expected in ("unchanged", "stable"):
        return computed_assessment in ("unchanged", "changed_within_range")
    elif expected == "censored_skipped":
        return computed_assessment == "censored_skipped"
    elif expected == "NOT_COMPARABLE":
        return True  # handled at trajectory level
    return computed_assessment == expected


def _trajectory_match(computed: str, expected: str) -> bool:
    if expected == "NOT_COMPARABLE":
        return computed in ("NOT_COMPARABLE", "BASELINE")
    return computed == expected


def _has_hallucinated_number(narrative: dict, result: dict) -> bool:
    """Check if the LLM narrative contains a number not in the input."""
    errors = validate_narrative(narrative, result)
    return any("hallucinated" in e.lower() or "possibly hallucinated" in e.lower() for e in errors)


def _has_drug_phrase(narrative: dict) -> bool:
    full_text = " ".join([
        narrative.get("headline", ""),
        narrative.get("summary", ""),
        " ".join(narrative.get("caveats", [])),
        " ".join(e.get("note", "") for group in [
            narrative.get("improved", []),
            narrative.get("worsened", []),
            narrative.get("unchanged", [])
        ] for e in group),
    ])
    return bool(_FORBIDDEN_DRUG_PATTERN.search(full_text))


# ─────────────────────────────────────────────────────────────────────────────
# Main evaluation loop
# ─────────────────────────────────────────────────────────────────────────────

def run_evaluation():
    with open(CASES_FILE, "r") as f:
        cases = json.load(f)

    run_llm = bool(GROQ_API_KEY)
    print(f"Loaded {len(cases)} evaluation cases.")
    print(f"LLM evaluation: {'YES (Groq)' if run_llm else 'NO (engine only)'}")
    print()

    engine_results = []
    narrator_results = []

    # Rate limit tracking
    request_count = 0
    minute_start = time.time()

    for case in cases:
        case_id = case["id"]
        desc = case["description"]
        ground_truth = case.get("ground_truth", {})
        expected_trajectory = case.get("trajectory", "STABLE_MAINTENANCE")

        try:
            visits, gt, exp_traj = _build_visits_from_case(case)
            result = compute_comparison("eval_user", visits)
            result_dict = result.model_dump()

            # Engine evaluation
            traj_ok = _trajectory_match(result_dict["trajectory"], exp_traj)

            bio_results = {}
            for bio_key, expected_assessment in gt.items():
                if expected_assessment == "NOT_COMPARABLE":
                    bio_results[bio_key] = traj_ok
                    continue
                # Find the computed biomarker
                computed_assessment = None
                for b in result_dict.get("biomarkers", []):
                    if b.get("key") == bio_key or canonicalize(bio_key) == b.get("key"):
                        computed_assessment = b.get("assessment", "")
                        break
                if computed_assessment is None:
                    bio_results[bio_key] = False
                else:
                    bio_results[bio_key] = _direction_match(computed_assessment, expected_assessment)

            all_bio_correct = all(bio_results.values()) if bio_results else True

            engine_results.append({
                "case_id": case_id,
                "description": desc,
                "trajectory_ok": traj_ok,
                "bio_results": bio_results,
                "all_bio_correct": all_bio_correct,
                "computed_trajectory": result_dict["trajectory"],
                "expected_trajectory": exp_traj,
            })

            # LLM evaluation
            if run_llm and result_dict["status"] == "COMPARED":
                # Rate limit: max 30 req/min
                request_count += 1
                elapsed = time.time() - minute_start
                if request_count >= MAX_REQUESTS_PER_MINUTE:
                    sleep_time = max(0, 60 - elapsed)
                    if sleep_time > 0:
                        print(f"  Rate limit: sleeping {sleep_time:.1f}s")
                        time.sleep(sleep_time)
                    request_count = 0
                    minute_start = time.time()
                else:
                    time.sleep(1.0)  # Polite delay

                try:
                    narrative = narrate(result_dict, user_id="eval_user")
                    has_halluc = _has_hallucinated_number(narrative, result_dict)
                    has_drug = _has_drug_phrase(narrative)
                    schema_valid = not bool(validate_narrative(narrative, result_dict))

                    narrator_results.append({
                        "case_id": case_id,
                        "description": desc,
                        "narrative_source": narrative.get("narrative_source"),
                        "schema_valid": schema_valid,
                        "hallucinated_number": has_halluc,
                        "drug_phrase": has_drug,
                        "validation_errors": narrative.get("validation_errors", []),
                    })
                except Exception as e:
                    narrator_results.append({
                        "case_id": case_id,
                        "description": desc,
                        "error": str(e),
                        "schema_valid": False,
                        "hallucinated_number": False,
                        "drug_phrase": False,
                        "validation_errors": [str(e)],
                    })

        except Exception as e:
            engine_results.append({
                "case_id": case_id,
                "description": desc,
                "error": str(e),
                "trajectory_ok": False,
                "bio_results": {},
                "all_bio_correct": False,
            })

    # ── Compute summary stats ──────────────────────────────────────────────

    n = len(engine_results)
    traj_correct = sum(1 for r in engine_results if r.get("trajectory_ok"))
    bio_correct = sum(1 for r in engine_results if r.get("all_bio_correct"))

    all_bio_checks = [(bio_key, ok) for r in engine_results for bio_key, ok in r.get("bio_results", {}).items()]
    n_bio = len(all_bio_checks)
    n_bio_correct = sum(1 for _, ok in all_bio_checks if ok)

    engine_summary = {
        "total_cases": n,
        "trajectory_accuracy": round(traj_correct / n, 3) if n else 0,
        "case_level_accuracy": round(bio_correct / n, 3) if n else 0,
        "biomarker_level_accuracy": round(n_bio_correct / n_bio, 3) if n_bio else 0,
    }

    narrator_summary = {}
    if narrator_results:
        n_narr = len(narrator_results)
        llm_cases = [r for r in narrator_results if r.get("narrative_source") == "llm"]
        narrator_summary = {
            "total_cases_narrated": n_narr,
            "llm_cases": len(llm_cases),
            "template_fallback_cases": n_narr - len(llm_cases),
            "schema_valid_rate": round(sum(1 for r in narrator_results if r.get("schema_valid")) / n_narr, 3),
            "hallucinated_number_rate": round(sum(1 for r in narrator_results if r.get("hallucinated_number")) / n_narr, 3),
            "drug_phrase_rate": round(sum(1 for r in narrator_results if r.get("drug_phrase")) / n_narr, 3),
            "fallback_rate": round((n_narr - len(llm_cases)) / n_narr, 3) if n_narr else 0,
        }

    results = {
        "run_at": datetime.utcnow().isoformat(),
        "llm_enabled": run_llm,
        "engine_summary": engine_summary,
        "narrator_summary": narrator_summary,
        "engine_per_case": engine_results,
        "narrator_per_case": narrator_results,
    }

    with open(RESULTS_FILE, "w") as f:
        json.dump(results, f, indent=2)

    # ── Print markdown table ───────────────────────────────────────────────

    print("## Engine Evaluation Results\n")
    print(f"| Metric | Value |")
    print(f"|--------|-------|")
    print(f"| Total cases | {engine_summary['total_cases']} |")
    print(f"| Trajectory accuracy | {engine_summary['trajectory_accuracy']:.1%} |")
    print(f"| Biomarker-level accuracy | {engine_summary['biomarker_level_accuracy']:.1%} |")
    print(f"| Case-level accuracy (all biomarkers correct) | {engine_summary['case_level_accuracy']:.1%} |")

    if narrator_summary:
        print("\n## Narrator Evaluation Results\n")
        print(f"| Metric | Value |")
        print(f"|--------|-------|")
        print(f"| Cases narrated | {narrator_summary['total_cases_narrated']} |")
        print(f"| LLM responses | {narrator_summary['llm_cases']} |")
        print(f"| Schema-valid rate | {narrator_summary['schema_valid_rate']:.1%} |")
        print(f"| Hallucinated-number rate | {narrator_summary['hallucinated_number_rate']:.1%} |")
        print(f"| Drug phrase rate | {narrator_summary['drug_phrase_rate']:.1%} |")
        print(f"| Fallback rate | {narrator_summary['fallback_rate']:.1%} |")

    print(f"\nResults written to {RESULTS_FILE}")

    # ── Per-case summary ───────────────────────────────────────────────────
    print("\n## Per-Case Results\n")
    print(f"| ID | Description | Trajectory | Bio OK | Notes |")
    print(f"|----|-------------|-----------|--------|-------|")
    for r in engine_results:
        traj = "OK" if r.get("trajectory_ok") else "FAIL"
        bio = "OK" if r.get("all_bio_correct") else "FAIL"
        note = r.get("error", "")[:50] if r.get("error") else r.get("computed_trajectory", "")
        print(f"| {r['case_id']} | {r['description'][:40]} | {traj} | {bio} | {note} |")

    return results


if __name__ == "__main__":
    run_evaluation()

