# Historical evaluation snapshot

Run date: 2026-08-13. This is a recorded regression result, not an
independent certification and not a guarantee of future performance.

## Internal corpus

The author-run snapshot reported 8 planted vulnerable fixtures correctly
identified and 3 clean fixtures cleared. Four vulnerable cases had executable
PoCs; the remaining cases were trace-level. The result is useful as a known-
class regression baseline, but it is subject to evaluator and corpus bias.

## External corpus

The recorded run reported 11 vulnerable and 7 benign neutral-ID fixtures
classified correctly. Evidence was trace-level for the external cases, and
the EVM examples were minimal reproducers rather than complete live protocols.

## Interpretation

These numbers measure a small, selected corpus and should not be converted
into a general precision/recall claim. Re-run `evals/score.py` after every
methodology change, disclose the exact prediction file, and include misses and
false positives in the release notes.
