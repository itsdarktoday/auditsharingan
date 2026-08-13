# Phase 4 — Deep Analysis

Goal: find leads through manual reasoning, static tools, and dynamic analysis. Output: `{AUDIT_DIR}/leads.md`.

## 4.1 Discipline

- Work **function-by-function** down the ranked attack surface. Never checklist-skim whole files.
- **Multi-pass**: every critical contract gets ≥2 passes — first pass data flow (what moves, what it updates), second pass adversarial inversion (what value slips past each check). Keep per-contract notes.
- Trace attacks with **concrete values** — a finding is not real until it is traced with concrete values.
- Record every lead with (contract, function, line, mechanism, invariant affected) and its origin (manual lens / tool / fuzz).

## 4.2 Manual reasoning protocol — the 8-level model

Apply in order per function:

1. **Code** — what does it literally do? (Feynman: explain in plain English, no jargon. Wherever the plain-English explanation gets fuzzy, that is an unexamined assumption — bugs hide there.)
2. **State** — what changes, exactly? Every storage write.
3. **Protocol** — why does this state exist?
4. **Invariants** — which `INV-x` does it touch? Could it violate one?
5. **Attacker** — what does the adversary control here?
6. **Economics** — can a violation be turned into value (WHO loses WHAT)?
7. **Composition** — can another contract, callback, oracle, token, or tx sequence amplify?
8. **Proof** — can it be demonstrated?

**Mental tools** (reach for the right one when the trigger fires):

- Opening any new function/contract → **Feynman** (always first).
- A line you don't fully understand → **Socratic**: why is this here? What does it assume? What happens if the assumption breaks? Drill 2–3 whys deep — the first answer is usually a restatement.
- A path that looks too clean → **Inversion**: how would I make it NOT do that? What value slips past the check? What state am I in just before this?
- A "bug" conclusion → **amplify the attack** (chain it, find more victims, lower the precondition cost). Never argue yourself out of one here — refutation is Phase 6+.

## 4.3 Analysis lenses (dispatch per protocol type)

Apply the lenses that match the protocol type; each lens has trigger questions and required proof (see the chain sub-skill + attack catalog for detail):

- **L1 Accounting drift** — missing write / wrong write / mistimed write / wrong party / untrustworthy input / unreachable state. Primary lens: most real money bugs are one-sided writes to tracked totals.
- **L2 Access control** — privilege escalation, initialization abuse, role confusion, ownership transitions.
- **L3 Rounding & precision** — favoring direction, compounding, zero-rounding, share inflation, donation attacks, decimals.
- **L4 Oracle & pricing** — spot/TWAP/Chainlink freshness, decimals, manipulation, stale data, fallback logic.
- **L5 Liquidation & settlement** — DoS of liquidations, unfair liquidation pricing, bad-debt accrual, keeper incentives.
- **L6 Signatures** — replay (cross-chain!), EIP-712 domain correctness, malleability, permit abuse, fee-on-transfer + permit.
- **L7 Reentrancy & external calls** — single-function, cross-function, read-only, callbacks, ERC deviations, return-value assumptions.
- **L8 Upgradeability** — storage collisions, uninitialized implementation, upgrade authorization, selfdestruct.
- **L9 Governance** — voting manipulation, delegation, quorum, timelock bypass, emergency powers.
- **L10 DoS / griefing** — permanent locks, gas exhaustion, state bloat, attacker-controlled iteration, griefing without profit.
- **L11 Cross-chain** — message replay, ordering, validation failures, trust-boundary violations, bridge accounting.
- **L12 Composability** — treat every external protocol/contract as adversarial unless explicitly trusted.

## 4.4 Static analysis (tool strategy)

For every tool you consider running, answer first: *What question am I trying to answer? Can this tool answer it? What evidence will it produce? What are its blind spots?* See `{SKILL_DIR}/tools/*.md` for per-tool cards.

Recommended order: Slither (broad) → Semgrep (custom patterns) → CodeQL (taint/data flow, if available) → chain-specific tools (Aderyn, SUIZERO, Move prover).

**All tool alerts are leads** — tag the origin and push them through the same reasoning protocol as manual leads.

## 4.5 Dynamic analysis (when the mode allows)

- **Invariant testing**: formalize `INV-x` as fuzz properties — see `{SKILL_DIR}/skills/fuzz-harness/SKILL.md` (Echidna/Medusa for EVM, Trident for Solana). Run on high-complexity accounting.
- **Symbolic**: Halmos for small, bounded models of critical math (rounding, exchange rates).
- **Fork differential**: for forked protocols, diff behavior against the fork origin — what changed is the attack surface. Test the diffs.
- **Tests as security intelligence**: fixtures/mocks are assumptions — ask whether a user can reach the same production function without the fixture's preconditions; hunt `assume`/`bound` fuzz filters (each excluded class is a candidate attack); compare what tests promise with what they prove.

## 4.6 Parallel lenses (optional, `--deep`, multi-agent runtime only)

Dispatch independent lens agents on disjoint code regions. Agent templates live in `{SKILL_DIR}/agents/`:

- `lens-accounting.md` — money-map drift (highest yield; always dispatch first)
- `lens-access-control.md` — privilege escalation, init abuse
- `lens-oracle.md` — pricing manipulation, staleness
- `lens-upgradeability.md` — proxies, storage, governance

Each template defines: inputs, method, lead output format, discipline (leads not findings; no severity; never argue leads away). Merge results into `leads.md` with dedup key `(contract, function, mechanism)`. If the runtime has no sub-agent support, run the same lenses sequentially — coverage drops, methodology does not change.

## Output: `leads.md`

Every lead: id · contract · function · lines · mechanism · affected invariant · origin · priority (P0–P2) · open questions. Sorted by priority.

## Exit gate

All ranked surfaces covered at least once; every lead traced to a mechanism + invariant; leads ranked.
