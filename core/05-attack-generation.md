# Phase 5 — Attack Generation (Hypothesis Engine)

Goal: turn leads and architecture into attack hypotheses. The question is: **"Can I break it?"** Output: `{AUDIT_DIR}/hypotheses.md`.

## 5.1 Generate from architecture, not checklists

Do not rely exclusively on known vulnerability lists. For each lead and each ranked surface, generate hypotheses from what the code *assumes* that an adversary can *violate*.

Work the attack families systematically — as triggers, not as a recited checklist:

- **Logic** — incorrect state transitions, broken assumptions, missing validation, edge cases, unexpected execution paths.
- **Access Control** — privilege escalation, authorization bypass, initialization abuse, role confusion, ownership transitions.
- **Accounting** — incorrect balances, share inflation, rounding, precision, donation attacks, inconsistent accounting, debt tracking.
- **Economics** — oracle manipulation, price manipulation, liquidation manipulation, collateral abuse, leverage amplification, flash-loan attacks, insolvency, fee manipulation, MEV.
- **External Calls** — reentrancy, callbacks, malicious tokens, ERC-standard deviations, arbitrary calls, return-value assumptions.
- **Cross-Contract** — inconsistent assumptions, state desynchronization, authorization propagation, callback chains, dependency manipulation.
- **Cross-Chain** — message replay, ordering, validation failures, trust-boundary violations, bridge accounting, chain-specific assumptions.
- **Upgradeability** — storage collisions, initialization, upgrade authorization, implementation replacement, proxy behavior, governance attack paths.
- **Governance** — voting manipulation, delegation issues, quorum problems, timelock bypass, emergency powers.
- **DoS / Griefing** — permanent locks, gas exhaustion, state bloat, attacker-controlled iteration, griefing without direct profit.
- **Composability** — external protocols and contracts behave adversarially unless explicitly trusted.

## 5.2 Hypothesis template

Fill one template per serious hypothesis:

```
H-id:
Trigger:        (who calls what, with what parameters)
Preconditions:  (state that must exist; how achievable)
Manipulation:   (tx sequence / steps)
Violated invariant: (INV-x)
Impact premise: (WHO loses WHAT — one sentence; mechanisms are insufficient)
Estimated severity: (preliminary)
Capital:        (attacker requirements)
Repeatability:  (once / recurring / per-user)
Related leads:  (lead ids)
Open questions:
```

## 5.3 Economic framing (Level 6)

For every hypothesis: attacker requirements, capital, profit/loss estimate, affected assets, affected users, protocol loss, repeatability, prerequisites. Ask: is the manipulation flash-loan feasible (same-tx atomic)? If no value extraction exists, it is griefer-only severity.

## 5.4 Composition framing (Level 7)

Can another contract, callback, bridge, oracle, token, or transaction sequence amplify it? Enumerate neighbors: fork-origin protocols, integrated pools/vaults, token bridges, keeper networks, hook callbacks.

## 5.5 Prioritize

Rank by expected value = P(valid) × impact × evidence availability. Assign each: **VALIDATE NOW** / **LATER** / **DROP** (with one-line reason).

## Output: `hypotheses.md` — sorted, template filled for each VALIDATE NOW / LATER candidate.

## Exit gate

Every P0 lead has ≥1 hypothesis; economic framing is filled for the top hypotheses.
