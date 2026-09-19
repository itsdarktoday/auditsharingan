#!/usr/bin/env python3
"""Validate the machine-readable contract of an AuditSharingan run."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


REQUIRED_MANIFEST_KEYS = {
    "schema_version", "engine", "engine_version", "generated_at", "target",
    "output_dir", "mode", "platforms", "scope", "steps", "overall_status",
    "guarantees",
}
REQUIRED_STEP_KEYS = {"name", "command", "status", "duration_seconds", "stdout_file", "stderr_file"}


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    manifest_path = path / "run-manifest.json"
    if not manifest_path.exists():
        return [f"missing {manifest_path}"]
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"invalid manifest: {exc}"]
    missing = REQUIRED_MANIFEST_KEYS - set(manifest)
    errors.extend(f"manifest missing key: {key}" for key in sorted(missing))
    if manifest.get("engine") != "AuditSharingan":
        errors.append("manifest engine is not AuditSharingan")
    if manifest.get("mode") not in {"quick", "standard", "deep"}:
        errors.append("manifest mode is invalid")
    if not isinstance(manifest.get("steps"), list) or not manifest["steps"]:
        errors.append("manifest must contain at least one step")
    else:
        names: set[str] = set()
        for step in manifest["steps"]:
            missing_step = REQUIRED_STEP_KEYS - set(step)
            errors.extend(f"step missing key: {key}" for key in sorted(missing_step))
            name = step.get("name")
            if name in names:
                errors.append(f"duplicate step: {name}")
            names.add(name)
            if step.get("status") not in {"ok", "skipped", "failed"}:
                errors.append(f"invalid status for step {name}")
            for log_key in ("stdout_file", "stderr_file"):
                log = Path(step.get(log_key, ""))
                if not log.exists():
                    errors.append(f"missing {log_key} for step {name}: {log}")
    if manifest.get("overall_status") == "completed" and any(step.get("status") != "ok" for step in manifest.get("steps", [])):
        errors.append("completed manifest contains a non-ok step")
    guarantees = manifest.get("guarantees", {})
    if guarantees.get("leads_are_not_findings") is not True:
        errors.append("lead/finding separation guarantee is absent")
    if not (path / "scope.json").exists():
        errors.append("missing scope.json")
    if not (path / "leads.md").exists():
        errors.append("missing leads.md")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an AuditSharingan artifact directory.")
    parser.add_argument("output_dir")
    args = parser.parse_args()
    errors = validate(Path(args.output_dir).expanduser().resolve())
    if errors:
        print("Artifact validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Artifact validation passed: manifest, logs, scope, and lead register are present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
