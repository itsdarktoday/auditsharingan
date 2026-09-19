# Wormhole — guardian verification and upgrade pattern

- **Archetype:** cross-chain message authentication
- **Root cause pattern:** a message verification or upgrade path failed to bind execution to the intended guardian set and verification state.
- **Invariant:** message execution requires a valid quorum for the correct domain, guardian set, and message digest.

## Audit trigger

Check deprecated instruction paths, guardian-set rotation, signature-count thresholds, replay keys, domain separation, and upgrade initialization. Test old and new verification entry points together.

## False-positive boundary

An unconstrained account or deprecated function is a lead until the attacker can use it to satisfy quorum or authorize a victim asset transfer.

