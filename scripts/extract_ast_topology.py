#!/usr/bin/env python3
"""Extract best-effort EVM contract and storage topology without false zeros."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


def run(command: list[str], cwd: Path, timeout: int = 120) -> tuple[int, str, str]:
    try:
        result = subprocess.run(command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace", timeout=timeout, check=False)
        return result.returncode, result.stdout, result.stderr
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, "", str(exc)


def contract_names(target: Path) -> tuple[list[str], str]:
    if shutil.which("forge"):
        code, out, err = run(["forge", "build", "--names"], target)
        if code == 0:
            names = [line.strip() for line in out.splitlines() if re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", line.strip())]
            if names:
                return sorted(set(names)), "forge build --names"
        fallback_error = err.strip() or "forge build --names returned no contract names"
    else:
        fallback_error = "forge not installed"
    names: set[str] = set()
    for path in target.rglob("*.sol"):
        if any(part in {"test", "tests", "mocks", "mock", "lib", "out", "cache"} for part in path.parts):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        names.update(re.findall(r"\bcontract\s+([A-Za-z_][A-Za-z0-9_]*)", text))
        names.update(re.findall(r"\blibrary\s+([A-Za-z_][A-Za-z0-9_]*)", text))
    return sorted(names), f"source fallback ({fallback_error})"


def inspect_layout(name: str, target: Path) -> tuple[dict | None, str]:
    if not shutil.which("forge"):
        return None, "forge not installed"
    code, out, err = run(["forge", "inspect", name, "storageLayout", "--json"], target)
    if code != 0:
        return None, err.strip() or f"forge inspect exited {code}"
    try:
        return json.loads(out), ""
    except json.JSONDecodeError as exc:
        return None, f"invalid forge JSON: {exc}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Extract EVM contract and storage topology.")
    parser.add_argument("target_dir")
    parser.add_argument("--output-file", default="AuditSharingan-audit/topology.md")
    parser.add_argument("--json-output", default="")
    args = parser.parse_args()
    target = Path(args.target_dir).expanduser().resolve()
    output = Path(args.output_file).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    names, source = contract_names(target)
    records = []
    for name in names:
        layout, error = inspect_layout(name, target)
        records.append({"contract": name, "storage": layout.get("storage", []) if layout else [], "error": error})
    with output.open("w", encoding="utf-8") as handle:
        handle.write("# Protocol architecture and storage topology\n\n")
        handle.write(f"Contract discovery: `{source}`. Detected {len(names)} contract/library names.\n\n")
        if not names:
            handle.write("No EVM contracts were discovered. This is a capability/scope result, not a clean-security result.\n")
        for record in records:
            handle.write(f"## `{record['contract']}`\n\n")
            if record["error"]:
                handle.write(f"> Storage inspection unavailable: {record['error']}\n\n")
                continue
            storage = record["storage"]
            if not storage:
                handle.write("No storage variables reported.\n\n")
                continue
            handle.write("| Slot | Offset | Variable | Type |\n|---|---:|---|---|\n")
            for variable in storage:
                handle.write(f"| {variable.get('slot', '')} | {variable.get('offset', '')} | `{variable.get('label', '')}` | `{variable.get('type', '')}` |\n")
            handle.write("\n")
    if args.json_output:
        json_output = Path(args.json_output).expanduser().resolve()
        json_output.parent.mkdir(parents=True, exist_ok=True)
        json_output.write_text(json.dumps({"discovery": source, "contracts": records}, indent=2) + "\n", encoding="utf-8")
    print(f"Topology saved to {output}; {len(names)} contract/library names recorded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
