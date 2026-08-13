# Pattern Index

Trigger keywords → pattern file. Consulted in Phase 1.3 (prior-art) and Phase 4 (lens dispatch). Grows during Phase 12.

## EVM — reentrancy & external calls

- `read-only reentrancy`, `view after external call`, `oracle snapshot`, `Balancer-style` → `patterns/evm/reentrancy-read-only.md`
- `cross-function reentrancy`, `nonReentrant missing`, `callback`, `ERC-777`, `transitive reentrancy` → `patterns/evm/reentrancy.md`

## EVM — accounting

- `totalX == Σ userX`, `accounting desync`, `missing decrement`, `one-sided write`, `claim twice` → `patterns/evm/accounting-desync.md`
- `share inflation`, `first depositor`, `donation attack`, `totalAssets`, `rounding` → `patterns/evm/rounding-share-inflation.md`
- `fee-on-transfer`, `balanceOf vs amount`, `transferFrom accounting`, `rebasing`, `blacklisting`, `no return value` → `patterns/evm/tokens-erc-deviations.md`

## EVM — oracle & pricing

- `spot price`, `TWAP`, `latestRoundData`, `staleness`, `flash loan manipulation` → `patterns/evm/oracle-manipulation.md`

## EVM — access control & upgradeability

- `missing modifier`, `role confusion`, `ownership transfer`, `tx.origin`, `init abuse` → `patterns/evm/access-control.md`
- `storage collision`, `proxy slot`, `upgrade`, `beacon`, `UUPS` → `patterns/evm/storage-collision.md` + `patterns/evm/upgradeability.md`
- `uninitialized`, `front-run initialize`, `implementation init` → `patterns/evm/init-front-run.md`

## EVM — signatures & governance

- `replay`, `EIP-712`, `chainId`, `permit` → `patterns/evm/signature-replay.md`
- `voting manipulation`, `quorum`, `timelock`, `delegation`, `emergency` → `patterns/evm/governance.md`

## EVM — liquidation, DoS, MEV, composability, cross-chain

- `liquidation DoS`, `unliquidatable`, `bad debt` → `patterns/evm/liquidation-dos.md`
- `permanent lock`, `gas exhaustion`, `unbounded loop`, `griefing` → `patterns/evm/dos-griefing.md`
- `sandwich`, `front-running`, `slippage`, `MEV` → `patterns/evm/mev-frontrunning.md`
- `external protocol integration`, `hooks`, `cross-protocol assumption` → `patterns/evm/composability.md`
- `bridge`, `relayer`, `message replay`, `chainid` → `patterns/evm/cross-chain.md`

## Solana

- `reload after CPI`, `stale account`, `CPI` → `patterns/solana/cpi-reload.md`
- `duplicate mutable account`, `from == to`, `account confusion` → `patterns/solana/duplicate-mutable-account.md`
- `PDA seeds`, `bump`, `signer`, `owner`, `reinit`, `remaining_accounts` → `patterns/solana/account-validation.md`
- `reward debt`, `share price`, `lamports`, `overflow` → `patterns/solana/economic-accounting.md`

## Move

- `capability store`, `Cap transfer`, `signer` → `patterns/move/capability-store.md`
- `capability burn/reissue`, `freeze`, `transfer policy`, `witness` → `patterns/move/capabilities.md`
- `UID/ID`, `dynamic fields`, `clock/epoch`, `abort-before-checkpoint` → `patterns/move/object-model.md`
- `PTB`, `check-vs-settlement`, `stale package` → `patterns/move/defi-timing.md`

## ZK

- `under-constrained`, `alias`, `division`, `Mux selector`, `public input` → `patterns/zk/soundness.md`
- `over-constraint`, `privacy leak`, `trusted setup` → `patterns/zk/completeness-privacy.md`
