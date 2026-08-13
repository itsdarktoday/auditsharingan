---
name: zk-audit
description: ZK circuit (Circom) deep-analysis sub-skill for the ultimate-web3-security pipeline. Loaded by the master skill when the target is a ZK circuit. Threat model: soundness / completeness / privacy.
---

# ZK Circuit Audit (Circom)

Loaded when the target is a Circom circuit (or ZK proof system glue). The core pipeline applies, but the reasoning model changes fundamentally.

## The declarative doctrine

**Circom is declarative, not imperative.** There is no execution order to exploit — there is only the set of constraints and the space of witnesses that satisfy them. The senior auditor's question is never "what does this line do?" It is always:

> **"What does the constraint system still ALLOW?"**

Every `===` / `<==` constrains; every `<--` / `-->` is witness-only (unconstrained); `assert(...)` is a compile-time check the verifier never sees.

## Threat model

- **Soundness break**: a malicious prover crafts a witness/inputs that satisfy the R1CS but violate the protocol's intended semantics, AND a verifier accepts the resulting proof.
- **Completeness break**: an honest prover gets bricked (DoS of users).
- **Privacy break**: the verifier learns a function of private inputs (e.g., public signals leak entropy).

Gate the pipeline on these three; a "vulnerability" that breaks none of them is not a circuit vulnerability.

## Code-shape triggers (grep-first)

| Shape | Ask |
|---|---|
| Every `<--` | Is its output constrained anywhere? ("Every `<--` is a constraint hole until proven otherwise.") |
| `LessThan(N)` | Operand must come from a `Num2Bits(M ≤ N)` chain. |
| `Num2Bits(254)` over BN254 | Needs `_strict` or an alias check (`x` vs `x + p`). |
| Division `<-- a / b` | Needs `IsZero(b).out === 0` upstream — witness-only division collapses to `0 === 0` when b=0. |
| `Mux*` selectors | Need `s * (s - 1) === 0` upstream. |
| Public inputs | Every public input must appear in ≥1 `===` / `<==` constraint (linear "dummy use" is optimized away by `circom -O2`). |
| `in[i] <--` with lookups | Out-of-bounds indices / unconstrained lookups. |
| Signature/Merkle gadgets | Enforce only what their body constrains — every precondition (on-curve, in-subgroup, < order, fixed depth, domain tag) is the CALLER's job until proven. |

## Weaponization / propagation rule

If you find that a library template (e.g., `circomlib.MontgomeryAdd`) is unsound under some input (`in[0] == in[1]`), then **every template that calls it (directly or transitively) inherits the bug**. Trace callers, don't stop at the library.

## Mental-tool protocol (mandatory markers)

- `[Feynman: <Template>]` — explain in plain English what the template proves; wherever the explanation gets fuzzy = unconstrained signal.
- `[Socratic: file:line]` — on unclear constraints; drill why each `===` exists.
- `[Inversion: <Template>]` — give concrete malicious-prover values (`in = p - 1`), not abstractions.

## Judge stanzas (circuit-specific gates)

- **G2 attack execution**: a finding fails ONLY when a specific constraint on the witness path provably pins the value the attacker needs free. "The witness generator only emits canonical values" → **clears** — witness generators do not constrain the prover; only the R1CS does.
- **G3 trusted-party demotion**: setup/designated-prover harms are demoted unless an unprivileged amplifier is named (toxic-waste leak, designated-prover gap via public entry, setup-assumed invariant any prover can violate).
- **G5 impact**: soundness = theft of verifier-trusted state; completeness = honest-user brick; privacy = selective disclosure.

## Tools

- `circom` compile + `snarkjs` for witness generation and constraint inspection; `circomspect` static analyzer when available (alerts = leads); write a malicious witness for any soundness hypothesis (that IS the PoC).
