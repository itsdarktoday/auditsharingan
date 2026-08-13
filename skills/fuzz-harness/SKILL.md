---
name: fuzz-harness
description: Invariant-driven fuzzing sub-skill for the ultimate-web3-security pipeline. Builds stateful fuzz harnesses (Echidna/Medusa for EVM, Trident for Solana) from the protocol invariants extracted in Phase 2. Loaded in Phase 4/6 for invariant-class analysis.
---

# Fuzz Harness (Invariant Testing)

Turns `INV-x` invariants into executable fuzz properties. Loaded when the protocol has extractable invariants (accounting-heavy protocols) and the effort mode allows dynamic analysis.

## When to fuzz

- The protocol has money-map invariants (`totalX == Σ userX`, solvency, exchange-rate monotonicity).
- You want to find state sequences that break an invariant — sequences manual reasoning may miss.
- Not for: pure access-control bugs (fuzzers find these poorly), one-shot init bugs, or things requiring specific timestamps.

## Mechanical tooling (`{SKILL_DIR}/scripts/`)

- `ensure_foundry.sh <PROJECT_ROOT>` — verify forge/foundry.toml/forge-std present (exit 1 with install guidance).
- `generate_suite.js` / `generate_handlers.js <PROJECT_ROOT> --suite-dir <dir> --meta-dir <dir>` — scaffold the harness dir and pre-populated handler stubs with correct signatures/type mappings (refine the stubs manually per handler-pattern rules below).
- `setup_fuzz_profile.sh <PROJECT_ROOT>` — add `[profile.fuzz]` (via_ir=false) when the project uses via_ir, so Medusa coverage isn't deflated (prints `FUZZ_PROFILE=no-ir|ir-no-opt|default`).
- `run_medusa.js <PROJECT_ROOT> --meta-dir <dir> --coverage-mode` / `run_echidna.js ...` — wrapped campaign runners with log files + plateau detection. Run asynchronously via the agent runtime, never with shell backgrounding.

## Invariant extraction

From Phase 2's `INV-x` list, formalize each as a checkable property:

- **Global property** (`property_xxx() returns bool`): e.g., `return totalAssets >= totalShares_implied` — checked by the fuzzer after every call.
- **Inline assertion** (`t(...)` / `assert(...)` inside handlers): fired mid-call, e.g., assert exchange rate didn't decrease after a deposit.
- Prioritize: conservation (tokens in = tokens out), solvency, monotonicity, roundtrip (deposit→withdraw ≈ lossless), rounding bounds (share value never decreases below X).

## Harness structure (EVM / Echidna-Medusa)

```
test/fuzz/
├── Base.sol            # deployment + actors + seeded balances (mirror real deploy scripts)
├── Handlers.sol        # inherits per-contract handlers
├── handlers/<Contract>Handler.sol
├── Properties.sol      # property_xxx() functions
└── *.yaml              # echidna.yaml / medusa.json
```

- **Actors**: ≥3 fuzzer addresses (`0x10000`, `0x20000`, `0x30000`) mapped to roles (user, attacker, keeper); handlers pick callers via fuzzer input.
- **Clamp inputs semantically**: amounts bounded to realistic ranges; avoid `assume()` on the critical path (each excluded class = unexplored attack space).
- **Boundary stress variants**: dust deposits, max approvals, 0-amount, token with 2 decimals, fee-on-transfer mock (if arbitrary tokens in scope).
- **Setup must mirror the real deployment** (same constructor args, same initial balances) — a harness that deploys a different config proves nothing.

## Running

- Echidna: `echidna . --contract FuzzTester --config echidna.yaml` (fast iteration, shrink).
- Medusa: `medusa fuzz` (parallel, coverage reports). Check coverage: core protocol contracts 80%+ (via_ir can deflate coverage — set a fuzz profile with `via_ir = false` or adjust targets).
- Solana: Trident — `trident fuzz run <target>` with an invariant-test scaffold (`#[invariant]` checks).

## Violation triage (do not report raw fuzz output as a finding)

1. **Reproduce** the failing sequence in a Foundry unit test (`test_repro_<property>`); shrink it manually to the minimal steps.
2. **Classify** the violation: real invariant break vs harness artifact (bad clamp, wrong initial state, property bug). Re-check the property against the protocol docs.
3. **Sensitivity/durability**: does the break depend on a single exact input? Perturb amounts ±10% — a real bug survives perturbation; a boundary artifact often doesn't.
4. If real → feed back into `leads.md` as a lead with the sequence; run it through the Phase 5 hypothesis template and the rest of the pipeline like any other lead.

## Output

`{AUDIT_DIR}/fuzz/` — harness, configs, `PROPERTIES.md` (property ↔ INV-x mapping), `VIOLATIONS.md` (triaged violations with minimal sequences), coverage summary.

## Blind spots (state in the report)

Fuzzers prove violations exist, never that they don't. Coverage < 100% means unexplored paths. Time-box campaigns (default: 15–30 min property) and note the bound.
