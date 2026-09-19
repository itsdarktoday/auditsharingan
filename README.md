<p align="center">
  <img src="assets/auditsharingan-sharingan.png" alt="AuditSharingan emblem" width="190">
</p>

<h1 align="center">AuditSharingan</h1>

<p align="center">
  Web3 security auditing skill for agents that need evidence, not noise.
</p>

<p align="center">
  <img alt="MIT license" src="https://img.shields.io/badge/license-MIT-111827?style=flat-square">
  <img alt="Python 3.10 or newer" src="https://img.shields.io/badge/python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white">
  <img alt="Agent harness agnostic" src="https://img.shields.io/badge/harness-agnostic-7C3AED?style=flat-square">
</p>

Built by `@itsdarktoday` and `@0xscarfac3`.

## What it does

AuditSharingan gives an agent one workflow for:

- Scoping the repository, build system, dependencies, tests, and tool gaps.
- Modeling actors, trust boundaries, money flows, state, and invariants.
- Finding leads across EVM/Vyper, Solana/Rust, Move, and ZK codebases.
- Turning leads into attack paths with reachability and impact math.
- Validating with traces, PoCs, fuzzing, symbolic checks, and fork tests.
- Producing reports with commands, logs, scope, assumptions, and evidence.

The useful rule is simple: a scanner can create a lead. A finding needs a
reachable attack path, a broken security property, quantified impact, and
evidence another reviewer can reproduce.

## Where it adds value

| Problem | AuditSharingan's answer |
| --- | --- |
| Scanner noise | Leads stay separate from validated findings. |
| Missed protocol context | Actors, assets, trust, state, and invariants are modeled first. |
| Weak exploit claims | High-impact issues require a PoC, checked trace, or mathematical proof. |
| Missing tool coverage | Unavailable tools and failed stages are recorded as gaps. |
| Audits that are hard to review | Every run keeps scope, commands, logs, hashes, and decisions. |

## Coverage

- EVM and Vyper: accounting, share inflation, access control, signatures,
  reentrancy, oracles, upgrades, governance, MEV, bridges, gas, L2, compiler,
  precision, and token edge cases.
- Solana and Rust: account ownership, signers, PDAs, aliasing, CPI reloads,
  `remaining_accounts`, account closure, and Token-2022 behavior.
- Sui and Aptos Move: capabilities, object ownership, PTBs, dynamic fields,
  package upgrades, timing, and balance rounding.
- ZK circuits and verifiers: constraints, hints, field aliasing, division,
  selectors, public inputs, replay, and privacy leaks.

## Use it with any agent harness

Agent Skills-compatible hosts can discover the folder from their skills path.
Custom harnesses can load the root `SKILL.md` directly and use the same files.
Keep the folder together and provide its path as `SKILL_DIR`.

```text
auditsharingan/
├── SKILL.md       workflow instructions
├── core/           audit stages
├── skills/         chain-specific guidance
├── agents/         review lenses and prompts
├── scripts/        executable audit tools
├── knowledge/      patterns and postmortems
├── schemas/        machine-readable contracts
└── templates/      report and finding formats
```

## Download

Download the repository as a ZIP and extract it, or use your Git host's clone
command. Keep the extracted `auditsharingan/` folder together.

For a local Agent Skills installation, copy the downloaded folder to:

```text
/path/to/project/.agents/skills/auditsharingan
```

For a custom harness, load:

```text
/path/to/auditsharingan/SKILL.md
```

The optional `agents/openai.yaml` file only provides interface metadata. Other
harnesses can ignore it.

## Run an audit

Ask the harness:

```text
Use the AuditSharingan workflow at /path/to/auditsharingan to audit
/path/to/protocol. Validate every candidate with reproducible evidence.
```

Or run the engine directly:

```bash
python3 /path/to/auditsharingan/scripts/auditsharingan.py \
  /path/to/protocol --standard
```

Use `--quick` for triage and `--deep` to prepare source-hashed review bundles.
The engine needs Python 3.10 or newer and has no required Python packages.

## Results

Artifacts are written to `TARGET/AuditSharingan-audit/` unless `--output-dir`
is supplied.

```text
run-manifest.json  what ran, what failed, and what was available
scope.json         source files, platforms, exclusions, and SLOC
leads.md           machine-generated leads awaiting validation
logs/              stdout and stderr for reproduction
```

## Checks

Before publishing changes:

```bash
python3 -B scripts/release_check.py
```

## Boundaries

AuditSharingan does not prove that a protocol is secure. Results depend on
scope, compiler and tool versions, deployment state, economic assumptions, and
the evidence completed by the reviewer. The workflow does not modify target
source, send transactions, use live private keys, or contact external services
without explicit authorization.

## Follow

- X: [@0xitsdarktoday](https://x.com/0xitsdarktoday)
- X: [@0xscarfac3](https://x.com/0xscarfac3)

## License

Original AuditSharingan material is MIT licensed. Third-party files in the
evaluation corpus keep their own license and attribution files.
