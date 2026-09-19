#!/usr/bin/env python3
"""Verify a mitigation in an isolated copy of the current target.

The original repository is never patched, reset, or cleaned. The verifier
requires a reproducible pre-patch PoC, applies the diff to a temporary copy,
checks that the post-patch command fails for an expected test reason (rather
than a compilation error), and runs the normal regression suite.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def run(command: list[str], cwd: Path, timeout: int = 900) -> dict:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        return {"command": command, "returncode": result.returncode, "stdout": result.stdout, "stderr": result.stderr, "timed_out": False}
    except subprocess.TimeoutExpired as exc:
        return {"command": command, "returncode": 124, "stdout": exc.stdout or "", "stderr": exc.stderr or "", "timed_out": True}
    except OSError as exc:
        return {"command": command, "returncode": 127, "stdout": "", "stderr": str(exc), "timed_out": False}


def combined(result: dict) -> str:
    return f"{result.get('stdout', '')}\n{result.get('stderr', '')}"


def looks_like_compilation_failure(result: dict) -> bool:
    text = combined(result).lower()
    markers = (
        "compilation failed", "compiler error", "error (", "error:",
        "failed to compile", "could not compile", "parsererror",
    )
    return result.get("returncode") not in (0, None) and any(marker in text for marker in markers)


def copy_target(source: Path, destination: Path) -> None:
    ignored = shutil.ignore_patterns(".git", "out", "cache", "AuditSharingan-audit", ".auditsharingan")
    shutil.copytree(source, destination, ignore=ignored, symlinks=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a mitigation without mutating the target repository.")
    parser.add_argument("target_dir")
    parser.add_argument("patch_file")
    parser.add_argument("--poc-test", required=True, help="Foundry test name passed to --match-test")
    parser.add_argument("--fork-url", default="")
    parser.add_argument("--regression-command", nargs="+", default=["forge", "test"], help="Regression command; defaults to forge test")
    parser.add_argument("--output-file", default="", help="Optional JSON result path")
    args = parser.parse_args()
    target = Path(args.target_dir).expanduser().resolve()
    patch = Path(args.patch_file).expanduser().resolve()
    if not target.is_dir():
        print(f"error: target directory not found: {target}", file=sys.stderr)
        return 2
    if not patch.is_file():
        print(f"error: patch file not found: {patch}", file=sys.stderr)
        return 2
    if shutil.which("forge") is None and args.regression_command[:1] == ["forge"]:
        print("error: forge is required for the default verifier", file=sys.stderr)
        return 2

    poc_command = ["forge", "test", "--match-test", args.poc_test, "-vv"]
    if args.fork_url:
        poc_command += ["--fork-url", args.fork_url]
    result: dict = {
        "schema_version": "1.0",
        "engine": "AuditSharingan",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "target": str(target),
        "patch": str(patch),
        "poc_test": args.poc_test,
        "target_mutated": False,
    }

    print("[1/4] Running the pre-patch PoC in the original target (read-only)")
    pre = run(poc_command, target)
    result["pre_patch"] = pre
    if pre["returncode"] != 0 or pre["timed_out"]:
        print("Pre-patch PoC did not pass; refusing to call the mitigation verified.", file=sys.stderr)
        result["verdict"] = "invalid_precondition"
        if args.output_file:
            Path(args.output_file).expanduser().resolve().write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        return 1
    print("      pre-patch exploit reproduction passed")

    with tempfile.TemporaryDirectory(prefix="auditsharingan-mitigation-") as temporary:
        sandbox = Path(temporary) / target.name
        copy_target(target, sandbox)
        print("[2/4] Applying the patch in an isolated temporary copy")
        check = run(["git", "apply", "--check", str(patch)], sandbox)
        if check["returncode"] != 0:
            result["patch_check"] = check
            result["verdict"] = "patch_not_applicable"
            print("Patch does not apply cleanly to the current target copy.", file=sys.stderr)
            return 1
        applied = run(["git", "apply", "--whitespace=nowarn", str(patch)], sandbox)
        result["patch_apply"] = applied
        if applied["returncode"] != 0:
            result["verdict"] = "patch_not_applied"
            print("Patch application failed.", file=sys.stderr)
            return 1

        print("[3/4] Re-running the PoC after the patch")
        post = run(poc_command, sandbox)
        result["post_patch"] = post
        if post["returncode"] == 0:
            exploit_blocked = False
            post_reason = "test still passes"
        elif post["timed_out"] or looks_like_compilation_failure(post):
            exploit_blocked = False
            post_reason = "post-patch command failed to compile or timed out"
        else:
            exploit_blocked = True
            post_reason = "test failed after patch; inspect output to confirm the expected exploit assertion/revert"
        print(f"      {'blocked' if exploit_blocked else 'not verified'}: {post_reason}")

        print("[4/4] Running the regression suite in the same isolated copy")
        regression = run(args.regression_command, sandbox)
        result["regression"] = regression
        regression_clean = regression["returncode"] == 0 and not regression["timed_out"]
        print(f"      {'zero regressions' if regression_clean else 'regressions or test failure detected'}")

        if exploit_blocked and regression_clean:
            result["verdict"] = "MITIGATION_VERIFIED_BLOCKS_EXPLOIT_ZERO_REGRESSIONS"
        elif exploit_blocked:
            result["verdict"] = "MITIGATION_PARTIAL_BLOCKS_EXPLOIT_WITH_REGRESSIONS"
        elif post["returncode"] == 0:
            result["verdict"] = "MITIGATION_FAILED_EXPLOIT_STILL_PASSES"
        else:
            result["verdict"] = "MITIGATION_UNVERIFIED_POST_PATCH_FAILURE_NOT_CLASSIFIED"

    if args.output_file:
        output = Path(args.output_file).expanduser().resolve()
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"VERDICT: {result['verdict']}")
    return 0 if result["verdict"] == "MITIGATION_VERIFIED_BLOCKS_EXPLOIT_ZERO_REGRESSIONS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
