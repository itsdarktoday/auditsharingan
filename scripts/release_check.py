#!/usr/bin/env python3
"""Run the local release gate for AuditSharingan.

This gate checks package integrity and regression behavior; it does not claim
that the audit methodology finds every novel vulnerability.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


LEGACY_TOKENS = (
    "ultimate" + "-web3-security",
    "Ultimate" + " Web3 Security",
    "ultimate" + " web3 security",
    "ultimate" + "-audit",
)
EXCLUDED_DIRS = {".git", "out", "cache", "node_modules", "artifacts", "build", "dist", "sources"}


def files_to_scan(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or set(path.relative_to(root).parts[:-1]).intersection(EXCLUDED_DIRS):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".pyc"}:
            continue
        yield path


def run(command: list[str], cwd: Path, *, capture: bool = True) -> tuple[int, str]:
    result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE if capture else None, stderr=subprocess.STDOUT if capture else None, text=True, encoding="utf-8", errors="replace", check=False)
    return result.returncode, result.stdout or ""


def check_skill(root: Path) -> list[str]:
    errors = []
    skill_file = root / "SKILL.md"
    if not skill_file.is_file():
        errors.append("SKILL.md is missing")
        return errors
    try:
        frontmatter = skill_file.read_text(encoding="utf-8").split("---", 2)
    except OSError as exc:
        return [f"could not read SKILL.md: {exc}"]
    if len(frontmatter) != 3 or not frontmatter[0].strip() == "":
        errors.append("SKILL.md must start with YAML frontmatter")
    else:
        metadata = frontmatter[1]
        if "name:" not in metadata:
            errors.append("SKILL.md frontmatter is missing name")
        if "description:" not in metadata:
            errors.append("SKILL.md frontmatter is missing description")

    candidates: list[Path] = []
    configured = os.environ.get("AUDITSHARINGAN_SKILL_VALIDATOR")
    if configured:
        candidates.append(Path(configured).expanduser())
    codex_home = os.environ.get("CODEX_HOME")
    if codex_home:
        candidates.append(Path(codex_home).expanduser() / "skills/.system/skill-creator/scripts/quick_validate.py")
    candidates.append(Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py")
    validator = next((candidate for candidate in candidates if candidate.is_file()), None)
    if validator is not None:
        code, output = run([sys.executable, str(validator), str(root)], root)
        if code:
            errors.append(f"skill metadata validation failed: {output.strip()}")
    return errors


def check_brand(root: Path) -> list[str]:
    errors = []
    for path in files_to_scan(root):
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for token in LEGACY_TOKENS:
            if token in content:
                errors.append(f"legacy brand token {token!r} remains in {path.relative_to(root)}")
    return errors


def check_python(root: Path) -> list[str]:
    scripts = [
        path
        for path in root.rglob("*.py")
        if not set(path.relative_to(root).parts[:-1]).intersection(EXCLUDED_DIRS)
        and "evals/corpus" not in str(path.relative_to(root))
    ]
    if not scripts:
        return ["no Python files found"]
    errors = []
    for path in scripts:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path.relative_to(root)))
        except (OSError, SyntaxError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return ["Python syntax check failed:\n" + "\n".join(errors)] if errors else []


def check_schemas(root: Path) -> list[str]:
    schema_dir = root / "schemas"
    schema_files = sorted(schema_dir.glob("*.json"))
    if not schema_files:
        return ["no JSON schemas found"]
    errors = []
    for path in schema_files:
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return ["schema validation failed:\n" + "\n".join(errors)] if errors else []


def check_smoke(root: Path) -> list[str]:
    errors = []
    if not (root / "evals/corpus").is_dir():
        return ["WARN: evals/corpus is unavailable; deterministic smoke test not run"]
    with tempfile.TemporaryDirectory(prefix="auditsharingan-release-") as temporary:
        output_dir = Path(temporary) / "artifacts"
        code, output = run([sys.executable, "-B", "scripts/auditsharingan.py", "evals/corpus", "--quick", "--output-dir", str(output_dir)], root)
        if code:
            errors.append(f"quick engine smoke failed:\n{output}")
            return errors
        code, output = run([sys.executable, "scripts/validate_artifacts.py", str(output_dir)], root)
        if code:
            errors.append(f"artifact validation failed:\n{output}")
        try:
            manifest = json.loads((output_dir / "run-manifest.json").read_text(encoding="utf-8"))
            if manifest.get("overall_status") == "failed":
                errors.append("smoke manifest is failed")
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"smoke manifest unreadable: {exc}")
    return errors


def check_foundry(root: Path) -> list[str]:
    if not (root / "evals/corpus").is_dir():
        return ["WARN: evals/corpus is unavailable; Foundry regression gate not run"]
    if shutil.which("forge") is None:
        return ["WARN: forge unavailable; Foundry regression gate not run"]
    with tempfile.TemporaryDirectory(prefix="auditsharingan-foundry-") as temporary:
        temporary_root = Path(temporary)
        code, output = run(
            [
                "forge",
                "test",
                "--root",
                "evals/corpus",
                "--out",
                str(temporary_root / "out"),
                "--cache-path",
                str(temporary_root / "cache"),
            ],
            root,
        )
    return [f"Foundry corpus tests failed:\n{output}"] if code else []


def check_unit_tests(root: Path) -> list[str]:
    code, output = run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"], root)
    return [f"unit tests failed:\n{output}"] if code else []


def main() -> int:
    parser = argparse.ArgumentParser(description="Run AuditSharingan release checks.")
    parser.add_argument("--skip-smoke", action="store_true")
    parser.add_argument("--skip-foundry", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parent.parent
    errors: list[str] = []
    checks = [
        ("skill metadata", check_skill),
        ("brand", check_brand),
        ("Python syntax", check_python),
        ("JSON schemas", check_schemas),
        ("unit tests", check_unit_tests),
    ]
    if not args.skip_smoke:
        checks.append(("engine smoke", check_smoke))
    if not args.skip_foundry:
        checks.append(("Foundry corpus", check_foundry))
    for name, check in checks:
        result = check(root)
        failures = [item for item in result if not item.startswith("WARN:")]
        warnings = [item.removeprefix("WARN:").strip() for item in result if item.startswith("WARN:")]
        if failures:
            print(f"[FAIL] {name}")
            errors.extend(failures)
        elif warnings:
            print(f"[WARN] {name}")
            for warning in warnings:
                print(f"- {warning}")
        else:
            print(f"[ OK ] {name}")
    if errors:
        print("\nRelease gate failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("\nRelease gate passed. This certifies package consistency, not protocol security.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
