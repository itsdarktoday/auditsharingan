# Radiant Capital — empty-market share-rate pattern

- **Archetype:** lending market / exchange-rate accounting
- **Root cause pattern:** initial market state, decimal conversion, and donation-sensitive exchange-rate math allowed a small initial position to distort later share/value conversions.
- **Invariant:** exchange-rate updates must remain bounded by actual cash, debt, reserves, and total supply; a donation cannot grant an attacker control over unrelated users' credit.

## Audit trigger

Test empty and near-empty markets, one-unit deposits, direct token transfers, decimal conversions, and borrow capacity immediately after a rate change.

## False-positive boundary

A high exchange rate is not itself a bug. Prove that the rate creates unauthorized borrow power or a victim loss and that the attacker can realize it after fees and repayment.

