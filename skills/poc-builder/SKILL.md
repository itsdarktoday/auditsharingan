---
name: poc-builder
description: Exploit PoC construction sub-skill for the ultimate-web3-security pipeline. Turns a validated attack hypothesis into an executable Foundry test (unit or mainnet-fork). Loaded by Phase 6 (Exploit Validation).
---

# PoC Builder (Foundry / Fork)

Turns a validated hypothesis into executable proof. Loaded in Phase 6 for serious candidates.

## Reading order (anti-anchoring)

Before writing the PoC, re-read: (1) the target contract code, (2) its dependencies actually on the path, (3) the deployment config. Do NOT re-read your own hypothesis notes first — derive the exploit from the code to avoid anchoring to a wrong assumption.

## Finding classification (choose the PoC type)

- **(a) Pure logic bug** (broken invariant in fresh code): unit-level Foundry test with mocks is acceptable — the exploit holds in any deployment.
- **(b) State/deployment-dependent bug** (needs real tokens, real pools, real oracle config): fork test against the deployed addresses. Mocks can CONFIRM a finding but never REFUTE it — a mock-based failure does not kill a candidate; only a real-path failure does.

## Fork test setup

```solidity
// 1. Pin the block at the top of the test:
vm.createSelectFork(vm.envString("ETH_RPC_URL"), BLOCK_NUMBER);
```

- Pin a specific block for reproducibility; document the block number.
- Use the real deployment addresses from recon (Phase 1). Verify on-chain state (balances, roles, oracle prices) before attacking.
- **Funding rule**: fund the attacker via `deal` ONLY when the attack path in production doesn't depend on how the attacker obtained funds. If the finding is about capital requirements, fund realistically or note the assumption. Never `prank` a contract into sending funds the real contract wouldn't send.
- Snapshot/rollback (`vm.snapshotState`/`revertToState`) between steps where useful, but the FINAL proof run must be the clean sequence.

## PoC structure (canonical sequence from core/06)

```
attacker setup → initial state → tx 1 → tx 2
→ manipulation → state violation → asset extraction / impact → final state
```

Encode each step as a clearly named function or `console.log` section; assert the state violation (`assertEq`/`assertLt` on balances/state) and the profit at the end.

## Proof-of-loss discipline

- Record before/after balances of the VICTIM, not just the attacker.
- Assert the specific invariant broken (`INV-x`) with a comment quoting it.
- If the exploit requires multiple txs or waiting, simulate time via `vm.warp`/`vm.roll` — but note where real-world timing constraints apply.

## Output

`{AUDIT_DIR}/poc/<finding-slug>/Exploit.t.sol` + `README.md` with:

- one-line root cause,
- exact run commands (`forge test --match-path ... -vvvv --fork-url $ETH_RPC_URL --fork-block-number N`),
- expected output (which asserts pass),
- any assumptions (funding, timing, config).

A PoC that does not reproduce under the clean sequence is NOT a PoC — go back to Phase 6 kill-gates.
