---
name: formal-verifier
description: Bounded symbolic property verification and formal invariant synthesis using Halmos and Kontrol. Loaded when the target needs solver-assisted reasoning.
---

# Formal Verifier (Halmos & Symbolic Invariant Testing)

Provides solver-assisted exploration of explicitly modeled paths. Halmos and Kontrol are bounded tools: a passing run proves only the encoded property under the recorded assumptions, and a timeout/unknown result is not a proof of safety.

## 1. When to Deploy Symbolic Verification

- Critical mathematical operations: `mulDiv`, share conversions, dynamic interest rates, debt compounding.
- Roundtrip conservation properties: `convertAssets(convertShares(x)) <= x`.
- State machines with strict authorization guarantees.

## 2. Halmos Cheatcodes & Setup

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "halmos-cheatcodes/SymTest.sol";

contract VaultSymbolicTest is Test, SymTest {
    // Symbolic Variables
    // uint256 a = svm.createUint256("assets");
    // svm.assume(a > 0 && a < type(uint128).max);
}
```

## 3. Core Symbolic Invariant Templates

1. **No-Free-Minting Invariant:**
   $\forall a > 0 : \text{deposit}(a) \implies \text{sharesMinted} > 0$.
2. **Monotonic Value Invariant:**
   $\forall a, b : a \ge b \implies \text{convertToShares}(a) \ge \text{convertToShares}(b)$.
3. **Roundtrip Solvency Invariant:**
   $\forall a : \text{redeem}(\text{deposit}(a)) \le a$.

## 4. Execution & Violation Triage

Run with the installed tool's version-specific command, for example:
```bash
halmos --function check_invariant_*
```

Record tool version, command, assumptions, explored bounds, and whether the
result is `PASS`, `FAIL`, or `UNKNOWN`. If Halmos finds a counterexample, retain
the concrete assignment and turn it into an executable Foundry PoC in Phase 6.
