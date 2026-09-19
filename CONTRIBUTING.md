# Contributing

AuditSharingan is maintained by [@itsdarktoday](https://github.com/itsdarktoday)
and [@0xscarfac3](https://github.com/0xscarfac3). Pull requests and focused
issue reports are welcome at
<https://github.com/itsdarktoday/auditsharingan>.

Contributions should improve the quality, reproducibility, or boundaries of
the AuditSharingan workflow without turning heuristic output into a claimed
finding.

Before opening a pull request:

1. Run `python3 -B scripts/release_check.py`.
2. Run the relevant unit, fixture, Foundry, or tool-specific checks.
3. Describe changed assumptions, supported tool versions, and any capability
   gaps.
4. Update the relevant schema, template, pattern, or regression fixture when
   behavior changes.

New detectors should produce leads with provenance and should not silently
claim coverage when a required tool is missing. New report fields must remain
backward-compatible with the schemas or include a deliberate schema update.
Avoid committing generated audit artifacts, secrets, target repositories, or
private deployment data.
