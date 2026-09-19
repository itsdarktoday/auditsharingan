# Evaluation suite

These fixtures catch regressions in the AuditSharingan workflow. They measure
known bug classes and methodology behavior. They do not measure discovery of
new vulnerabilities in arbitrary production protocols.

## Corpora

- `corpus/` contains eight planted vulnerable EVM fixtures and three clean
  fixtures, including executable Foundry PoCs.
- `external/fixtures/` contains neutral IDs X01–X18 across EVM, Solana/Rust,
  and Move. Most of these cases stay at trace level because their toolchains
  may not be installed.
- Ground truth is stored in the repository for regression use. It is no longer
  a blind benchmark after a contributor reads the truth files.

## Scoring

Create one JSON prediction for each fixture:

```json
[
  {"fixture": "V01_ReentrancyVault", "verdict": "VALID", "root_cause": "reentrancy"},
  {"fixture": "C01_CleanVault", "verdict": "NO FINDING", "root_cause": ""}
]
```

Score the predictions with:

```bash
python3 evals/score.py \
  --ground-truth evals/internal-ground-truth.json \
  --predictions predictions.json \
  --output score.json
```

The scorer reports true positives, true negatives, false positives, false
negatives, precision, recall, missing predictions, and wrong-class predictions.
When publishing a score, name the fixture set, evidence level, evaluator, and
limitations.

## Regression procedure

1. Run `forge test --root evals/corpus` and retain the output.
2. Audit each fixture under a neutral name before opening its truth record.
3. Record status, root cause, severity, confidence, and evidence level.
4. Run `evals/score.py` against the predictions.
5. For every miss or false positive, update the relevant pattern, kill gate, or
   test. Do not tune the score itself.

The fixtures are small and the internal truth is author-defined. External EVM
cases are minimal reproducers. Solana and Move coverage depends on the tools
available in the test environment, and the same runtime may perform both
analysis and judging.
