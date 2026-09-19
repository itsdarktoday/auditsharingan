# DeFi exploit pattern index

This is a compact pattern catalogue, not a claim that the package contains a complete incident database. Each summary is a trigger for source-level investigation; verify historical details against a primary incident report before citing them in a deliverable.

| Incident | Archetype | Audit trigger | Invariant | Reference |
|---|---|---|---|---|
| Euler Finance | Lending/accounting | Donation or debt-reducing paths that skip health checks | Collateral and debt remain solvent after every state transition | [euler-finance.md](euler-finance.md) |
| KyberSwap Elastic | AMM/math | Tick crossing, liquidity deltas, and rounding direction | Swap conservation and monotonic reserve accounting | [kyberswap-elastic.md](kyberswap-elastic.md) |
| Curve Vyper incident | AMM/reentrancy | Compiler-version-specific non-reentrancy behavior and callback pricing | No observable mid-update pool state | [curve-vyper-reentrancy.md](curve-vyper-reentrancy.md) |
| Platypus Finance | CDP/emergency flow | Emergency withdrawal bypassing debt or solvency checks | Collateral cannot be withdrawn while it backs debt | [platypus-finance.md](platypus-finance.md) |
| Radiant Capital | Lending/share math | Empty-market exchange rates, donation inflation, decimal mismatch | Share value and cash/debt accounting remain bounded | [radiant-capital.md](radiant-capital.md) |
| Nomad Bridge | Cross-chain authentication | Zero/default roots treated as initialized trust | Only an explicitly accepted root authenticates a message | [nomad-bridge.md](nomad-bridge.md) |
| Wormhole | Cross-chain authentication | Guardian-set verification and upgrade initialization | Every message has a valid quorum under the intended guardian set | [wormhole-bridge.md](wormhole-bridge.md) |
| Mango Markets | Oracle/economic | Thin-market oracle and unrealized PnL used as collateral | Borrow capacity follows manipulation-resistant value | [mango-markets.md](mango-markets.md) |
| Hundred Finance | Lending/reentrancy | Callback-enabled token interacting with exchange-rate accounting | Token callbacks cannot observe or reuse unsettled accounting | [hundred-finance.md](hundred-finance.md) |

## How to use this index

A matching archetype is a hypothesis only. Record the exact code path, deployment assumptions, affected victim, and proof level in the evidence ledger before promoting it.

