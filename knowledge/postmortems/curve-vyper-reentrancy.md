# Curve Vyper incident — compiler and read-only reentrancy pattern

- **Archetype:** AMM / pool valuation
- **Root cause pattern:** affected Vyper compiler versions generated incorrect non-reentrancy behavior for some lock usage, exposing pool state during an external callback.
- **Invariant:** no callback or external reader may observe a pool valuation between coupled state updates.

## Audit trigger

Pin the compiler and EVM target, inspect generated behavior for every lock identifier, and trace raw ETH/token callbacks into view functions used by other protocols. A source-level guard is not evidence if the compiler/toolchain is outside the affected assumptions.

## False-positive boundary

The issue requires an affected compiler/build configuration and an attacker-controlled callback or downstream reader. Confirm both before assigning severity.

## Defensive test

Compile with the deployed compiler, test every callback path, and compare pre/post-update values from a separate reader contract during the callback.

