# Phase 2 — Protocol Model

Goal: understand the architecture; extract assets, roles, and invariants. Output: `{AUDIT_DIR}/protocol-model.md`.

## 2.1 Read everything, verify claims

- Read ALL in-scope code before producing output. Read tests, fixtures, scripts, and configs too — they reveal developer intent, expected behavior, and what was never tested.
- Verify README/docs claims against code. Mark every discrepancy `⚠️ UNCLEAR - <what and why>`.
- Flag uncertainties rather than papering over them.

## 2.2 Money map (accounting-first)

For every value-bearing operation, answer: value enters via X, is tracked in Y, leaves via Z.

- **Assets table**: every asset (native coin, ERC20, NFT, LP position, wrapped asset) entering/leaving the protocol; who holds it; which mapping/balance tracks it.
- **Total-vs-sum invariants**: `sum(user claims) <= actual balance`, `totalX == Σ userX` — write these down per asset.
- **Fee flows**: every fee — rate, accrual point, destination.
- **Accounting-desync check**: wherever value leaves the contract, confirm the variable tracking it is decremented **in the same branch** (the classic bug: value leaves, tracked total is never decremented, or decremented in only one of two branches).

## 2.3 Entry-point classification

For every external/public non-view function:

- Access level: **permissionless** / **role-gated (name the role)** / **admin-only**. A function without a modifier but with an internal `msg.sender` check (`require(msg.sender == pendingX)`) is role-gated. `nonReentrant` is NOT access control.
- Caller (User, Keeper, Admin, LP, Relayer...), parameter trust levels (`user-controlled`, `user-signed`, `keeper-provided`, `protocol-derived`).
- Call chain: `→ Contract.fn() → Contract.fn()`; state modified (which storage vars/mappings); value flow (`in` / `out` / `none`).

## 2.4 State machines (reasoning Level 2)

For each core operation (deposit/withdraw/borrow/repay/liquidate/swap/mint/burn/stake/claim/settle/transfer/upgrade):

- Preconditions → storage changes (variable by variable) → postconditions → events.
- Note sentinel values (0 = "unset"), write-once flags gating critical logic, monotonic claim pointers, pause-state asymmetries.

## 2.5 Roles & capabilities

Every privileged role: capabilities; timelock?; multisig?; guardian?; emergency powers; upgrade rights; who can add/remove role holders; two-step transfer policy. Note which roles are **trusted by design** (they matter for the admin rule).

## 2.6 Invariants (reasoning Level 4) — the protocol's contract with itself

Extract **5–15 invariants**, each with an ID `INV-x`, in forms such as:

- `sum(user claims) <= actual token balance`
- `totalX == Σ userX`
- `index only increases` (never decreases)
- `every credited unit is debited exactly once`
- `exchange rate is monotonic between updates`
- `health factor > 1 after every user transaction`

Sources: explicit `require`/`assert` statements; invariant/property test files; docs; derived from protocol math. This list is the primary vulnerability yardstick for the rest of the audit — every candidate finding will be tested against `INV-x`.

## 2.7 Numeric grounding

For all non-trivial math (exchange rates, interest accrual, fees, rewards, liquidation): trace one example through with concrete numbers. If a formula cannot be traced numerically, mark it `⚠️ UNCLEAR`.

## Output: `protocol-model.md`

Sections: assets/money map · entry-point classification table · state machines per core operation · roles & capabilities · invariants `INV-x` · numeric traces · doc/code mismatches.

## Exit gate

Money map complete; all entry points classified; ≥5 invariants with IDs; roles table complete.
