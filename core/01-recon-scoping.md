# Phase 1 — Recon & Scoping

Goal: discover and scope the target. Know what you are auditing before you audit it. Output: `{AUDIT_DIR}/scope.md` (use `templates/scope.md`).

## 1.1 Resolve the target

- Project root, chain(s), in-scope paths.
- Default excludes: `interfaces/`, `lib/`, `mocks/`, `test/`, `scripts/`, node modules, `*.t.sol`, `*.s.sol`, `*Mock*`, `*Test*` — unless the user explicitly puts them in scope.
- Size guards: any source file >1 MB → refuse; >500 KB → warn and treat as complex.
- Toolchain detection: `foundry.toml` / `hardhat.config.*` / `Cargo.toml`+`Anchor.toml` / `Move.toml` / circom `package.json`.
- If the toolchain exists, capture a baseline build (`forge build` / `cargo check` / `sui move build`) and run coverage in the background (`forge coverage` / `npx hardhat coverage`) — coverage is recon data, not a gate.

## 1.2 Documentation & history recon (mechanized)

- Run `bash {SKILL_DIR}/scripts/enumerate.sh <root> <src-dir>` — toolchain, per-file line counts/nSLOC, NatSpec ratio, test stats, commit stats. Feeds the scope report and the complexity rubric.
- Run `python3 {SKILL_DIR}/scripts/analyze_git_security.py --repo <root> --src-dir <src-dir> --json {AUDIT_DIR}/git-security-analysis.json` — fix candidates, dangerous-area changes, late changes, forked deps, tech debt. Read the JSON into the scope report's recon section. (Exit 2 = repo has no commit history — record "no git history" and continue; not a blocker.)
- Read **everything** before producing output. Do not start writing after reading 3 files.

- README, docs, whitepapers, docs site, previous audit reports, known-issues lists, bug-bounty scope, `SECURITY.md`, deploy/migration scripts, config files.
- Git history signals (see `{SKILL_DIR}/sources/pashov-skills/x-ray` for tooling): late-stage changes, changes in fund-movement files, fix candidates, forked dependencies, tech debt.
- Deployment recon: deployed addresses, chains, proxy admins/owners (browser/RPC if network available), TVL, protocol age, prior incidents.
- Do not trust the README — verify claims against code. Flag any discrepancy as `⚠️ DOC/CODE MISMATCH` in the scope report.

## 1.3 Prior-art / known-issues register

Before hunting, register what is already known:

- Search public finding databases for this protocol (Solodit via claudit MCP if available, Immunefi, audit reports).
- Record each known issue with a **mechanism-level** note (match on mechanism, not topic): what was exploited, in which function, and what the fix looked like.
- Consult `{SKILL_DIR}/knowledge/index.md` for pattern families relevant to the protocol type.

## 1.4 Complexity rubric (effort calibration)

Score each metric 1–4 (auto-bump to ≥3 on red flags), composite:

```
composite = 0.25×nSLOC + 0.25×externalIntegration + 0.20×stateCoupling
          + 0.15×accessControl + 0.15×upgradeability
```

- 1.0–1.5 LOW → checklist sweep; 1.6–2.5 MEDIUM → vector scan; 2.6–3.5 HIGH → deep interrogation; 3.6–4.0 CRITICAL → deep + invariant extraction + PoC.
- Red flags: `delegatecall` / user-supplied call targets; Solana user-supplied program accounts / `invoke_signed` with complex seeds / `remaining_accounts` iteration; sentinel values (0="unset"), monotonic claim pointers, write-once flags gating critical logic, cross-contract shared state; self-assignable roles, no two-step transfer, inconsistent modifier application, `tx.origin` auth; `selfdestruct` in implementation, no storage gap, uninitialized implementation, admin changing core addresses without validation.
- Map the tier to the effort mode from Phase 0; upgrade to `--deep` if CRITICAL.

## 1.5 Attack-surface inventory (first pass)

Trigger-condition-driven; mark `⚠️ INVESTIGATE` items (the full matrix stays internal — only the summary goes in the scope report):

- Entry points (permissionless / role-gated / admin-only), external calls, oracles, token handlers, governance, upgrade paths, cross-chain bridges/relays, callbacks/hooks, fallback/receive, signature entry points.

## 1.6 Trust-assumptions table

| From | To | Assumption | Risk if broken |
|---|---|---|---|
| users | protocol | ... | ... |
| protocol | oracle | reports sane prices | spot pool manipulation |

Complete for every external dependency. One line each; no raw JSON.

## Output: `scope.md`

Sections: target identity · chain(s) · in-scope file list · complexity tier + effort mode · protocol category · attack-surface summary · trust table · known-issues register · doc/code mismatches · open questions · documented assumptions.

## Exit gate

- Every in-scope source file is listed; entry points are classified; trust table is filled; known-issues register exists.
- Open questions proceed with documented assumptions — do not block.
