from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "evals"))

import auditsharingan  # noqa: E402
import generate_html_report  # noqa: E402
import score  # noqa: E402


class AuditSharinganUnitTests(unittest.TestCase):
    def test_scope_excludes_tests_and_artifacts(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "src").mkdir()
            (root / "test").mkdir()
            (root / "src" / "Vault.sol").write_text("pragma solidity ^0.8.20;\ncontract Vault {}\n", encoding="utf-8")
            (root / "test" / "Vault.t.sol").write_text("contract Test {}\n", encoding="utf-8")
            output = root / "AuditSharingan-audit"
            files = auditsharingan.collect_sources(root, output)
            self.assertEqual([path.relative_to(root).as_posix() for path in files], ["src/Vault.sol"])

    def test_manifest_shape_is_machine_readable(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output = root / "artifacts"
            (output / "logs").mkdir(parents=True)
            for name in ("one.stdout.log", "one.stderr.log"):
                (output / "logs" / name).write_text("", encoding="utf-8")
            (output / "scope.json").write_text("{}\n", encoding="utf-8")
            (output / "leads.md").write_text("# Leads\n", encoding="utf-8")
            manifest = {
                "schema_version": "1.0", "engine": "AuditSharingan", "engine_version": "1.0.0",
                "generated_at": "now", "target": str(root), "output_dir": str(output),
                "mode": "quick", "platforms": [], "scope": {"files": [], "counts_by_extension": {}, "sloc": 0},
                "steps": [{"name": "one", "command": ["true"], "status": "ok", "returncode": 0, "duration_seconds": 0.0, "stdout_file": str(output / "logs" / "one.stdout.log"), "stderr_file": str(output / "logs" / "one.stderr.log")}],
                "overall_status": "completed", "dispatch_plan": str(output / "dispatch-plan.md"), "guarantees": {"leads_are_not_findings": True},
            }
            (output / "run-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            from validate_artifacts import validate
            self.assertEqual(validate(output), [])

    def test_html_never_infers_clean_from_empty_input(self):
        self.assertEqual(generate_html_report.parse_findings("# report\n"), [])
        html = generate_html_report.page("AuditSharingan", "", {"critical": 0, "high": 0, "medium": 0, "low": 0, "informational": 0, "unclassified": 0}, "No parseable findings")
        self.assertIn("No parseable findings", html)
        self.assertNotIn("Zero unresolved", html)

    def test_score_distinguishes_wrong_class(self):
        truth = [{"fixture": "V01", "bug_class": "reentrancy"}, {"fixture": "C01", "bug_class": "benign"}]
        predictions = [{"fixture": "V01", "verdict": "VALID", "root_cause": "oracle"}, {"fixture": "C01", "verdict": "NO FINDING", "root_cause": ""}]
        result = score.score(truth, predictions)
        self.assertEqual(result["counts"]["FN"], 1)
        self.assertEqual(result["counts"]["FP"], 1)


if __name__ == "__main__":
    unittest.main()
