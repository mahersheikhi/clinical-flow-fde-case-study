"""Dependency-free evaluation for the Clinical Flow case study.

All inputs are synthetic. This is a portfolio demonstrator, not clinical software.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

THRESHOLD = 0.85
EVALUATOR_VERSION = "0.1.0"


def extension_value(record: dict, suffix: str):
    for item in record.get("extension", []):
        if item.get("url", "").endswith(suffix):
            return item.get("valueInteger") or item.get("valueString")
    return None


def evaluate(record: dict) -> dict:
    required = extension_value(record, "required-fields") or 0
    complete = extension_value(record, "completed-fields") or 0
    completeness = round(complete / required, 2) if required else 0.0
    document_match = 0.76 if len(record.get("supportingInfo", [])) >= 3 else 0.45
    policy_fit = 0.82 if record.get("code", {}).get("text") == "Neurology consult" else 0.5
    confidence = round((completeness + document_match + policy_fit) / 3, 2)
    missing_field = extension_value(record, "missing-field")
    decision = "REVIEW_READY" if confidence >= THRESHOLD and not missing_field else "NEEDS_HUMAN_REVIEW"
    return {
        "event_id": f"EVAL-{record.get('id', 'UNKNOWN')}",
        "evaluator_version": EVALUATOR_VERSION,
        "decision": decision,
        "confidence": confidence,
        "threshold": THRESHOLD,
        "signals": {"completeness": completeness, "document_match": document_match, "policy_fit": policy_fit},
        "human_review_reason": f"Missing required field: {missing_field}" if missing_field else None,
    }


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/referral_2048.json")
    record = json.loads(path.read_text(encoding="utf-8"))
    print(json.dumps(evaluate(record), indent=2))


if __name__ == "__main__":
    main()
