#!/usr/bin/env python3
"""Render a conservative, self-contained HTML report.

Finding headings accept the repository's canonical ``[H-01]`` and
``[FINDING-01]`` forms. If no finding can be parsed, the dashboard says so;
it never turns malformed input into a false "zero vulnerabilities" claim.
"""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path


HEADING = re.compile(r"^#{1,6}\s+\[((?:C|H|M|L|I|CRITICAL|HIGH|MEDIUM|LOW|INFO|FINDING)-\d+)\]\s*(.*)$", re.IGNORECASE)
SEVERITY = re.compile(r"\[(CRITICAL|HIGH|MEDIUM|LOW|INFO|C|H|M|L|I)-\d+\]", re.IGNORECASE)


def parse_findings(content: str) -> list[dict]:
    findings: list[dict] = []
    current: dict | None = None
    for line in content.splitlines():
        match = HEADING.match(line.strip())
        if match:
            if current:
                findings.append(current)
            identifier = match.group(1).upper()
            current = {"id": identifier, "title": match.group(2).strip() or identifier, "body": []}
        elif current is not None:
            current["body"].append(line)
    if current:
        findings.append(current)
    return findings


def severity(identifier: str, body: str) -> str:
    explicit = re.search(r"\bseverity\s*[:|]\s*(critical|high|medium|low|informational|info)\b", body, re.IGNORECASE)
    if explicit:
        return {"critical": "critical", "high": "high", "medium": "medium", "low": "low", "informational": "informational", "info": "informational"}[explicit.group(1).lower()]
    match = SEVERITY.search(f"[{identifier}]\n{body}")
    if not match:
        return "unclassified"
    value = match.group(1).lower()
    return {"c": "critical", "critical": "critical", "h": "high", "high": "high", "m": "medium", "medium": "medium", "l": "low", "low": "low", "i": "informational", "info": "informational"}.get(value, "unclassified")


def page(title: str, cards: str, counts: dict[str, int], note: str) -> str:
    return f"""<!doctype html>
<html lang=\"en\"><head><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">
<title>{html.escape(title)}</title>
<style>
:root{{color-scheme:dark;--bg:#0d1117;--panel:#161b22;--line:#30363d;--text:#c9d1d9;--muted:#8b949e;--critical:#f85149;--high:#ff7b72;--medium:#d29922;--low:#58a6ff}}body{{font:15px/1.55 system-ui,sans-serif;background:var(--bg);color:var(--text);margin:0;padding:2rem}}main{{max-width:1100px;margin:auto}}header{{border-bottom:1px solid var(--line);margin-bottom:1.5rem}}h1{{color:#79c0ff}}.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:.75rem}}.card,details{{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:1rem;margin:.75rem 0}}.metric{{font-size:2rem;font-weight:700}}.muted{{color:var(--muted)}}summary{{cursor:pointer;font-weight:700}}pre{{white-space:pre-wrap;overflow:auto;background:#090d13;border:1px solid var(--line);padding:1rem;border-radius:6px}}.critical{{color:var(--critical)}}.high{{color:var(--high)}}.medium{{color:var(--medium)}}.low,.informational{{color:var(--low)}}input{{width:100%;box-sizing:border-box;background:var(--panel);border:1px solid var(--line);color:var(--text);padding:.7rem;border-radius:6px}}
</style></head><body><main><header><h1>AuditSharingan security report</h1><p class=\"muted\">Evidence dashboard generated from the supplied report. Machine leads remain unvalidated until the report says otherwise.</p></header>
<section class=\"grid\">{''.join(f'<div class=\"card\"><span class=\"{key}\">{key.title()}</span><div class=\"metric\">{counts.get(key, 0)}</div></div>' for key in ('critical','high','medium','low','informational','unclassified'))}</section>
<p class=\"muted\">{html.escape(note)}</p><input id=\"filter\" placeholder=\"Filter findings\" aria-label=\"Filter findings\"><section id=\"findings\">{cards}</section>
</main><script>const q=document.querySelector('#filter');q.addEventListener('input',()=>{{const term=q.value.toLowerCase();document.querySelectorAll('details').forEach(x=>x.hidden=!x.innerText.toLowerCase().includes(term));}});</script></body></html>"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate an evidence-aware HTML AuditSharingan report.")
    parser.add_argument("report_file")
    parser.add_argument("--output-file", default="AuditSharingan-audit/report.html")
    args = parser.parse_args()
    report = Path(args.report_file).expanduser().resolve()
    output = Path(args.output_file).expanduser().resolve()
    content = report.read_text(encoding="utf-8", errors="replace") if report.exists() else ""
    findings = parse_findings(content)
    counts = {key: 0 for key in ("critical", "high", "medium", "low", "informational", "unclassified")}
    cards = []
    for finding in findings:
        level = severity(finding["id"], "\n".join(finding["body"]))
        counts[level] += 1
        body = "\n".join(finding["body"]).strip() or "No finding body supplied."
        cards.append(f'<details data-severity="{level}"><summary class="{level}">[{html.escape(finding["id"])}] {html.escape(finding["title"])}</summary><pre>{html.escape(body)}</pre></details>')
    if not findings:
        cards.append('<div class="card"><strong>No parseable findings.</strong><p class="muted">The source report is missing or uses a heading format this renderer does not understand. This dashboard does not infer that the target is safe.</p></div>')
    note = f"Parsed {len(findings)} finding heading(s)." if findings else "Parsed 0 finding headings; review the source report and renderer format before making a security claim."
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page("AuditSharingan security report", "".join(cards), counts, note), encoding="utf-8")
    print(f"HTML report generated at {output}; parsed {len(findings)} finding heading(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
