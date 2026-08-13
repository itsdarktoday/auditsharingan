# Phase 3 — Threat Model

Goal: define who attacks, what they control, and where they strike. Output: `{AUDIT_DIR}/threat-model.md`.

## 3.1 Attacker profiles (reasoning Level 5)

Define at least these, mapped to the concrete protocol:

- **U1 Unprivileged user** — normal accounts, no capital constraints.
- **U2 Financed adversary** — flash loans, leveraged positions, atomic multi-step (same-tx) attacks, MEV bundling.
- **U3 Malicious external protocol/token** — fee-on-transfer, rebasing, blacklisting, ERC-deviant tokens, malicious/comprised oracle, malicious hook/callback.
- **U4 Malicious or compromised insider** — admin, keeper, multisig member, relayer.
- **U5 Griefer** — no profit motive; DoS, permanent locks, gas griefing at cost.
- **U6 Cross-chain adversary** — relay/validator manipulation, message replay, ordering games (add if bridges/messaging exist).

For each: what they control, capital requirements, and — explicitly — what they **cannot** control (this bounds later hypotheses).

## 3.2 Trust assumptions

Complete the table from scoping (From → To → Assumption → Risk if broken). For each assumption, ask the breaking question: *can an unprivileged actor break this?* Examples:

- "Oracle reports sane prices" → who can move the spot pool feeding it, and for how much?
- "Keepers are honest" → what if a keeper is bribed/compromised? What invariant does that break?
- "Tokens behave per ERC-20" → which deviations are exploitable here?

## 3.3 Attack surface (complete enumeration)

Per surface: what the adversary controls (Level 5) + profit potential (Level 6).

- **Entry points & authorization** — every permissionless/role-gated function, init functions, ownership transitions.
- **External calls** — tokens, oracles, routers, callbacks, hooks: reentrancy and read-only reentrancy surface.
- **Oracle & pricing paths** — spot, TWAP, Chainlink (freshness, decimals, heartbeat), fallbacks.
- **Accounting paths** — shares, debt, rewards, fees: inflation, donation, rounding surface.
- **Liquidation & settlement** — who liquidates, with what incentives, at what price.
- **Governance & upgrades** — proposal flow, quorum, timelock, proxy admin, storage layout, emergency powers.
- **Signatures** — permits, meta-tx, EIP-712 domains, replay scope, malleability.
- **Cross-chain** — message format, ordering, replay protection, validation, fallback paths.
- **Native/asset handling** — ETH/wrapped-native handling, receive/fallback, dual-address tokens.
- **Chain-specific surfaces** — Solana: PDAs, CPIs, rent, re-init, remaining_accounts. Move: capabilities, PTB, freeze, upgrade policy, dynamic fields. ZK: constraint completeness, soundness, privacy.

## 3.4 Rank the surfaces

Rank by (reachability × impact × adversary control). The top surfaces become Phase 4 priorities.

## Output: `threat-model.md`

Sections: attacker profiles (with control boundaries) · trust-assumption break-analysis · attack-surface enumeration · ranked priority list.

## Exit gate

All 6 attacker profiles considered; trust table has a break-analysis per row; attack surface ranked.
