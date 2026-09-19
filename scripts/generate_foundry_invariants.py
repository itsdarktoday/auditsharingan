#!/usr/bin/env python3
"""Generate a compiling Foundry invariant harness.

The output is intentionally a harness, not a fabricated security proof. It
contains one configuration invariant and clearly marked integration points for
protocol-specific handlers and properties.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


TEMPLATE = """// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import \"forge-std/Test.sol\";
import \"forge-std/StdInvariant.sol\";

/// @title AuditSharingan Invariant Harness
/// @notice Generated harness. It is not security evidence until protocol-specific
///         handlers, state transitions, and properties are implemented.
contract AuditSharinganInvariantsTest is StdInvariant, Test {{
    address internal trackedTarget;

    // Ghost accounting variables: update these from a protocol handler.
    uint256 public ghostTotalDeposited;
    uint256 public ghostTotalWithdrawn;
    uint256 public ghostTotalClaimed;

    function setUp() public {{
        trackedTarget = {target_address};
        // This call is the StdInvariant target registration API. The variable
        // is deliberately named trackedTarget to avoid shadowing the method.
        targetContract(trackedTarget);
    }}

    /// @notice Configuration sanity check; this is not a protocol invariant.
    function invariant_target_is_configured() public view {{
        assertTrue(trackedTarget != address(0), \"target address is not configured\");
    }}

    // TODO(owner): connect real protocol actors and implement properties such as:
    // - total assets >= user liabilities after every handler action;
    // - withdrawals never exceed the caller's entitled balance;
    // - share conversion is monotone and never rounds a non-zero deposit to zero.
}}
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a compile-safe Foundry invariant harness.")
    parser.add_argument("target_dir", help="Target repository (used for provenance only)")
    parser.add_argument("--output-file", default="AuditSharingan-audit/test/AuditInvariants.t.sol")
    parser.add_argument("--target-address", default="0x0000000000000000000000000000000000001234")
    args = parser.parse_args()
    if not re.fullmatch(r"0x[0-9a-fA-F]{40}", args.target_address):
        parser.error("--target-address must be a 20-byte hexadecimal address")
    output = Path(args.output_file).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(TEMPLATE.format(target_address=args.target_address), encoding="utf-8")
    print(f"Compile-safe invariant harness generated at {output}")
    print("Status: scaffold only; protocol properties still require auditor implementation.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
