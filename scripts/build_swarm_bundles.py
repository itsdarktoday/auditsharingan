#!/usr/bin/env python3
"""Build deterministic prompt packages for the manual AuditSharingan swarm.

The script prepares dispatch artifacts; it does not pretend to invoke
subagents. Bundles are lightweight by default and reference a hashed source
manifest. Use --embed-source when a host runtime cannot grant agents access to
the target directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


AGENT_SPECIALTIES = {
    "agent-01-math-precision": "Fixed-point arithmetic, rounding direction, zero-share mints, decimal shifts, and conservation equations.",
    "agent-02-reentrancy-transient": "CEI, read-only reentrancy, token hooks, callbacks, and transient-storage lifetime.",
    "agent-03-access-control": "Authorization, initialization, ownership transitions, capability leaks, and trust boundaries.",
    "agent-04-economic-mev": "Flash-loan manipulation, sandwichability, liquidity, incentives, and executable profit.",
    "agent-05-oracle-pricing": "Staleness, heartbeat, sequencer downtime, decimals, and multi-source price disagreement.",
    "agent-06-lending-cdp": "Health factors, liquidation math, bad debt, toxic collateral, and liveness.",
    "agent-07-amm-hooks": "Hook callbacks, deltas, tick boundaries, invariant drift, and pool accounting.",
    "agent-08-vault-inflation": "ERC-4626 donation/inflation, share conversion, yield timing, and first-depositor risk.",
    "agent-09-governance-voting": "Voting snapshots, flash power, proposal races, timelocks, and execution authority.",
    "agent-10-signatures-permits": "Domain separation, replay, nonce scope, malleability, and permit denial of service.",
    "agent-11-upgradeability-proxies": "Initialization, proxy slots, upgrade authorization, storage compatibility, and rollback.",
    "agent-12-dos-griefing": "Unbounded work, push payments, gas forwarding, queue starvation, and dust griefing.",
    "agent-13-crosschain-bridges": "Replay, finality, message ordering, proof validation, lock/mint parity, and destination gas.",
    "agent-14-assembly-lowlevel": "Memory safety, dirty bits, returndata, calldata slicing, and unchecked low-level assumptions.",
    "agent-15-gap-hunter-numerical": "Seams between rounding, accounting, and economic incentives across contracts.",
    "agent-16-gap-hunter-trust": "Seams between permissions, callbacks, delegated calls, and intermediate state.",
    "agent-17-gap-hunter-flow": "Seams between asynchronous settlement, queues, and multi-transaction state machines.",
    "agent-18-skeptic-adversary": "Attempt to disprove every candidate with exact guards, assumptions, and counterexamples.",
}

EXTENSIONS = {".sol", ".vy", ".rs", ".move", ".circom", ".nr", ".cairo"}
EXCLUDED = {".git", "node_modules", "vendor", "lib", "out", "cache", "artifacts", "build", "dist", "script", "scripts", "migrations", "deploy", "test", "tests", "mocks", "mock"}


def source_files(target: Path, output: Path) -> list[Path]:
    files = []
    for path in target.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in EXTENSIONS:
            continue
        if set(path.relative_to(target).parts[:-1]).intersection(EXCLUDED):
            continue
        try:
            path.resolve().relative_to(output.resolve())
            continue
        except ValueError:
            pass
        if path.name.endswith(".t.sol") or path.name.lower().startswith(("test", "mock")):
            continue
        files.append(path)
    return sorted(files)


def file_record(path: Path, target: Path) -> dict:
    data = path.read_bytes()
    return {
        "path": str(path.relative_to(target)),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "lines": data.count(b"\n") + (1 if data and not data.endswith(b"\n") else 0),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build deterministic AuditSharingan swarm dispatch bundles.")
    parser.add_argument("target")
    parser.add_argument("--output-dir", default="AuditSharingan-audit/bundles")
    parser.add_argument("--embed-source", action="store_true", help="Embed source in every bundle; increases artifact size")
    args = parser.parse_args()
    target = Path(args.target).expanduser().resolve()
    output = Path(args.output_dir).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    files = source_files(target, output)
    records = [file_record(path, target) for path in files]
    manifest = {"schema_version": "1.0", "engine": "AuditSharingan", "target": str(target), "source_files": records, "embedded_source": args.embed_source, "agent_count": len(AGENT_SPECIALTIES)}
    (output / "source-manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    source_text = ""
    if args.embed_source:
        chunks = ["# In-scope source code\n"]
        for path in files:
            chunks.append(f"\n## File: `{path.relative_to(target)}`\n\n```{path.suffix.lstrip('.')}`\n{path.read_text(encoding='utf-8', errors='replace')}\n```\n")
        source_text = "\n".join(chunks)
        (output / "source.md").write_text(source_text, encoding="utf-8")

    dispatch = []
    for agent_id, specialty in AGENT_SPECIALTIES.items():
        bundle = output / f"{agent_id}-bundle.md"
        content = [
            f"# AuditSharingan dispatch bundle: {agent_id}",
            "",
            "## Dispatch contract",
            "Produce candidates only when you can state the exact location, reachable attacker, broken invariant, and victim impact. Otherwise label the item LEAD.",
            "Do not upgrade another agent's lead without independently checking the source and preserving the evidence receipt.",
            "",
            "## Specialty",
            specialty,
            "",
            "## Source provenance",
            f"Target: `{target}`",
            "Source files and SHA-256 hashes are in `source-manifest.json`. Read the target files directly when the host runtime provides access.",
        ]
        if args.embed_source:
            content.extend(["", "## Embedded source", source_text])
        bundle.write_text("\n".join(content) + "\n", encoding="utf-8")
        dispatch.append({"agent": agent_id, "specialty": specialty, "bundle": str(bundle), "source_manifest": str(output / "source-manifest.json")})
    (output / "dispatch-manifest.json").write_text(json.dumps({"schema_version": "1.0", "engine": "AuditSharingan", "dispatches": dispatch, "execution": "prepared-only"}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(dispatch)} dispatch bundles for {len(files)} source files in {output}.")
    print("Execution: prepared-only; invoke agents through the host runtime and retain their outputs for judging.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
