---
name: solana-audit
description: Solana/Rust (Anchor + native) deep-analysis sub-skill for the ultimate-web3-security pipeline. Loaded by the master skill when the target is a Solana program.
---

# Solana Audit

Loaded when the target is a Solana program (Anchor or native Rust). The core pipeline (recon → model → threat → analysis → judge) applies unchanged; this file supplies the Solana-specific lenses and checks. Findings still pass the core judge gates.

## Solana threat-model notes

- **No shared memory between instructions** — cross-instruction state lives in accounts. Every invariant is "which account fields must equal which other account fields".
- **Attacker profiles**: same six, plus: anyone can call any instruction with any account set they can construct (account data + owner checks are the authorization boundary — the program is the only code that can enforce them).
- **CPI (cross-program invocation) trust**: the program you invoke is a trusted dependency — its *callers* are not. An attacker can invoke your program via an intermediate program.

## Account validation checklist (the #1 Solana bug class)

For EVERY instruction:

1. **Signer** — which accounts must sign? `#[account(signer)]`/`Signer` for authority, payer, fee recipients.
2. **Owner** — token accounts must be `spl_token::ID` (or token-2022); mint owner checks; program-owned accounts must be PDA-owned by THIS program (`#[account(owner = crate::ID)]`).
3. **PDA seeds + bump** — verify bump against `ProgramDerivedAddress` / `bump_seed` constraint; validate ALL seed contents (missing seed validation = PDA hijack: attacker derives the same PDA with different remaining data).
4. **Duplicate mutable accounts** — the SAME account passed twice as mutable (e.g., `from == to` in a transfer, user == vault): the serialized checks can pass one and be overwritten by the other. Explicitly handle or reject `from == to` and repeated accounts.
5. **Type confusion via data discrimination** — check `discriminator`/account type when a program owns multiple account types.
6. **`remaining_accounts` iteration** — attacker-controlled length and contents; validate each entry before use.
7. **Sysvars** — validate clock/rent sysvar addresses when passed as accounts.
8. **`reload()` after CPI** — after any CPI that may modify an account (transfer, other programs), the local `Account` struct is STALE. Reload or re-derive before further checks. THE classic Solana bug.

## CPI checklist

- CPI target program id verified (not attacker-supplied).
- Account list ordering/duplication matches the target's constraints.
- Signer seeds for `invoke_signed` are exactly the seeds the PDA was derived with.
- No CPI into token programs with unvalidated authority (attacker-supplied authority = theft).
- After CPI: reload (above) and re-validate balances if they gate later logic.

## Rent, lamports, init/reinit

- `init` / `init_if_needed` / `realloc` / `close` safety: `close` must zero-check the destination; lamport accounting on close must not credit the wrong account.
- Reinitialization attacks: an account previously `close`d can be re-`init`ed if checks are insufficient — always require a discriminator that survives or reject re-init entirely.
- Rent-exempt enforcement for long-lived accounts; rent drain griefing.

## Token-2022 / Token Extensions (see also `references/token2022.md` patterns)

- **Transfer fees**: `transferChecked` vs `transfer` amounts differ — balance assertions must use post-fee amounts; the fee recipient can grief/drain via fee rate changes if `transfer_fee_config` authority is untrusted.
- **PermanentDelegate**: tokens can be moved without holder consent — never treat balances as commitments.
- **FreezeAuthority / MintCloseAuthority**: freeze kills withdrawal flows → DoS; `close` on mint allows reinitialize → swap/redirect attacks.
- **CloseAuthority / Confidential transfers / realloc extensions** — check extension policy per mint BEFORE trusting balances in settlement logic.
- Dual-WSOL/native handling: wrap/unwrap paths must be atomic with the settlement.

## Economic/accounting invariants

- **Reward-debt settlement**: every accrual path must (1) accrue, (2) update user's reward debt, (3) in that order, with the user's balance snapshot consistent — skips/ordering bugs = claim forever, or double-claim.
- Pool tokens: `total_shares == Σ user_shares`; deposit/withdraw symmetry incl. fees.
- Integer overflow: use checked math everywhere; Solana programs panic → tx revert, but panics in one branch can brick withdrawals.

## Judge stanzas (Solana-specific gate checks)

- Gate G2: "a specific guard interrupts" → check signer/owner/bump constraints on the actual account set.
- Gate G3: vulnerable state must exist on-chain → check the actual deployed account states/ownership.
- Admin-trust: upgrade authority actions are trusted; the finding must name an unprivileged amplifier (e.g., reinit path reachable after close, missing bump validation).

## Tools

- `cargo clippy` / `cargo audit` for baseline; Aderyn (`aderyn .`) when available; Solana program dumps (`solana program dump`) + anchor IDL diff for deployed-vs-source checks; Trident fuzzing via `{SKILL_DIR}/skills/fuzz-harness/SKILL.md`.
