#!/usr/bin/env python3
"""Release-grade AuditSharingan execution engine.

The engine is deliberately conservative: it inventories the target, runs only
declared subprocesses with argument lists (never a shell), records every
result, and emits a manifest that makes missing tools and failed stages visible.
It is an orchestration layer, not a replacement for the manual reasoning
protocol in the core/ documents.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


ENGINE_VERSION = "1.0.0"
SOURCE_EXTENSIONS = {
    ".sol": "evm",
    ".vy": "evm",
    ".rs": "solana-or-rust",
    ".move": "move",
    ".circom": "zk",
    ".nr": "zk",
    ".cairo": "cairo",
}
EXCLUDED_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "vendor",
    "lib",
    "out",
    "cache",
    "artifacts",
    "build",
    "dist",
    "script",
    "scripts",
    "migrations",
    "deploy",
    "test",
    "tests",
    "mocks",
    "mock",
}


@dataclass
class StepResult:
    name: str
    command: list[str]
    status: str
    returncode: int | None
    duration_seconds: float
    stdout_file: str
    stderr_file: str
    reason: str = ""


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def is_excluded(path: Path, root: Path) -> bool:
    try:
        relative = path.relative_to(root)
    except ValueError:
        return True
    return bool(set(relative.parts[:-1]).intersection(EXCLUDED_DIRS))


def collect_sources(root: Path, output_dir: Path) -> list[Path]:
    sources: list[Path] = []
    output_dir = output_dir.resolve()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in SOURCE_EXTENSIONS:
            continue
        if is_excluded(path, root):
            continue
        try:
            path.resolve().relative_to(output_dir)
            continue
        except ValueError:
            pass
        if path.name.endswith(".t.sol") or path.name.lower().startswith(("test", "mock")):
            continue
        sources.append(path)
    return sorted(sources)


def count_sloc(path: Path) -> int:
    try:
        return sum(
            1
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines()
            if line.strip() and not line.lstrip().startswith(("//", "#", "/*", "*"))
        )
    except OSError:
        return 0


def detect_platforms(target: Path, sources: Iterable[Path]) -> list[str]:
    platforms = {SOURCE_EXTENSIONS[path.suffix.lower()] for path in sources}
    if (target / "foundry.toml").exists() or (target / "hardhat.config.js").exists() or (target / "hardhat.config.ts").exists():
        platforms.add("evm-toolchain")
    if (target / "Anchor.toml").exists() or (target / "Cargo.toml").exists():
        platforms.add("solana-toolchain")
    if (target / "Move.toml").exists():
        platforms.add("move-toolchain")
    return sorted(platforms)


def run_step(
    name: str,
    command: list[str],
    target: Path,
    output_dir: Path,
    timeout: int,
    *,
    optional: bool = False,
) -> StepResult:
    logs = output_dir / "logs"
    logs.mkdir(parents=True, exist_ok=True)
    stdout_path = logs / f"{name}.stdout.log"
    stderr_path = logs / f"{name}.stderr.log"
    started = time.monotonic()
    reason = ""
    status = "ok"
    returncode: int | None = None
    try:
        if shutil.which(command[0]) is None and command[0] != sys.executable:
            status = "skipped" if optional else "failed"
            reason = f"executable not found: {command[0]}"
            stdout_path.write_text("", encoding="utf-8")
            stderr_path.write_text(reason + "\n", encoding="utf-8")
        else:
            completed = subprocess.run(
                command,
                cwd=target,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout,
                check=False,
            )
            returncode = completed.returncode
            stdout_path.write_text(completed.stdout, encoding="utf-8")
            stderr_path.write_text(completed.stderr, encoding="utf-8")
            if returncode != 0:
                status = "failed"
                reason = f"process exited with code {returncode}"
    except subprocess.TimeoutExpired as exc:
        status = "failed"
        reason = f"timed out after {timeout}s"
        stdout_path.write_text(exc.stdout or "", encoding="utf-8")
        stderr_path.write_text((exc.stderr or "") + "\n" + reason + "\n", encoding="utf-8")
    except OSError as exc:
        status = "failed"
        reason = str(exc)
        stdout_path.write_text("", encoding="utf-8")
        stderr_path.write_text(reason + "\n", encoding="utf-8")

    if status == "failed" and optional:
        reason = f"optional step: {reason}"
    return StepResult(
        name=name,
        command=command,
        status=status,
        returncode=returncode,
        duration_seconds=round(time.monotonic() - started, 3),
        stdout_file=str(stdout_path),
        stderr_file=str(stderr_path),
        reason=reason,
    )


def script_command(script_dir: Path, script: str, *args: str) -> list[str]:
    return [sys.executable, str(script_dir / script), *args]


def build_steps(target: Path, output_dir: Path, mode: str, script_dir: Path, platforms: set[str]) -> list[tuple[str, list[str], bool]]:
    steps: list[tuple[str, list[str], bool]] = []
    evm = bool(platforms.intersection({"evm", "evm-toolchain"}))
    if evm:
        quick_steps = [
            ("topology", script_command(script_dir, "extract_ast_topology.py", str(target), "--output-file", str(output_dir / "topology.md"), "--json-output", str(output_dir / "topology.json")), True),
            ("compiler-hazards", script_command(script_dir, "compiler_hazard_scanner.py", str(target), "--output-file", str(output_dir / "compiler_hazards.md")), True),
            ("precision-truncation", script_command(script_dir, "precision_truncation_scanner.py", str(target), "--output-file", str(output_dir / "precision_truncation.md")), True),
            ("static-analysis", script_command(script_dir, "run_static_analysis.py", str(target), "--output-dir", str(output_dir)), True),
        ]
        full_steps = [
            ("topology", script_command(script_dir, "extract_ast_topology.py", str(target), "--output-file", str(output_dir / "topology.md"), "--json-output", str(output_dir / "topology.json")), True),
            ("differential-spec", script_command(script_dir, "differential_spec_miner.py", str(target), "--output-file", str(output_dir / "differential_spec_report.md")), True),
            ("l2-hazards", script_command(script_dir, "l2_hazard_scanner.py", str(target), "--output-file", str(output_dir / "l2_hazards.md")), True),
            ("multicall-hazards", script_command(script_dir, "multicall_msg_value_detector.py", str(target), "--output-file", str(output_dir / "multicall_hazards.md")), True),
            ("precision-truncation", script_command(script_dir, "precision_truncation_scanner.py", str(target), "--output-file", str(output_dir / "precision_truncation.md")), True),
            ("gas-griefing", script_command(script_dir, "eip150_gas_scanner.py", str(target), "--output-file", str(output_dir / "gas_griefing_hazards.md")), True),
            ("compiler-hazards", script_command(script_dir, "compiler_hazard_scanner.py", str(target), "--output-file", str(output_dir / "compiler_hazards.md")), True),
            ("natspec-intent", script_command(script_dir, "natspec_intent_miner.py", str(target), "--output-file", str(output_dir / "natspec_contradictions.md")), True),
            ("storage-packing", script_command(script_dir, "storage_packing_analyzer.py", str(target), "--output-file", str(output_dir / "storage_packing_hazards.md")), True),
            ("access-matrix", script_command(script_dir, "generate_access_matrix.py", str(target), "--output-file", str(output_dir / "access_matrix.md")), True),
            ("invariant-scaffold", script_command(script_dir, "generate_foundry_invariants.py", str(target), "--output-file", str(output_dir / "test" / "AuditInvariants.t.sol")), True),
            ("static-analysis", script_command(script_dir, "run_static_analysis.py", str(target), "--output-dir", str(output_dir)), True),
        ]
        steps.extend(quick_steps if mode == "quick" else full_steps)
    else:
        steps.append(("static-analysis", script_command(script_dir, "run_static_analysis.py", str(target), "--output-dir", str(output_dir)), True))

    if mode == "deep":
        steps.append(("swarm-bundles", script_command(script_dir, "build_swarm_bundles.py", str(target), "--output-dir", str(output_dir / "bundles")), True))
    return steps


def aggregate_leads(output_dir: Path, sources: list[Path], step_results: list[StepResult]) -> Path:
    reports = [
        ("Canonical specification", "differential_spec_report.md"),
        ("L2 execution hazards", "l2_hazards.md"),
        ("Payable multicall and msg.value", "multicall_hazards.md"),
        ("Precision and truncation", "precision_truncation.md"),
        ("EIP-150 gas griefing", "gas_griefing_hazards.md"),
        ("Compiler and Yul hazards", "compiler_hazards.md"),
        ("NatSpec intent contradictions", "natspec_contradictions.md"),
        ("Storage packing and pointers", "storage_packing_hazards.md"),
        ("Access-control matrix", "access_matrix.md"),
        ("Static-analysis seeds", "static_leads.md"),
    ]
    path = output_dir / "leads.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# AuditSharingan Lead Register\n\n")
        handle.write("This file contains machine-generated leads. A lead is not a validated finding until the core evidence chain is completed.\n\n")
        handle.write(f"- In-scope source files: {len(sources)}\n")
        handle.write(f"- Completed steps: {sum(result.status == 'ok' for result in step_results)}\n")
        handle.write(f"- Failed steps: {sum(result.status == 'failed' for result in step_results)}\n")
        handle.write(f"- Skipped steps: {sum(result.status == 'skipped' for result in step_results)}\n")
        for title, filename in reports:
            report = output_dir / filename
            if not report.exists():
                continue
            handle.write(f"\n---\n\n## {title}\n\n")
            handle.write(report.read_text(encoding="utf-8", errors="replace"))
            handle.write("\n")
    return path


def write_dispatch_plan(output_dir: Path, target: Path, platforms: list[str], mode: str) -> Path:
    path = output_dir / "dispatch-plan.md"
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# AuditSharingan chain dispatch plan\n\n")
        handle.write(f"Target: `{target}`\n\nMode: `{mode}`\n\n")
        handle.write("This plan records what the local engine can execute and what requires a chain-specific tool or manual review. A detected file extension is not proof that the corresponding build/deployment is in scope.\n\n")
        if not platforms:
            handle.write("- No supported source extension or toolchain marker detected. Resolve scope manually.\n")
        for platform in platforms:
            if platform in {"evm", "evm-toolchain"}:
                handle.write("- **EVM/Vyper:** deterministic topology, source-shape leads, optional Slither/Aderyn/Semgrep, and compile-safe Foundry scaffolds are available. Run protocol-specific tests separately.\n")
            elif platform in {"solana-or-rust", "solana-toolchain"}:
                handle.write("- **Solana/Rust:** load `skills/solana-audit/SKILL.md`; run `cargo check`/Anchor/Trident only when the target toolchain and lockfile are available. The EVM scanners do not cover this surface.\n")
            elif platform in {"move", "move-toolchain"}:
                handle.write("- **Move:** load `skills/move-audit/SKILL.md`; use the installed Sui/Aptos toolchain and inspect object/capability/PTB semantics manually.\n")
            elif platform == "zk":
                handle.write("- **ZK:** load `skills/zk-audit/SKILL.md`; compile circuits and generate malicious witnesses with the target's exact field and verifier configuration.\n")
            elif platform == "cairo":
                handle.write("- **Cairo:** no built-in Cairo detector is claimed; resolve compiler/version and load an appropriate Cairo-specific review method before reporting coverage.\n")
        handle.write("\n## Coverage boundary\n\n")
        handle.write("The run manifest is authoritative for executed stages. Unavailable chain tools, skipped builds, missing deployments, and unpinned external state remain limitations.\n")
    return path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the AuditSharingan evidence-oriented audit pipeline.")
    parser.add_argument("target", help="Target repository or source directory")
    parser.add_argument("--quick", action="store_const", dest="mode", const="quick", help="Run deterministic triage only")
    parser.add_argument("--standard", action="store_const", dest="mode", const="standard", help="Run the standard pipeline (default)")
    parser.add_argument("--deep", action="store_const", dest="mode", const="deep", help="Also build review bundles for the manual swarm")
    parser.add_argument("--output-dir", help="Audit artifact directory; defaults to TARGET/AuditSharingan-audit")
    parser.add_argument("--timeout", type=int, default=300, help="Per-step timeout in seconds (default: 300)")
    parser.add_argument("--version", action="version", version=ENGINE_VERSION)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    mode = args.mode or "standard"
    target = Path(args.target).expanduser().resolve()
    if not target.is_dir():
        print(f"error: target is not a directory: {target}", file=sys.stderr)
        return 2
    output_dir = Path(args.output_dir).expanduser().resolve() if args.output_dir else target / "AuditSharingan-audit"
    output_dir.mkdir(parents=True, exist_ok=True)
    script_dir = Path(__file__).resolve().parent
    sources = collect_sources(target, output_dir)
    platforms = detect_platforms(target, sources)
    scope = {
        "files": [str(path.relative_to(target)) for path in sources],
        "counts_by_extension": {ext: sum(path.suffix.lower() == ext for path in sources) for ext in sorted(SOURCE_EXTENSIONS)},
        "sloc": sum(count_sloc(path) for path in sources),
    }
    write_json(output_dir / "scope.json", {"generated_at": utc_now(), "target": str(target), "platforms": platforms, **scope})
    dispatch_plan = write_dispatch_plan(output_dir, target, platforms, mode)

    print("=" * 80)
    print(" AuditSharingan :: evidence-oriented audit engine")
    print("=" * 80)
    print(f"Target: {target}")
    print(f"Artifacts: {output_dir}")
    print(f"Mode: {mode} | Platforms: {', '.join(platforms) or 'none detected'}")
    print(f"Scope: {len(sources)} source files | {scope['sloc']:,} non-comment SLOC")

    results: list[StepResult] = []
    for name, command, optional in build_steps(target, output_dir, mode, script_dir, set(platforms)):
        print(f"[run] {name}")
        result = run_step(name, command, target, output_dir, args.timeout, optional=optional)
        results.append(result)
        marker = {"ok": "OK", "skipped": "SKIP", "failed": "FAIL"}[result.status]
        print(f"      {marker} ({result.duration_seconds:.1f}s){(': ' + result.reason) if result.reason else ''}")

    leads = aggregate_leads(output_dir, sources, results)
    failed = [result for result in results if result.status == "failed"]
    skipped = [result for result in results if result.status == "skipped"]
    overall = "failed" if failed else ("completed_with_warnings" if skipped else "completed")
    manifest = {
        "schema_version": "1.0",
        "engine": "AuditSharingan",
        "engine_version": ENGINE_VERSION,
        "generated_at": utc_now(),
        "target": str(target),
        "output_dir": str(output_dir),
        "mode": mode,
        "platforms": platforms,
        "scope": scope,
        "steps": [asdict(result) for result in results],
        "overall_status": overall,
        "lead_register": str(leads),
        "dispatch_plan": str(dispatch_plan),
        "guarantees": {
            "source_files_unchanged_by_engine": True,
            "failed_steps_are_visible": True,
            "leads_are_not_findings": True,
            "manual_evidence_chain_required": True,
        },
    }
    write_json(output_dir / "run-manifest.json", manifest)
    if mode in {"standard", "deep"}:
        print("[run] artifact-validation")
        validation = run_step(
            "artifact-validation",
            script_command(script_dir, "validate_artifacts.py", str(output_dir)),
            target,
            output_dir,
            args.timeout,
            optional=False,
        )
        results.append(validation)
        failed = [result for result in results if result.status == "failed"]
        skipped = [result for result in results if result.status == "skipped"]
        overall = "failed" if failed else ("completed_with_warnings" if skipped else "completed")
        manifest["steps"] = [asdict(result) for result in results]
        manifest["overall_status"] = overall
        write_json(output_dir / "run-manifest.json", manifest)
        marker = {"ok": "OK", "skipped": "SKIP", "failed": "FAIL"}[validation.status]
        print(f"      {marker} ({validation.duration_seconds:.1f}s){(': ' + validation.reason) if validation.reason else ''}")
    print(f"Manifest: {output_dir / 'run-manifest.json'}")
    print(f"Lead register: {leads}")
    if failed:
        print(f"Pipeline finished with {len(failed)} failed step(s); inspect logs before relying on results.", file=sys.stderr)
        return 1
    if skipped:
        print(f"Pipeline completed with {len(skipped)} skipped step(s); capability gaps are recorded in the manifest.")
    else:
        print("Pipeline completed; all declared steps succeeded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
