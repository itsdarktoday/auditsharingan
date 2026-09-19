# Euler Finance — accounting and health-check pattern

- **Archetype:** lending / CDP
- **Root cause pattern:** a collateral/debt transition allowed an account to become unhealthy without enforcing the health invariant on that path.
- **Invariant:** an account cannot reduce backing collateral or increase effective debt past its liquidation boundary without a corresponding solvency check.

## Audit trigger

Whenever a protocol has donation, reserve, transfer, liquidation, or internal-balance operations, compare every path that changes collateral or liabilities. A function name that sounds administrative does not remove the need for the same health check.

## Attack shape

1. Acquire or mint a leveraged position.
2. Invoke the path that changes collateral accounting while omitting the health check.
3. Leave the account with under-collateralized debt.
4. Use liquidation or another withdrawal path to transfer real collateral while bad debt remains socialized.

## False-positive boundary

Do not report a missing check if the called function cannot reduce collateral, the position is atomically closed, or a later checked transition makes the state unreachable. Prove the state transition and victim loss.

## Defensive test

Fuzz every collateral-reducing operation from healthy, borderline, and already-liquidatable states. Assert that the aggregate collateral/debt invariant holds after each successful operation.

