#!/usr/bin/env python3
"""Score explicit audit predictions against a declared fixture truth set.

The scorer is intentionally dumb and transparent. It never reads a report's
marketing language; predictions must identify a fixture, verdict, and root
cause. This makes benchmark numbers reproducible and exposes missing outputs.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path


POSITIVE_VERDICTS = {"valid", "likely valid", "confirmed", "true positive"}


def load_json(path: Path):
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, dict) and "fixtures" in value:
        value = value["fixtures"]
    if isinstance(value, dict):
        return [{"fixture": key, **(item if isinstance(item, dict) else {"bug_class": item})} for key, item in value.items()]
    if not isinstance(value, list):
        raise ValueError(f"{path} must contain a list or fixture mapping")
    return value


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def is_correct_root_cause(expected: str, reported: str) -> bool:
    if not expected:
        return True
    expected_norm = normalize(expected)
    reported_norm = normalize(reported)
    aliases = {
        "share inflation rounding": ("share inflation", "donation", "round"),
        "accounting desync": ("accounting", "desync"),
        "fee on transfer accounting": ("fee", "transfer", "accounting"),
        "signature replay": ("signature", "replay"),
        "price manipulation": ("price", "oracle", "manipulation"),
        "access control": ("access", "control", "guard", "authorization"),
        "unvalidated cpi": ("cpi", "program", "validation"),
        "missing signer check": ("signer",),
        "missing access control": ("access", "control", "mint"),
    }
    for alias, terms in aliases.items():
        if expected_norm == alias:
            return all(term in reported_norm for term in terms)
    return expected_norm in reported_norm or reported_norm in expected_norm


def score(truth: list[dict], predictions: list[dict]) -> dict:
    truth_by_id = {str(item["fixture"]): item for item in truth}
    prediction_by_id = {str(item["fixture"]): item for item in predictions}
    counts = Counter(TP=0, TN=0, FP=0, FN=0)
    rows = []
    for fixture, expected in sorted(truth_by_id.items()):
        prediction = prediction_by_id.get(fixture, {})
        verdict = normalize(str(prediction.get("verdict", prediction.get("status", ""))))
        positive = verdict in POSITIVE_VERDICTS or verdict.startswith("valid ") or "confirmed" in verdict
        expected_class = str(expected.get("bug_class", expected.get("expected", "")))
        benign = expected_class in {"", "benign", "none", "[]", "negative"}
        root = str(prediction.get("root_cause", prediction.get("finding", "")))
        correct_class = not positive or is_correct_root_cause(expected_class, root)
        if benign:
            outcome = "FP" if positive else "TN"
        elif positive and correct_class:
            outcome = "TP"
        else:
            outcome = "FN"
            if positive and not correct_class:
                counts["FP"] += 1
        counts[outcome] += 1
        rows.append({"fixture": fixture, "expected": expected_class or "benign", "reported": root, "verdict": verdict or "missing", "outcome": outcome})
    predicted_unknown = sorted(set(prediction_by_id) - set(truth_by_id))
    for fixture in predicted_unknown:
        counts["FP"] += 1
        rows.append({"fixture": fixture, "expected": "unknown fixture", "reported": str(prediction_by_id[fixture]), "verdict": "unknown", "outcome": "FP"})
    precision = counts["TP"] / (counts["TP"] + counts["FP"]) if counts["TP"] + counts["FP"] else 0.0
    recall = counts["TP"] / (counts["TP"] + counts["FN"]) if counts["TP"] + counts["FN"] else 0.0
    return {"counts": dict(counts), "precision": precision, "recall": recall, "rows": rows}


def main() -> int:
    parser = argparse.ArgumentParser(description="Score AuditSharingan benchmark predictions.")
    parser.add_argument("--ground-truth", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--output", type=Path, help="Optional JSON score output")
    args = parser.parse_args()
    try:
        result = score(load_json(args.ground_truth), load_json(args.predictions))
    except (OSError, json.JSONDecodeError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    print(json.dumps({key: value for key, value in result.items() if key != "rows"}, indent=2))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
