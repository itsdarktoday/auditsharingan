# Knowledge base

This directory stores reusable vulnerability patterns and postmortems. The
knowledge stage reads it during prior-art checks and lens dispatch, then adds
validated lessons from later audits.

## Pattern format

Each file under `patterns/<chain>/<pattern-name>.md` should cover one root
cause:

```text
# pattern-name (chain)

root cause: what the code author got wrong
protocol type: vault / lending / DEX / bridge / staking / auction / perp / ...
affected architecture: shares accounting, proxy storage, keeper liquidation, ...
attack preconditions: state or capability the attacker needs
invariant violated: the broken INV property
exploit pattern: the concrete attack sequence
detection strategy: code shapes, triggers, or tools
false-positive indicators: when similar code is safe
example PoC: a real audit path or "none yet"
```

Keep patterns focused and under 60 lines when practical. Cite a real finding
or PoC when one exists. A pattern is a review prompt, not a verdict. Matching
code earns a closer look and nothing more.

## Index and maintenance

`index.md` maps trigger keywords to pattern files by chain and family.

Add validated findings and reusable false-positive lessons. Merge variants into
an existing family when they share the same root cause. Do not add a pattern
just because a scanner emitted a lead.
