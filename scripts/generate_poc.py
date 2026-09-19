#!/usr/bin/env python3
"""Generate a compile-safe, explicitly incomplete Foundry PoC scaffold."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


POC_TEMPLATE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import \"forge-std/Test.sol\";

/// @title AuditSharingan PoC Scaffold: {finding_slug}
/// @notice This test is skipped until the auditor supplies target setup,
///         attacker actions, and an impact assertion. A scaffold is not proof.
contract Exploit_{finding_slug} is Test {{
    address internal attacker = makeAddr(\"attacker\");
    address internal victim = makeAddr(\"victim\");

    function setUp() public {{
        {fork_setup}
        // TODO: deploy mocks or attach to the exact target deployment.
    }}

    function test_exploit_{finding_slug}() public {{
        vm.skip(true);
        // TODO: record the pre-state and execute the complete attacker path.
        // TODO: assert the broken invariant and quantify victim loss/profit.
    }}
}}
"""


def safe_slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]", "_", value)
    slug = re.sub(r"_+", "_", slug).strip("_") or "finding"
    if slug[0].isdigit():
        slug = "finding_" + slug
    return slug


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a compile-safe Foundry PoC scaffold.")
    parser.add_argument("slug", help="Unique finding slug")
    parser.add_argument("--output-dir", default="AuditSharingan-audit/poc")
    parser.add_argument("--fork-url", default="")
    parser.add_argument("--block-number", default="0")
    args = parser.parse_args()
    if args.fork_url and not args.block_number.isdigit():
        parser.error("--block-number must be an integer")
    slug = safe_slug(args.slug)
    out_dir = Path(args.output_dir).expanduser().resolve() / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    fork_setup = ""
    if args.fork_url:
        fork_setup = f"vm.createSelectFork({json.dumps(args.fork_url)}, {args.block_number});"
    else:
        fork_setup = "// Standalone unit-test setup"
    code = POC_TEMPLATE.format(finding_slug=slug, fork_setup=fork_setup)
    test_file = out_dir / "Exploit.t.sol"
    test_file.write_text(code, encoding="utf-8")
    readme = out_dir / "README.md"
    command = f"forge test --match-test test_exploit_{slug} -vvvv"
    if args.fork_url:
        command += f" --fork-url {args.fork_url} --fork-block-number {args.block_number}"
    readme.write_text(
        f"# PoC scaffold: {args.slug}\n\n"
        "This generated file is deliberately skipped. Implement and review the setup, attacker path, broken invariant, and quantified impact before treating it as evidence.\n\n"
        f"```bash\n{command}\n```\n",
        encoding="utf-8",
    )
    print(f"Compile-safe PoC scaffold generated at {test_file}")
    print("Status: skipped scaffold; it is not an exploit reproduction until completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
