---
name: move-audit
description: Sui/Aptos Move deep-analysis sub-skill for the ultimate-web3-security pipeline. Loaded by the master skill when the target is a Move package (object-centric runtime).
---

# Move Audit (Sui / Aptos)

Loaded when the target is a Move package. The core pipeline applies unchanged; this file supplies the object-model-specific lenses and checks. All findings still pass the core judge gates.

## Move threat model — the object-centric runtime

The runtime differs from EVM in ways that change what "state" and "authorization" mean:

- **Objects have owners**: most shared state is per-object, not global mappings. Invariants become "which fields must stay consistent on which object".
- **Authorization = capability/signer possession**, not address checks: `&signer`, capability structs (with `store` ability!), `TransferPolicy`, `FreezeCap`.
- **Programmable Transaction Blocks (PTB)**: an attacker can bundle arbitrary calls in ONE tx (up to 1024) — "atomic multi-step" is the default posture on Sui. Never assume a call happens alone. PTB repeated calls to the same function (e.g., `deposit`/`withdraw` pairs, reward claims) bypass any mental model of "one call per tx".
- **No cross-contract reentrancy** (no synchronous callback into your module mid-execution) — but PTB sequences replace it: state read in tx step N can be stale by step N+1.

## Capability & signer discipline

1. **`store` ability on capability structs** — the classic Move bug: a capability with `store` can be wrapped/transferred, breaking the "only the creator holds it" assumption. Audit every capability struct's abilities.
2. **Signer checks**: `signer::address_of` vs the expected owner; missing signer on privileged functions; signers passed via generic wrappers.
3. **Capability creation without burning the original**: minting a `Cap` but keeping an open path to mint more (e.g., re-issuing `MintCap` on upgrade, `TransferPolicy` for a frozen object).
4. **`Freeze`**: who holds `FreezeCap`; is a critical object freezable by an attacker or griefer?
5. **Dynamic fields**: keys attacker-influenced? Can an attacker add/remove dynamic fields that break lookups (dynamic field cache ceiling, `max_move_object_size` DoS)?

## Check vs settlement timing (DEFI)

The four-axis table for every value-bearing function:

| Axis | Question |
|---|---|
| Check timing | When is the precondition (balance, health, price) verified? |
| Settlement timing | When does the value actually move? |
| Oracle freshness | Which clock (`clock::timestamp_ms` vs epoch) gates it? |
| Signer binding | Is the checked party the same party that settles? |

- **Check-before-settle with a stale read**: PTB step N checks balance; step N+1's transfer uses a different source object → mismatch.
- **Signing-time policy binding**: a policy (fee rate, whitelist) read at call time can change between sign and execute — bind policies at signing or re-verify at settlement.

## Epoch/time pitfalls

- `tx_context::epoch()` vs wall-clock: tests can fast-forward epoch but not clock — test-only behavior may not match production; production logic gated on epoch is manipulable via epoch transitions (validators).
- **Abort-before-checkpoint deadlock** (DEFI-86): a multi-object transaction that aborts AFTER one object's state is committed but BEFORE a checkpoint inverts — if the abort path doesn't revert all writes, the protocol can deadlock permanently (state half-committed, no one can proceed). Audit every `assert!`/abort path for incomplete rollback.
- `clock::timestamp_ms` is miner/validator-set influenced within a window — don't use it for exact-amount fairness.

## Upgrade policy & stale packages

- **Upgrade policy** (`COMPATIBLE` vs `ADDITIVE` vs `IMMUTABLE`): what can change silently? `ADDITIVE` lets new public functions appear — can they be called with existing state in a breaking way?
- **Stale-package surface ritual** (SUI-23): on every upgrade, re-walk all functions reachable from the old package version still referenced by on-chain objects — old entry points remain callable. A fix in v2 does not protect v1 objects still pointing at v1 logic.
- Published-at address vs versioned module imports: hardcoded package IDs (self/other) can brick upgrades.

## Freeze / transfer / burn policy

- Who can freeze/transfer/burn shared objects; is the policy `TransferPolicy` correctly enforced on ALL creation paths (every `transfer::public_transfer`, every `mint`)?
- Frozen objects holding funds: any withdrawal path left? (Funds trapped = loss/DoS.)

## Accounting invariants (Move flavor)

- `totalX == Σ userX` across dynamic-field-based user state: watch for partial updates when iterating dynamic fields.
- Reward accrual: same reward-debt pattern as Solana — accrue, then update debt, same snapshot.
- Rounding in `u64` math with fee splits; donate-to-vault equivalents (Sui `Balance` donations).

## Judge stanzas (Move-specific)

- Gate G2: "specific guard interrupts" → PTB ordering counts as part of the path; a guard that only holds for single-call flows does NOT interrupt a PTB sequence.
- Gate G3: vulnerable state must exist on-chain → check published packages' version and objects' type versions.
- Admin-trust: package upgrade authority is trusted; findings need an unprivileged amplifier (e.g., stale v1 entry point still callable by anyone).

## Tools

- `sui move build`/`test` and log analysis; SUIZERO bytecode scanner when available (alerts = leads); `sui client` for on-chain object state inspection; regression matrix from the repo's own test suite + historical fixes.
