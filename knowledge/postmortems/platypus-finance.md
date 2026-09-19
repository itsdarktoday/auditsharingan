# Platypus Finance — emergency withdrawal and solvency pattern

- **Archetype:** stableswap / collateralized debt
- **Root cause pattern:** an emergency withdrawal path returned collateral without enforcing the debt relationship that normally made the collateral encumbered.
- **Invariant:** collateral backing outstanding debt cannot be withdrawn without repaying, transferring, or otherwise settling that debt.

## Audit trigger

Audit pause, emergency, migration, rescue, and shutdown functions with the same rigor as normal withdrawals. Compare their debt and ownership checks line by line.

## Attack shape

1. Deposit collateral and borrow against it.
2. Enter the emergency path or satisfy its pause predicate.
3. Withdraw the collateral while keeping the debt.
4. Leave the protocol with an unbacked liability.

## False-positive boundary

Do not report a bypass if the emergency path burns the debt claim, transfers the debt atomically, or is only callable after a trusted governance settlement that is explicitly in scope.

