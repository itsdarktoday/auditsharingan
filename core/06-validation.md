# Phases 6–7 — Exploit Validation & False-Positive Elimination

Goal: prove the attack works, or kill it. Output: `{AUDIT_DIR}/validation.md`.

## 6.1 Construct a minimal exploit (for serious candidates)

Canonical sequence:

```
attacker setup → initial state → transaction 1 → transaction 2
→ manipulation → state violation → asset extraction / impact → final state
```

- Prefer **executable proof**: a Foundry test (unit-level) or a fork test against deployed addresses — see `{SKILL_DIR}/skills/poc-builder/SKILL.md`. Invariant-class candidates → fuzz reproduction — see `{SKILL_DIR}/skills/fuzz-harness/SKILL.md`.
- Record per exploit: attacker requirements, capital requirements, profit/loss, affected assets, affected users, protocol loss, repeatability, prerequisites.
- Do not claim exploitability without evidence. If no PoC, keep a candidate only with a complete, unbroken trace; otherwise downgrade.

## 6.2 False-positive elimination — "prove yourself wrong"

Run every candidate through these pre-gates before the Phase 10 judge:

- **K1 Impact premise.** WHO loses WHAT? If the hypothesis is mechanism-only ("`startLiquidation` succeeds while active"), DO NOT kill it — derive the harm first: name the assets, the victims, and the amount at risk from the trace. Kill only if, after this attempt, NO identifiable victim or loss exists.
- **K2 Guard interrupt.** Read every guard, check, modifier, and constraint on the attack path. A specific guard that interrupts the attack before harm (quote the exact line) → kill.
- **K3 Speculative interruption does not count.** "The deployer would set X", "the caller would notice" → clears nothing; continue.
- **K4 Privilege.** Harm requires a trusted role acting maliciously or against documented intent → reject unless an unprivileged amplifier is named: race / retroactive sweep / asymmetric formula / access gap.
- **K5 Dust.** Dust-level loss with no compounding → demote.
- **K6 Self-harm only** → reject.
- **K7 Known/intended.** Mechanism matches the known-issues register or documented behavior → route to KNOWN verdict, not a new finding.
- **Weak-evidence floor.** Loss depending on off-chain payload construction, admin-set-later config, unobservable user ordering, or callbacks on callee types outside the whitelist → cap at LOW.
- **Calibration checks.** A rounding error is only Low if it cannot be looped — check first, always. Torn between two severities → choose the lower and say why in one line. Over-claiming costs credibility.

## 6.3 Document kills

Every killed candidate gets one line: what guard, invariant, or economic fact saved it. This is audit evidence too, and it feeds the knowledge phase.

## 6.4 Promotion criteria — what survives to the judge

The kill gates above must never be the only decision rule. A candidate SURVIVES Phase 6/7 (proceeds to the judge) when ANY of these hold:

- **P1 PoC**: executable proof passes the clean sequence (highest grade).
- **P2 Complete trace**: no PoC, but the attacker→harm path is unbroken — every guard read, every precondition reachable through normal usage or common token behaviors.
- **P3 Convergence**: 2+ independent lenses/agents/passes derived the same mechanism independently (weakens single-pass anchoring).
- **P4 Partial path**: only weakness is an incomplete trace step, but the path is reachable and unguarded — survives with the missing step named explicitly (judged at confidence ≤75).
- Otherwise → kill (with K-id) or demote to LEAD (high-signal trail for manual follow-up; never silent-dropped).

Record which criterion (P1–P4) each surviving candidate meets in `validation.md`.

## Output: `validation.md`

Per candidate: exploit trace (with PoC pointer and commands) or kill reason (with K-id and evidence).

## Exit gate

Every candidate above LOW has explicit validate/kill evidence.
