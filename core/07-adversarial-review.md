# Phases 8–9 — Adversarial Review & Second Opinion

Goal: attack every surviving candidate from the opposite direction. Output: `{AUDIT_DIR}/adversarial-review.md`.

## 8.1 Inversion review — per candidate

Assume the finding is wrong. Ask: **"How can I prove it is wrong?"** Check in order:

1. **Reachability** — can the vulnerable state actually exist in a live deployment? (constructor args, init flow, deployment config)
2. **Access restrictions** — hidden validations, modifiers, role checks, internal `msg.sender` checks you missed.
3. **Protocol invariants** — does an `INV-x` actually prevent it?
4. **State prerequisites** — are preconditions achievable through normal usage or common token behaviors (fee-on-transfer, rebasing, blacklisting are plausible for arbitrary tokens)?
5. **Economic feasibility** — do costs exceed gains? MEV/atomicity constraints? Flash-loan fees?
6. **Existing mitigations** — `nonReentrant`, `SafeERC20`, checks-effects-interactions, re-entrancy guards on the actual path.
7. **Intended behavior** — documented design tradeoff? Accepted risk? (cite the doc)
8. **Deployment configuration** — admin/timelock config in deploy scripts changes the threat.
9. **Upgrade configuration** — proxy admin, storage gaps, `_disableInitializers()`.
10. **Known issues** — previous audits, bounty reports, the known-issues register (mechanism-level match).
11. **Accepted risks** — team statements, README caveats.

Then **attack your own PoC**: find the input or configuration that makes the exploit fail, and test it. If the PoC survives, record that too — a PoC that survives hostile testing is much stronger evidence.

A finding that survives adversarial review gets significantly higher confidence.

## 8.2 Second opinion (fresh derivation)

For each surviving candidate, re-derive it independently:

- When a multi-agent runtime is available, use the `{SKILL_DIR}/agents/second-opinion.md` template: give the reviewer ONLY the code region and the invariant claim (`INV-x`) — never your original chain. The template enforces: derive-own-path first, CONFIRM/CONTRADICT/UNKNOWN verdicts, killing evidence must be an exact line, burden of proof on the disagreeing party.
- Single-agent fallback: perform the same fresh derivation yourself, reading only the code region + invariant claim, before comparing with your original chain.
- Compare the derived chain with yours:
  - **Agrees** → confidence up.
  - **Disagrees** → the disagreeing party bears the burden of proof. No proof → that party's claim fails.
  - **New guard discovered** → back to Phase 6 validation.

Record the second-opinion outcome per candidate.

## Output: `adversarial-review.md`

Per candidate: inversion notes (which checks were made, which held), own-PoC attack result, second-opinion outcome (agree/disagree + proof), revised confidence.

## Exit gate

Every candidate has inversion notes + own-PoC attack + second-opinion outcome.
