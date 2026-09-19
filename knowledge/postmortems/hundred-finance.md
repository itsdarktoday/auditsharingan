# Hundred Finance — callback and exchange-rate accounting pattern

- **Archetype:** lending market / callback-enabled token
- **Root cause pattern:** token callback behavior interacted with exchange-rate and redemption accounting before the market had fully settled its state.
- **Invariant:** a redemption or transfer callback cannot obtain multiple claims against the same underlying balance.

## Audit trigger

Run the accounting sequence with standard, fee-on-transfer, rebasing, and callback-enabled tokens. Check whether exchange rates are read before balances and supply are updated.

## False-positive boundary

Promote the lead only when the exact token behavior is supported, the re-entry path is reachable, and the resulting asset delta is borne by other users or the protocol.

