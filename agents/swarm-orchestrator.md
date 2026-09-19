# AuditSharingan reviewer swarm

The swarm is a review protocol and dispatch artifact, not an imaginary source
of parallel workers. The host runtime must provide actual reviewers; when it
does not, run the bundles as a documented sequential review.

## Roles

Fourteen domain lenses cover math, callbacks, access control, economics,
oracles, lending, AMM hooks, vaults, governance, signatures, upgradeability,
DoS, bridges, and assembly. Three seam reviewers cover numerical/economic,
trust/callback, and state-machine interactions. A final skeptic tries to kill
the candidates rather than add more.

The canonical prompt files are `agents/lens-*.md`, `agents/gap-hunter-*.md`,
and `agents/skeptic-adversary.md`. Each reviewer must return:

```text
status: VALIDATED_CANDIDATE | LEAD | KILLED
location: file:function:lines
invariant: INV-...
attacker_and_path: ...
impact: victim, asset/state, magnitude
evidence: poc | trace | mathematical-proof | static-lead | none
guards_checked: ...
decision_receipt: ...
```

## Dispatch procedure

Prepare deterministic bundles:

```bash
python3 scripts/build_swarm_bundles.py TARGET \
  --output-dir TARGET/AuditSharingan-audit/bundles
```

The builder emits `source-manifest.json` with SHA-256 hashes and lightweight
prompts by default. Use `--embed-source` only when the host cannot grant a
reviewer access to the target. It emits `dispatch-manifest.json` with
`execution: prepared-only`; no script output may be described as a reviewer
result until a host reviewer actually produced it.

Dispatch in parallel only when the host provides independent workers. Give
each role the same target revision, scope manifest, and source hashes. Keep
the skeptic blind to the proposing reviewer's rationale when possible.

## Consolidation

1. Normalize locations and root causes.
2. Deduplicate only identical `(contract, function, mechanism)` tuples.
3. Preserve distinct remediation options and contradictory evidence.
4. Run every surviving candidate through `core/06-validation.md` and
   `core/08-judge.md`.
5. Emit a completeness line: every lead is validated, killed, known, or
   deferred with a receipt.

Reviewer count is not evidence quality. A unanimous conclusion with no proof is
still a lead; a single reproducible PoC can outweigh many speculative alerts.
