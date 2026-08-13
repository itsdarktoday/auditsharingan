# EVM Attack Catalog

Load-on-trigger reference for lens dispatch. Each entry: **Trigger** (code shape), **Attack shapes** (what to hypothesize), **Prove** (minimum evidence), **FP indicators** (when to drop). A finding without the "Prove" column is a lead, not a finding.

## REENTRANCY

**Trigger**: external call before state update (violates checks-effects-interactions); token hooks (ERC-777, ERC-1155); callbacks to user-controlled contracts; cross-function state reads after external calls.

**Attack shapes**: single-function reentrancy (deposit/withdraw) · cross-function reentrancy (shared state updated in a different function) · **read-only reentrancy** (view function reads inconsistent intermediate state after an external call — e.g., price/oracle snapshot poisoned mid-update; the "Balancer-style" class) · transitive reentrancy (A→B→...→X calls back into any contract in the chain).

**Prove**: name the callback-capable token/contract in scope; show the external call occurs before the violating state update; show the reentered function reads the inconsistent state; impact premise.

**FP indicators**: `nonReentrant` on both the calling and reentered function (single-function class gone; cross-function survives) · no callback-capable token in the whitelist · reentered state already updated before the call (CEI satisfied).

## ACCOUNTING DESYNC (money map drift)

**Trigger**: value movement (transfer/mint/burn/claim) without a matching tracked-total update; update in only one branch; `+=` where `-=` should pair; interest/reward accrual applied asymmetrically (debt rounds up, supply rounds down is CORRECT — inverted is the bug).

**Attack shapes**: withdraw without decrementing `totalX` · deposit credited twice (fee-on-transfer: credit `amount` but only `amount - fee` arrived) · claim reset before/after transfer mismatch · share inflation via donations (first-deposit or direct token transfer inflating `totalAssets` vs `totalSupply`) · per-token accounting where a global variable is assumed.

**Prove**: trace the value out and the tracking variable in the same branch; quantify the drift (who gains, who loses); loop-ability for rounding classes.

**FP indicators**: drift is compensated elsewhere (reconciliation function) · only affects the caller (self-harm) · requires admin config that is timelocked and validated.

## ROUNDING / PRECISION

**Trigger**: `mulDiv`, integer division, share math, exchange rates, reward distribution, `1e18` scaling, multiple decimals interacting.

**Attack shapes**: round-down donation to protocol (protocol-favoring, compounding) · zero-amount share mint (round to 0) · precision loss when token decimals ≠ 18 · first depositor inflation (mitigated by MINIMUM_LIQUIDITY — check for its absence in custom vaults) · compounding rounding drained per-tx (loop-able dust).

**Prove**: numeric trace with concrete values; show compounding or loop-ability; identify victim. A rounding error is only Low if it cannot be looped — check that first.

**FP indicators**: one-time dust < gas cost · consistent protocol-favoring rounding with no compounding · MINIMUM_LIQUIDITY present · precision explicitly documented as accepted.

## DONATION / INFLATION

**Trigger**: vault-style `totalAssets = balanceOf(this)` accounting; shares derived from balances; reward accrual based on raw balances.

**Attack shapes**: donate tokens to inflate total assets before a victim's deposit/withdraw (skew shares) · inflate reward rate then harvest · griefing share price to zero (rounding) · front-run inflation of exchange rate between oracle update and settlement.

**Prove**: show the donated asset feeds the same `totalAssets` the victim's shares use; quantify victim loss; check first-deposit protection.

**FP indicators**: virtual/offset accounting (Uniswap v3-style) · internal balance ledger instead of raw balances · donations are not counted until accrual.

## ORACLE / PRICING

**Trigger**: spot price reads (`getReserves`), short TWAP windows, `latestRoundData` without staleness, missing decimals conversion, fallback oracle logic, user-supplied price parameters.

**Attack shapes**: same-tx spot manipulation via flash loan · stale Chainlink feed (no `updatedAt`/heartbeat check, or zero price) · decimals mismatch (8 vs 18) · TWAP window too short → sandwichable · oracle switch/fallback manipulation · price used at deposit vs withdraw asymmetry.

**Prove**: name the pool and capital needed to move the price X%; show the path uses the manipulated value; quantify the impact.

**FP indicators**: 30-min+ TWAP on deep pools · staleness checks present with correct heartbeat · oracle admin action requiring governance · manipulation cost exceeds profit (show the math).


## LIQUIDATION

**Trigger**: liquidation functions, health-factor math, keeper incentives, auction logic, bad-debt paths.

**Attack shapes**: liquidation DoS (fee-on-transfer collateral breaks `transferFrom` exact math; blacklisted positions; gas griefing of auction) · unfair liquidation pricing (spot price at liquidation, stale oracle) · self-liquidation profit (attacker liquidates own position at manipulated price) · bad-debt accrual when liquidation fails · wrong collateral accounting during partial liquidation.

**Prove**: show the position becomes unliquidatable or the liquidation price is manipulable; identify who eats the bad debt.

**FP indicators**: keeper-incentivized with caps · TWAP-protected liquidation prices · dust positions only.

## SIGNATURES / PERMITS

**Trigger**: `ecrecover`, EIP-712 `_hashTypedDataV4`, permit flows, meta-transactions, off-chain order matching.

**Attack shapes**: replay across chains (missing chainId in domain) · EIP-712 typehash wrong (struct mismatch → cross-protocol signature reuse) · malleability (`v` normalization) · permit + fee-on-transfer (approval amount ≠ received amount) · signature replay within protocol (missing nonce/deadline) · order hash ambiguity (colliding encodings).

**Prove**: show the exact message an attacker reuses and where; for cross-chain: name the second chain where the domain is valid.

**FP indicators**: chainId + verifyingContract + nonce + deadline all present · malleability irrelevant for the use · signatures one-shot (consumed by nonce).

## UPGRADEABILITY / PROXY

**Trigger**: proxies (Transparent/UUPS/Beacon), `delegatecall`, storage layout, initializers, `selfdestruct`.

**Attack shapes**: storage collision between implementation versions · uninitialized implementation (anyone can call `initialize` on the logic contract) · UUPS `upgradeTo` missing auth in implementation · initializer missing `initializer` modifier / double-init · `_disableInitializers()` absent · delegatecall to user-supplied address · storage gaps missing across upgrades.

**Prove**: show the collision (slot map) or the uninitialized state is reachable on-chain; for init abuse: show the function is callable by anyone and corrupts state.

**FP indicators**: ERC-7201 namespaced storage · `_disableInitializers()` in constructor · UUPS auth in implementation verified · fresh deployment (no upgrade history to collide).

## GOVERNANCE

**Trigger**: vote/propose/execute, delegation, quorum math, timelock, emergency functions.

**Attack shapes**: voting manipulation (flash-loan votes — vote weight from transferable balance; delegation to self) · quorum bypass via stale snapshots · timelock bypass (execute without delay) · emergency powers without constraints · proposal execution reentrancy.

**Prove**: show vote weight acquisition and the malicious proposal's effect; check snapshot logic (balance-at-block vs current).

**FP indicators**: votes snapshotted at proposal block · timelock enforced in `execute` · emergency powers documented and time-boxed.

## DOS / GRIEFING

**Trigger**: loops over attacker-influenced arrays, pull-based withdrawals, auction settle functions, unbounded arrays, external calls in loops.

**Attack shapes**: permanent lock of user funds (blocked withdrawal by a single griefing actor) · gas exhaustion of keeper functions (liquidation/auction) · state bloat · attacker-controlled iteration length · griefing all users of a critical function.

**Prove**: show the concrete griefing sequence and who is locked out; DoS of ALL users of a critical lifecycle function → HIGH; per-user → MEDIUM.

**FP indicators**: bounded arrays with caps · permissioned iteration · fallback paths.

## CROSS-CHAIN / BRIDGE

**Trigger**: message passing, relayers, `sendMessage`/`receiveMessage`, token bridges, `block.chainid` checks.

**Attack shapes**: message replay (missing nonce/hash consumption) · ordering manipulation · relayer trust assumptions (single relayer can grief) · token address collision across chains · `chainid` missing in signed messages · reentrancy on message execution · accounting desync between locked/minted totals.

**Prove**: show the replay or the desync with the cross-chain totals; identify which chain's users lose.

**FP indicators**: consumed message hashes · canonical token addresses per chain · multi-relayer with dispute.

## INITIALIZATION

**Trigger**: `initialize` functions, `constructor` vs init split, proxies, clone/factory patterns.

**Attack shapes**: anyone initializes before deployer (front-run) · double initialization · initialize on the implementation contract · factory mis-configures children · missing init guard on critical roles.

**Prove**: show the uninitialized state is observable on-chain (e.g., via storage read or call) and initializable by an attacker.

**FP indicators**: `initializer` modifier + `_disableInitializers()` · initialization in the same tx as deployment (CREATE2 factory) · verified deployer tx order.
