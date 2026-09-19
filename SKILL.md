---
name: auditsharingan
description: >
  Evidence-oriented Web3 security auditing for EVM/Solidity, Vyper, Solana/Rust,
  Move, and ZK codebases. Use when asked to audit a protocol or repository,
  review smart contracts, find vulnerabilities, validate an exploit, or assess
  Web3 security. It combines deterministic reconnaissance and scanners with
  protocol modeling, adversarial reasoning, reproducible proofs, mitigation
  verification, and a machine-readable evidence trail.
metadata:
  display_name: AuditSharingan
  version: "1.0.0"
---

# AuditSharingan

AuditSharingan is a security research workflow, not a vulnerability counter.
It separates machine-generated leads from validated findings and requires a
complete evidence chain before assigning a high-impact verdict:

```text
scope → protocol model → threat model → observation → hypothesis
→ reachability → invariant violation → quantified impact → proof or trace
→ mitigation → known-issue check → skeptic review → judgment → report
```

## Operating contract

When triggered, work autonomously inside the user-provided target and preserve
the target's source. Read only the core and chain-specific guidance needed for
the target, then run the deterministic engine:

```bash
python3 {SKILL_DIR}/scripts/auditsharingan.py {TARGET} --standard
```

Use `--quick` for triage and `--deep` when bundle preparation is useful for a
host runtime that can dispatch reviewers. The engine writes artifacts to
`{TARGET}/AuditSharingan-audit/` unless `--output-dir` is supplied. It never
claims that a missing executable or failed stage succeeded; inspect
`run-manifest.json` and the step logs before relying on any output.

Do not modify application source, deploy contracts, send transactions, use a
live private key, or contact an external service unless the user explicitly
requests that action. Running local read-only build, test, lint, fuzz, and
symbolic commands is in scope. If a command can spend funds, alter a remote
system, or destroy data, stop and request a specific decision.

## Required reading and dispatch

Load these in order, using the target's actual chain and complexity to decide
how much detail is needed:

1. `core/01-recon-scoping.md` — boundary, build graph, scope, toolchain, and
   trust matrix.
2. `core/02-protocol-model.md` — actors, money flows, state machines, and
   explicit invariants.
3. `core/03-threat-model.md` — attacker capabilities, trust boundaries, and
   assumptions that must be tested.
4. `core/04-deep-analysis.md` — eight reasoning levels, archetype lenses, and
   composition checks.
5. `core/05-attack-generation.md` — attack graphs and profit/impact math.
6. `core/06-validation.md` — evidence ladder and deterministic validation
   gates.
7. `core/07-adversarial-review.md` — committed invariants and blind skepticism.
8. `core/08-judge.md` — severity, confidence, deduplication, completeness, and
   the difference between a lead and a finding.
9. `core/09-reporting.md` — report and remediation schema.
10. `core/10-knowledge.md` — memory updates and regression discipline.

Then load the relevant sub-skill(s):

- EVM/Vyper: `skills/evm-deep-audit/SKILL.md`.
- Foundry/Echidna/Medusa testing: `skills/fuzz-harness/SKILL.md`.
- PoC construction: `skills/poc-builder/SKILL.md`.
- Bounded symbolic reasoning: `skills/formal-verifier/SKILL.md`.
- Solana/Rust: `skills/solana-audit/SKILL.md`.
- Sui/Aptos Move: `skills/move-audit/SKILL.md`.
- Circom and related circuits: `skills/zk-audit/SKILL.md`.

For independent review, use the lens prompts in `agents/`. The bundle builder
creates deterministic prompts and source hashes; it prepares dispatch but does
not impersonate a subagent runtime. Preserve each reviewer output and feed it
through the judge and skeptic stages.

## Evidence rules

Every candidate must state all of the following, or remain a `LEAD`:

- exact file, function, and line range;
- attacker identity and reachable call sequence;
- state before and after the sequence;
- invariant or security property violated;
- who loses what, including a numeric or bounded impact model;
- proof level: `poc`, `trace`, `mathematical-proof`, `static-lead`, or `none`;
- guard, privilege, economic, and known-issue checks;
- minimal remediation and a regression plan;
- a decision receipt explaining why the item was validated or killed.

Static output, compiler warnings, suspicious naming, and a failing tool are
signals—not findings. A tool can report a candidate, never a final severity.
Unknown facts are recorded as unknown and lower confidence; they are not
silently treated as attacker-favorable or defender-favorable assumptions.

High and critical candidates require one of:

- a passing, target-specific executable PoC;
- a complete trace with every guard and state transition checked; or
- a mathematical proof whose assumptions and solver limits are recorded.

If a generated PoC or invariant file still contains a scaffold marker, it is
not evidence. `scripts/generate_poc.py` and
`scripts/generate_foundry_invariants.py` intentionally emit compile-safe,
incomplete scaffolds rather than fake proofs.

## Standard audit sequence

1. Resolve the target, repository root, build system, compiler versions, chain,
   deployment addresses, dependencies, tests, and explicit exclusions.
2. Build a scope manifest and list capabilities. Treat missing tools and
   failed commands as visible limitations.
3. Draw the actor/trust map, asset-flow map, state machines, and invariants.
4. Run the deterministic engine and review every report in `leads.md`.
5. Apply the eight reasoning levels and relevant lens prompts manually against
   in-scope code, including cross-contract and cross-domain seams.
6. Form attack graphs. Check reachability, privilege, timing, gas, oracle,
   token behavior, liquidity, and net economic outcome.
7. Validate candidates with local tests, fuzzing, symbolic tools, or numeric
   traces. Preserve commands and outputs in the artifact directory.
8. Run the skeptic pass. Resolve duplicates by root cause while retaining all
   evidence and killed-lead receipts.
9. Judge severity and confidence separately. Do not upgrade a candidate merely
   because it is plausible or severe in the abstract.
10. Write the Markdown report, JSON findings when available, HTML dashboard,
    limitations, and remediation verification plan.

For a proposed patch, use the isolated verifier:

```bash
python3 {SKILL_DIR}/scripts/verify_mitigation.py {TARGET} PATCH.diff \
  --poc-test test_exploit_slug \
  --output-file {TARGET}/AuditSharingan-audit/mitigation.json
```

It refuses a missing pre-patch reproduction, applies the patch only to a
temporary copy, distinguishes compilation failure from an expected blocked
exploit, and runs the regression suite without resetting the user's worktree.

## Report minimum

The final report must include scope and exclusions, tool/capability manifest,
architecture and invariants, validated findings, killed/deferred leads,
limitations, reproducibility commands, and remediation status. Findings use
the schema in `templates/finding.md` and must never imply that an untested
chain, tool, deployment, or formal method was covered.

Generate the dashboard only after reviewing the Markdown:

```bash
python3 {SKILL_DIR}/scripts/generate_html_report.py \
  {TARGET}/AuditSharingan-audit/report.md \
  --output-file {TARGET}/AuditSharingan-audit/report.html
```

The HTML renderer preserves an explicit “no parseable findings” state instead
of turning malformed or empty input into a false clean bill of health.
