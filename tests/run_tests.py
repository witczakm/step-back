#!/usr/bin/env python3
"""Backtest: every case -> expected status, in English and Polish.
Run from the repository root: python3 tests/run_tests.py"""
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCRIPTS = [HERE.parent / "plugins" / "step-back" / "skills" / "step-back" / "scripts" / "signals.py",
           HERE.parent / "plugins" / "krok-wstecz" / "skills" / "krok-wstecz" / "scripts" / "signals.py"]
expected = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))
failures = 0
for script in SCRIPTS:
    if not script.exists():
        print(f"MISSING {script}"); failures += 1; continue
    for lang, cases in expected.items():
        for name, status in cases.items():
            out = subprocess.run([sys.executable, str(script), str(HERE / "cases" / lang / name),
                                  "--json", "--lang", lang], capture_output=True, text=True)
            got = json.loads(out.stdout)[0]["status"] if out.returncode == 0 else f"rc{out.returncode}"
            ok = got == status
            failures += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {script.parts[-3]:<12} {lang}  {name:<36} expected {status:<9} got {got}")
    rc = subprocess.run([sys.executable, str(script), "/does/not/exist.md"], capture_output=True).returncode
    print(f"{'PASS' if rc == 0 else 'FAIL'}  {script.parts[-3]:<12} missing log -> exit code 0 (got {rc})")
    failures += rc != 0
print(f"\nFAILURES: {failures}")
sys.exit(1 if failures else 0)
