#!/usr/bin/env python3
"""Run available static analyzers with reproducible, shell-free commands.

Unavailable tools are recorded as capability gaps. Raw output is retained so
an auditor can reproduce or challenge every candidate seed.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def run_command(command: list[str], cwd: Path, timeout: int = 300) -> tuple[int, str, str]:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired as exc:
        return 124, exc.stdout or "", (exc.stderr or "") + f"\nTimed out after {timeout}s\n"
    except OSError as exc:
        return 127, "", str(exc)


def save_result(out_dir: Path, name: str, command: list[str], status: str, code: int | None, stdout: str, stderr: str, reason: str = "") -> dict:
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    (raw_dir / f"{name}.stdout.log").write_text(stdout, encoding="utf-8")
    (raw_dir / f"{name}.stderr.log").write_text(stderr, encoding="utf-8")
    return {"name": name, "command": command, "status": status, "returncode": code, "reason": reason}


def parse_slither(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [
        {
            "tool": "slither",
            "check": detector.get("check", "unknown"),
            "impact": detector.get("impact", "Informational"),
            "description": detector.get("description", "").strip(),
            "locations": detector.get("elements", []),
        }
        for detector in data.get("results", {}).get("detectors", [])
    ]


def parse_aderyn(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    findings = []
    for bucket, impact in (("high_issues", "High"), ("medium_issues", "Medium"), ("low_issues", "Low")):
        for issue in data.get(bucket, {}).get("issues", []):
            findings.append({
                "tool": "aderyn",
                "check": issue.get("title", "unknown"),
                "impact": impact,
                "description": issue.get("description", "").strip(),
                "locations": issue.get("instances", []),
            })
    return findings


def parse_semgrep(path: Path) -> list[dict]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [
        {
            "tool": "semgrep",
            "check": result.get("check_id", "unknown"),
            "impact": result.get("extra", {}).get("severity", "WARNING"),
            "description": result.get("extra", {}).get("message", "").strip(),
            "locations": [result.get("start", {}), result.get("end", {})],
        }
        for result in data.get("results", [])
    ]


def run_tool(name: str, executable: str, command: list[str], target: Path, out_dir: Path) -> dict:
    if shutil.which(executable) is None:
        return save_result(out_dir, name, command, "unavailable", None, "", f"{executable} not installed\n", f"{executable} not installed")
    code, stdout, stderr = run_command(command, target)
    status = "ok" if code == 0 else "completed_with_findings_or_warnings"
    return save_result(out_dir, name, command, status, code, stdout, stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description="Aggregate available static analyzers for an AuditSharingan run.")
    parser.add_argument("target_dir")
    parser.add_argument("--output-dir", default="AuditSharingan-audit")
    args = parser.parse_args()
    target = Path(args.target_dir).expanduser().resolve()
    out_dir = Path(args.output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    findings: list[dict] = []
    slither_json = raw_dir / "slither.json"
    results.append(run_tool("slither", "slither", ["slither", ".", "--json", str(slither_json), "--filter-paths", "test|tests|mocks|lib|out|cache"], target, out_dir))
    findings.extend(parse_slither(slither_json))

    aderyn_json = raw_dir / "aderyn.json"
    results.append(run_tool("aderyn", "aderyn", ["aderyn", "--output", str(aderyn_json)], target, out_dir))
    findings.extend(parse_aderyn(aderyn_json))

    semgrep_json = raw_dir / "semgrep.json"
    config = Path(__file__).resolve().parent.parent / "tools" / "semgrep.yml"
    results.append(run_tool("semgrep", "semgrep", ["semgrep", "--config", str(config), "--json", "--no-git-ignore", "."], target, out_dir))
    semgrep_stdout = raw_dir / "semgrep.stdout.log"
    if semgrep_stdout.exists():
        semgrep_json.write_text(semgrep_stdout.read_text(encoding="utf-8", errors="replace"), encoding="utf-8")
    findings.extend(parse_semgrep(semgrep_json))

    (out_dir / "static_findings.json").write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")
    with (out_dir / "static_leads.md").open("w", encoding="utf-8") as handle:
        handle.write("# Static-analysis candidate seeds\n\n")
        handle.write("Raw tool output and capability status are in `raw/` and `static_tools.json`. These are leads, not validated findings.\n\n")
        if findings:
            handle.write("| # | Tool | Severity | Detector | Description |\n|---:|---|---|---|---|\n")
            for index, item in enumerate(findings, 1):
                description = " ".join(item["description"].split()).replace("|", "\\|")
                handle.write(f"| {index} | {item['tool']} | {item['impact']} | {item['check']} | {description[:300]} |\n")
        else:
            handle.write("No parseable findings were returned by the available analyzers. This is not evidence that the target is safe.\n")
    (out_dir / "static_tools.json").write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    unavailable = sum(item["status"] == "unavailable" for item in results)
    print(f"Static analysis recorded {len(findings)} candidate seed(s); {unavailable} tool(s) unavailable.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
