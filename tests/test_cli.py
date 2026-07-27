#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
CLI integration test: verify command-line interface works correctly.
"""

import subprocess
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CLI = os.path.join(REPO_DIR, "cli.py")
PY = sys.executable

bugs = []
passes = []

def check(name, condition, detail=""):
    if condition:
        passes.append(name)
    else:
        bugs.append(f"BUG: {name} | {detail}")
        print(f"  ❌ {name}: {detail}")

def run_cli(*args):
    """Run cli.py with given args, return (returncode, stdout, stderr)."""
    cmd = [PY, CLI] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                            encoding='utf-8', errors='replace')
    return result.returncode, result.stdout, result.stderr

print("=" * 60)
print("  CLI INTEGRATION TEST")
print("=" * 60)

# Test 1: --help works
print("\n[Test 1] --help works")
rc, out, err = run_cli("--help")
check("help exits 0", rc == 0, f"rc={rc}, err={err[:100]}")
check("help shows description", "9-dimension scoring model" in out, "missing description")
check("help shows examples", "Anker" in out, "missing examples")

# Test 2: --backtest works
print("[Test 2] --backtest works")
rc, out, err = run_cli("--backtest")
check("backtest exits 0", rc == 0, f"rc={rc}, err={err[:200]}")
check("backtest shows N=10", "N=10" in out, "missing N=10")
check("backtest shows 100%", "100%" in out, "missing accuracy")
check("backtest shows Anker", "Anker" in out, "missing Anker")

# Test 3: minimal evaluation (text output)
print("[Test 3] Minimal evaluation (text)")
rc, out, err = run_cli("-n", "Test", "-c", "00001.HK", "-p", "10.0")
check("minimal eval exits 0", rc == 0, f"rc={rc}, err={err[:200]}")
check("minimal eval shows name", "Test" in out, "missing name")
check("minimal eval shows advice", "CAUTIOUS" in out or "SKIP" in out or "BUY" in out,
      "missing advice")
check("minimal eval shows weighted", "Weighted" in out, "missing weighted")

# Test 4: JSON output
print("[Test 4] JSON output")
rc, out, err = run_cli("-n", "Test", "-c", "00001.HK", "-p", "10.0", "--json")
check("json exits 0", rc == 0, f"rc={rc}, err={err[:200]}")
import json
try:
    parsed = json.loads(out)
    check("json is valid JSON", True)
    check("json has name", parsed.get("name") == "Test", f"name={parsed.get('name')}")
    check("json has advice", "advice" in parsed, "missing advice")
    check("json has scores", "scores" in parsed, "missing scores")
except json.JSONDecodeError as e:
    check("json is valid JSON", False, f"JSON parse error: {e}")

# Test 5: Full evaluation with all params
print("[Test 5] Full evaluation with all params")
rc, out, err = run_cli(
    "-n", "Anker", "-c", "00668.HK", "-p", "99.32",
    "--ref-cny", "100.4", "--rating", "AA+", "--scale", "56",
    "--retail", "27.57", "--inst", "10.24", "--cornerstone",
    "--sentiment", "positive", "--ipos-week", "8",
)
check("full eval exits 0", rc == 0, f"rc={rc}, err={err[:200]}")
check("full eval shows BUY", "BUY" in out, "expected BUY")
check("full eval shows discount", "disc" in out, "missing disc")
check("full eval shows A-share ref", "A-share" in out, "missing A-share ref")

# Test 6: Dark signal veto via CLI
print("[Test 6] Dark signal veto via CLI")
rc, out, err = run_cli(
    "-n", "Crash", "-c", "00002.HK", "-p", "10.0",
    "--rating", "AAA", "--scale", "5",
    "--retail", "30", "--inst", "20", "--cornerstone",
    "--market-env", "bull", "--sentiment", "positive",
    "--dark", "-10.0", "--ipos-week", "1",
)
check("veto exits 0", rc == 0, f"rc={rc}, err={err[:200]}")
check("veto shows SKIP", "SKIP" in out, "expected SKIP")
check("veto shows Veto line", "Veto" in out, "expected Veto line")

# Test 7: Cost warning via CLI
print("[Test 7] Cost warning via CLI")
rc, out, err = run_cli(
    "-n", "Marginal", "-c", "00003.HK", "-p", "10.0",
    "--ref-cny", "10.0", "--rating", "AA+", "--scale", "10",
    "--retail", "15", "--inst", "8", "--cornerstone",
    "--sentiment", "neutral", "--dark", "1.0", "--ipos-week", "2",
)
check("cost warning exits 0", rc == 0, f"rc={rc}, err={err[:200]}")
if "BUY" in out:
    check("cost warning shows Cost line", "Cost" in out, "expected Cost warning")
else:
    check("cost warning (advice not BUY, skip)", True)

# Test 8: Missing required args
print("[Test 8] Missing required args")
rc, out, err = run_cli("-n", "Incomplete")  # missing --code and --price
check("missing args exits non-zero", rc != 0, f"rc={rc}, should be non-zero")
check("missing args shows error", "required" in err.lower() or "error" in err.lower(),
      "missing error message")

# Summary
print(f"\n{'=' * 60}")
print(f"  CLI TEST SUMMARY")
print(f"{'=' * 60}")
print(f"  Tests passed: {len(passes)}")
print(f"  Bugs found:   {len(bugs)}")
if bugs:
    print(f"\n  BUGS:")
    for b in bugs:
        print(f"  {b}")
else:
    print(f"\n  ✅ No bugs found!")
print(f"{'=' * 60}")
