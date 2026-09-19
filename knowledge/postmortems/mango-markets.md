# Mango Markets — thin-oracle economic pattern

- **Archetype:** perpetuals / margin lending
- **Root cause pattern:** manipulable or thin-market pricing influenced unrealized profit and borrowing capacity faster than the system could constrain exposure.
- **Invariant:** collateral value and borrow capacity must be based on a manipulation-resistant price and conservative liquidity assumptions.

## Audit trigger

Model price impact, available liquidity, oracle update rules, mark/index divergence, and whether unrealized PnL can be reused as collateral in the same transaction.

## False-positive boundary

A price can move without creating a vulnerability. Quantify capital required, exit liquidity, oracle reaction, liquidation path, and actual protocol loss.

