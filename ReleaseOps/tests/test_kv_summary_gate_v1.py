#!/usr/bin/env python3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "kv_summary_gate_v1.py"


class SummaryGateTests(unittest.TestCase):
    def run_gate(self, text: str, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "summary.txt"
            p.write_text(text, encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPT), str(p), *args], text=True, capture_output=True)

    def test_duplicate_truth_is_not_false_negative(self):
        r = self.run_gate(
            "status=PASS\nstatus=PASS\nstatus=PASS\nstatus=PASS\n"
            "target_sdk=36\ntarget_sdk=36\ntarget_sdk=36\ntarget_sdk=36\n"
            "canonical_archive_unchanged=true\ncanonical_archive_unchanged=true\n",
            "--require", "status=PASS:2",
            "--require", "target_sdk=36:2",
            "--require", "canonical_archive_unchanged=true:2",
        )
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertIn("KV_SUMMARY_GATE=PASS", r.stdout)

    def test_missing_required_truth_fails_closed(self):
        r = self.run_gate("status=PASS\n", "--require", "status=PASS:2")
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("KV_SUMMARY_GATE=FAIL", r.stdout)

    def test_forbidden_marker_fails(self):
        r = self.run_gate("status=PASS\nproduction_signing=true\n", "--require", "status=PASS:1", "--forbid", "production_signing=true")
        self.assertNotEqual(r.returncode, 0)


if __name__ == "__main__":
    unittest.main()
