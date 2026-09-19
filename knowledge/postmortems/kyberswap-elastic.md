# KyberSwap Elastic — tick-crossing math pattern

- **Archetype:** concentrated-liquidity AMM
- **Root cause pattern:** liquidity and price accounting around a tick boundary used an inconsistent update/rounding sequence.
- **Invariant:** each swap conserves input/output value under the configured fee and never credits liquidity that was not present.

## Audit trigger

Compare the exact rounding direction on both sides of a tick crossing. Check partial crossings, zero-liquidity ranges, repeated back-and-forth swaps, and state updates that recompute a delta already applied.

## Attack shape

An attacker supplies a carefully chosen position and swap sequence that repeatedly crosses a boundary. If the pool double-counts a liquidity delta or rounds the price in the wrong direction, the attacker can receive more output than the invariant permits.

## False-positive boundary

A suspicious rounding operation is not enough. Reproduce the boundary with concrete reserves, ticks, fees, and a stateful sequence; account for all fees and price limits.

## Defensive test

Run a stateful differential test against a reference implementation and assert conservation after every tick transition, including reverse-direction swaps.

