#!/usr/bin/env python3
"""Context-aware compiler and low-level-code lead scanner.

Compiler warnings depend on the exact resolved compiler, optimizer, EVM target,
and deployment chain. This script records review candidates and does not assign
High severity from a pragma string alone.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


EXACT_HAZARDS = [
    (r"pragma\s+solidity\s*(?:=|\s)\s*0\.8\.15\s*;", "Solidity 0.8.15 exact pin", "Review the resolved compiler and the affected bytes-to-storage behavior.", "REVIEW"),
    (r"pragma\s+solidity\s*(?:=|\s)\s*0\.8\.(?:13|14)\s*;", "Solidity 0.8.13/0.8.14 exact pin", "Review the resolved compiler and optimizer behavior for the deployed bytecode.", "REVIEW"),
]


def configured_evm_version(target: Path) -> str:
    for config in (target / "foundry.toml", target / "hardhat.config.js", target / "hardhat.config.ts"):
        if not config.exists():
            continue
        text = config.read_text(encoding="utf-8", errors="ignore")
        match = re.search(r"(?:evm_version|evmVersion)\s*[=:]\s*[\"']?([A-Za-z0-9_-]+)", text)
        if match:
            return match.group(1).lower()
    return "unspecified"


def scan(target: Path, chain: str) -> list[dict]:
    findings = []
    evm_version = configured_evm_version(target)
    for source in target.rglob("*.sol"):
        if not source.is_file() or any(part in {"test", "tests", "mocks", "mock", "lib", "node_modules", "out", "cache", "artifacts", "build"} for part in source.parts):
            continue
        content = source.read_text(encoding="utf-8", errors="ignore")
        for pattern, title, remediation, severity in EXACT_HAZARDS:
            if re.search(pattern, content, re.IGNORECASE):
                findings.append({"file": str(source.relative_to(target)), "title": title, "severity": severity, "description": "Exact compiler pins can be affected, but the resolved build and bytecode must be verified.", "remediation": remediation})
        assembly_count = len(re.findall(r"assembly\s*\{", content))
        if assembly_count:
            findings.append({"file": str(source.relative_to(target)), "title": "Inline assembly requires memory-safety review", "severity": "REVIEW", "description": f"Found {assembly_count} unannotated assembly block(s); safety depends on memory discipline and the optimizer configuration.", "remediation": "Review memory writes, free-memory pointer handling, optimizer settings, and annotate only after proving the memory-safe contract."})
        if re.search(r"pragma\s+solidity\s+[^;]*0\.8\.20", content, re.IGNORECASE) and chain.lower() in {"arbitrum", "zksync", "legacy-l2"} and evm_version not in {"paris", "berlin", "london"}:
            findings.append({"file": str(source.relative_to(target)), "title": "PUSH0 deployment compatibility requires verification", "severity": "REVIEW", "description": f"The target chain is declared as {chain}, while the config EVM target is {evm_version}; verify deployed bytecode compatibility rather than inferring a vulnerability from pragma alone.", "remediation": "Pin compiler and EVM target to the deployment chain, compile the exact artifact, and test deployment/execution on that chain."})
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan compiler, optimizer, and assembly hazards as review leads.")
    parser.add_argument("target_dir")
    parser.add_argument("--output-file", default="AuditSharingan-audit/compiler_hazards.md")
    parser.add_argument("--target-chain", default="unspecified", help="Deployment chain; required for chain-specific compatibility checks")
    args = parser.parse_args()
    target = Path(args.target_dir).expanduser().resolve()
    output = Path(args.output_file).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    findings = scan(target, args.target_chain)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("# Compiler, optimizer, and low-level review leads\n\n")
        handle.write(f"Deployment chain: `{args.target_chain}`. Resolved EVM config: `{configured_evm_version(target)}`.\n\n")
        handle.write("These are review leads. Confirm the resolved compiler, optimizer, bytecode, and deployment environment before judging impact.\n\n")
        if not findings:
            handle.write("No configured compiler review leads were detected.\n")
        else:
            handle.write("| File | Status | Lead | Why it needs review | Next check |\n|---|---|---|---|---|\n")
            for item in findings:
                handle.write(f"| `{item['file']}` | {item['severity']} | {item['title']} | {item['description']} | {item['remediation']} |\n")
    print(f"Compiler/low-level review scan saved to {output}; {len(findings)} lead(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
