# Nomad Bridge — default-root authentication pattern

- **Archetype:** cross-chain message verification
- **Root cause pattern:** an initialization/upgrade state made a default or zero-valued root acceptable as if it were an explicitly confirmed root.
- **Invariant:** only a non-default root that was independently accepted by the intended verification process can authorize a message.

## Audit trigger

Inspect zero values, mappings with implicit defaults, upgrade initialization, root freshness, domain separation, and the ordering of “accepted” writes relative to message execution.

## False-positive boundary

A zero sentinel is safe only when it is rejected on every authorization path and cannot be written as a valid root through an upgrade or initialization sequence.

