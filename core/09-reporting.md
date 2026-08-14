# Phase 11 — Final Report

Goal: concise, evidence-backed, reproducible findings. Output: `{AUDIT_DIR}/report.md` (optionally also `{TARGET}/SECURITY_REPORT.md`).

## 11.1 Finding format

Per validated finding (use `templates/finding.md`):

```
Title
Severity          (recalibrated)
Confidence        (band + score)
Root Cause
Affected Components
Attack Path       (attacker → harm, step by step)
Impact            (WHO loses WHAT, quantified where possible)
Exploitability    (attacker requirements, capital, prerequisites, repeatability)
Proof / PoC       (code pointer + exact rerun commands)
Why Existing Checks Do Not Prevent It
Recommended Fix   (minimal, concrete; alternative fixes labeled Option A/B when distinct)
Prerequisites
Status            (NEW / KNOWN)
```

## 11.2 Report structure (use `templates/report.md`)

1. **Executive summary** — protocol, approach, findings table (severity/confidence), top risks.
2. **Scope & methodology** — files audited, phases run, tools run, coverage data, effort mode, out-of-scope items.
3. **Findings** — validated findings by severity, template format. Only validated findings here.
4. **Leads** — unvalidated, high-signal trails for manual follow-up (no confidence, no fix).
5. **Informational & governance observations** — centralization, missing events, admin powers by design.
6. **Validation log** — killed candidates with kill reason (brief, one line each).
7. **Appendix** — reproducibility commands, knowledge patterns extracted.

## 11.3 Honesty rules

- No speculative claims; no manufactured findings. **"No valid vulnerability found" is a successful outcome when the evidence supports it** — but it is only credible when it comes with the receipts:
  - the completeness line from Phase 10 (`Completeness: N leads, N covered...`) is printed in the report,
  - the **leads section lists every surviving lead** with what remains unverified,
  - the validation log shows what was checked and killed, with kill reasons.
  - A report with zero findings AND zero leads means the audit did not engage — go back to Phase 4 and re-run the accounting lens.
- Every severity claim justified in one line from the verified path.
- State confidence and open questions explicitly; never hide uncertainty.
- Do not report: linter/compiler issues, gas micro-optimizations, naming, NatSpec, admin privileges by design (without amplifier), missing events alone, centralization without an exploit path, implausible preconditions.

## Output

`report.md` per above structure.

## Exit gate

Every validated finding has all template fields; honesty rules reviewed one by one.
