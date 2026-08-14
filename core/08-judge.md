# Phase 10 — Finding Judge

Goal: verdict + severity + confidence for every candidate. Output: `{AUDIT_DIR}/judgments.md`.

You are not defending the code and not defending the finding. The gates verify that the attacker's claimed exploit actually fires end-to-end — anything that interrupts the attack between the attacker's call and the harm means the claim does not execute.

## 10.0 Judge mode — single or ensemble

- Default: single-judge gates below, then `--deep` mode (or any CRITICAL/HIGH candidate the judge is not confident about) escalates to the **ensemble judge**: see `{SKILL_DIR}/agents/ensemble-judge.md`.
- Ensemble core rules: N=3 judges, model diversity required when the runtime supports it, blind inputs (code region + invariant claim only), evidence outranks votes (a concrete guard from any judge sends the candidate back to Phase 6), unanimous/majority aggregation, severity = min of confirmers, UNKNOWN is an acceptable verdict.
- Same-model ensembles only correct context anchoring — record which kind you ran in `judgments.md`.

## 10.1 Sequential gates (in order; fail → stop, verdict per gate)

- **G1 Impact premise.** WHO loses WHAT? Mechanism-only descriptions fail — but note them as "cheap to fix: describe the harm" rather than silently dropping.
- **G2 Attack execution.** Trace caller → harm. Read every guard/check/modifier on the path. A specific guard interrupting the exploit step before harm (quote the exact line) → fail. Speculative interruptions ("probably wouldn't happen") → clears, continue.
- **G3 Reachability.** The vulnerable state must exist in a live deployment. Structurally impossible (an enforced invariant prevents it) → fail. Requires privileged actions outside normal operation → demote.
- **G4 Trigger.** An unprivileged actor executes the attack profitably → pass. Only trusted roles → demote **unless** an unprivileged amplifier is named (race / retroactive sweep / asymmetric formula / access gap). Admin findings with no amplifier → reject (do not even emit as lead).
- **G5 Impact.** Self-harm only → fail. Dust, non-compounding → demote. Material loss to an identifiable victim → confirmed.

`UNCERTAIN` at any gate counts as ALLOWS — an unproven guard is not a guard.

## 10.2 Verdicts

| Verdict | Meaning |
|---|---|
| **VALID** | all gates pass; PoC exists or complete unbroken trace |
| **LIKELY VALID** | gates pass logically; PoC incomplete but trace unbroken |
| **UNCERTAIN** | genuine ambiguity in reachability/impact after targeted checks |
| **KNOWN** | mechanism matches known-issues register or documented behavior |
| **INTENDED** | documented design tradeoff; no invariant broken |
| **FALSE POSITIVE** | a specific gate fails with concrete evidence |

## 10.3 Confidence (labels findings, never removes them)

**Verdict determines whether something is a finding. Confidence only labels it.** A VALID or LIKELY VALID verdict ALWAYS appears in the findings section — regardless of confidence score.

Start at **100**; deduct only for genuine weaknesses:

- Partial attack path (P4 promotion: a named missing step) −20
- Evidence relies on off-chain data or unverified external behavior −10
- Requires specific but achievable state −5

A **complete unbroken trace (P2) is full evidence** — it takes NO "partial path" deduction and NO "weak evidence" deduction. No PoC ≠ weak evidence.

Bands (labels only): ≥80 high · 65–79 medium · 40–64 low · <40 → lead (with reason).

Never let deductions accumulate into demotion for a candidate that passed all five gates — the gates already proved the attack fires end-to-end.

## 10.4 Severity (recalibrate from the verified path, not the claim)

- **CRITICAL** — permissionless loss of most protocol funds or total loss of user funds; no meaningful preconditions; direct drain / unauthorized mint, protocol-wide.
- **HIGH** — direct drain/unauthorized mint with limited preconditions; irreversible bricking of a core lifecycle function; griefing affecting ALL users of a critical function.
- **MEDIUM** — loss with strict preconditions; admin-only harm with a named unprivileged amplifier; per-user griefing; missing access control on a function setting an economic parameter.
- **LOW** — non-loopable dust/rounding; missing access control on per-user state setters; admin actions without timelock (centralization, no exploit path).
- **INFO** — centralization observations, missing events, best practices without an exploit path.

Override rules: admin-only without amplifier → not a finding (document in governance notes). Requires 3+ simultaneous preconditions → demote. Do not inflate severity; do not downgrade valid multi-transaction issues merely because they need multiple transactions; judge the **actual security consequence**.

## 10.5 Dedup & completeness

- Dedup key: (contract, function, mechanism, fix-shape). Same root cause but different fix shapes → distinct findings. The same missing named check across many functions → ONE finding, title generalized to the missing check.
- Completeness check before finalizing — print: `Completeness: N unique (contract, function, mechanism) in leads, N covered by verdict or documented rejection.` Zero silent drops.

## 10.6 Lead promotion (the judge's upward path — never only kill/demote)

Before finalizing, promote leads where warranted:

- **Cross-contract echo.** A root cause confirmed as a finding in one contract → promote in every contract with the identical pattern.
- **Multi-agent convergence.** 2+ independent lenses/agents/passes flagged the same area and the lead was demoted (not rejected) → promote to FINDING at confidence 75.
- **Partial-path completion.** The only weakness is an incomplete trace, but the path is reachable and unguarded → promote to FINDING at confidence 75, description only.
- **Evidence upgrade.** LIKELY VALID (confidence <80) → VALID when the missing evidence (PoC / reachability proof) is supplied.
- Promoted findings still carry their promotion reason in `judgments.md`; leads that do not meet any criterion stay leads — explicitly listed, never silent-dropped.

## Output: `judgments.md`

Per candidate: gates passed/failed (with line evidence) · verdict · severity · confidence · dedup group · completeness line at the end.

## Exit gate

Verdict + severity + confidence for every candidate; completeness check printed.
