# Ultimate Web3 Security Skill

A production-grade, autonomous Web3 security-research system for agent runtimes. Give it a repository and say **"Audit this protocol"** — it runs the full pipeline:

```
RECON/SCOPING → PROTOCOL MODEL → THREAT MODEL → DEEP ANALYSIS (manual/static/dynamic)
→ ATTACK GENERATION → HYPOTHESIS ENGINE → EXPLOIT VALIDATION → FALSE POSITIVE ELIMINATION
→ ADVERSARIAL REVIEW → SECOND OPINION → FINDING JUDGE → FINAL REPORT → KNOWLEDGE MEMORY
```

**Core principle:** never equate suspicious code with vulnerability. Every finding must survive an evidence chain (Observation → Hypothesis → Reachability → Invariant violation → Attack path → Impact → Exploitability → PoC → Mitigation analysis → Known-issue analysis → Adversarial challenge → Validated finding). Optimized for *real vulnerability discovery*, not finding count. "No valid vulnerability found" is a successful outcome.

## Layout

| Path | Role |
|---|---|
| `SKILL.md` | Master orchestrator: pipeline, phase dispatch, effort modes, chain dispatch, global rules |
| `core/01..10` | Pipeline phase methodology — loaded phase-by-phase |
| `skills/evm-deep-audit` | EVM sub-skill + load-on-trigger attack catalog |
| `skills/solana-audit` | Solana sub-skill + Token-2022 pitfalls reference |
| `skills/move-audit` | Sui/Aptos Move sub-skill (object model, capabilities, PTB, upgrades) |
| `skills/zk-audit` | Circom sub-skill (declarative doctrine, soundness/completeness/privacy) |
| `skills/poc-builder` | Foundry PoC + mainnet-fork construction |
| `skills/fuzz-harness` | Invariant-driven fuzzing (Echidna/Medusa/Trident) |
| `agents/` | Parallel lens agent templates + adversarial second-opinion template |
| `tools/` | Per-tool strategy cards: question → evidence → blind spots |
| `scripts/` | **Mechanized tooling**: enumerate.sh, analyze_git_security.py, ensure_foundry.sh, setup_fuzz_profile.sh, medusa/ (run_medusa.js, run_echidna.js, generate_suite.js, generate_handlers.js) |
| `knowledge/` | Pattern memory: schema + index + **28 pattern files** across EVM/Solana/Move/ZK |
| `evals/` | **Benchmark corpus (8 vuln + 3 clean fixtures, 4 executable PoCs) + measured results + regression-gate protocol** |
| `templates/` | scope.md, finding.md, report.md |
| `research/` | Research extraction reports (provenance of design decisions) |
| `sources/` | Cloned reference repositories (provenance) |

## Provenance

Built from [pashov/ai-web3-security](https://github.com/pashov/ai-web3-security) — treated as a **curated index**, not a final architecture. 47 referenced repositories were cloned into `sources/` and analyzed by research agents; `research/` documents what each contributed and how contradictions were resolved.

## Measured performance (29 fixtures, 2026-08-13 runs)

| Corpus | Precision | Recall | Notes |
|---|---|---|---|
| Internal (8 vuln + 3 clean) | 8/8 = 100% | 8/8 = 100% | 4 PoC-level executable forge proofs |
| External (11 vuln + 7 benign) | 11/11 = 100% | 11/11 = 100% | real hacks (bZx $8M, Cream $130M, Harvest $34M, Inverse $1.2M, Rari $10M, Cashio $52M) + benign traps, audited blind under neutral IDs, 7/7 benign cleared |
| **Combined** | **19/19 = 100%** | **19/19 = 100%** | 0 false positives, 0 misses |
| Ensemble judge | — | — | protocol + simulation on 2 candidates, correct both directions |

Honest limits: external evidence is trace-level (Solana/Move toolchains unavailable here; EVM reproducers are minimal excerpts); all fixtures are small reproducers — multi-contract live protocols remain the untested frontier; ensemble is same-model until a multi-model runtime is available. `evals/README.md` defines the regression protocol.

## Key design decisions

1. **Master stays focused.** SKILL.md is ~90 lines of orchestration; methodology lives in `core/` loaded per phase and load-on-trigger catalogs.
2. **Accounting-first analysis.** The primary lens is the money-map drift taxonomy — the highest-yield bug framing across sources.
3. **Gate-first judging, adversarial second.** Deterministic kill gates → inversion pass → fresh second-opinion derivation. Consensus never substitutes for a gate.
4. **The judge is the pashov lineage, hardened.** Four sequential gates + unprivileged-amplifier rule + impact premise ("WHO loses WHAT") + severity recalibrated from the verified path.
5. **Mechanized tooling.** Recon (enumerate + git-security) and fuzzing (suite/handler generation, medusa/echidna runners, via_ir profile fix) run through ported, tested scripts — not ad-hoc agent code.
6. **Knowledge layer is evidence-gated.** 28 pattern files; only validated findings and generalizable kills update them; patterns are hypotheses for closer looks, never auto-verdicts.
7. **Every claim is measured or labeled.** Findings carry confidence + evidence level; the skill itself carries eval numbers with stated limitations.

## Install

Copy this directory into your agent runtime's skills directory (e.g., `~/.claude/skills/ultimate-web3-security/`). Triggers on "audit this protocol", "security review", "smart contract audit", and similar phrases.

## Usage

```
Audit this protocol.                      # audits {cwd} with the standard pipeline
Audit /path/to/repo.                      # audits a specific repo
Audit this protocol --deep.               # + fuzz campaigns, fork tests, parallel lens agents
Audit this protocol --quick.              # triage: single pass, no PoC/fuzz
```

All working artifacts land in `{target}/ultimate-audit/` — the target source tree is never modified.
