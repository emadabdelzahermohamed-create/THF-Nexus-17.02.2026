import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fitness_phone_preflight.sh"
FORBIDDEN = (
    " connect ",
    " pair ",
    " install ",
    " uninstall ",
    " force-stop",
    " monkey",
    " input ",
    " am start",
    " pm clear",
)


FAKE_ADB = r'''#!/usr/bin/env python3
import os
import sys

args = sys.argv[1:]
with open(os.environ["ADB_CALL_LOG"], "a", encoding="utf-8") as handle:
    handle.write(" ".join(args) + "\n")

scenario = os.environ["ADB_SCENARIO"]
if args == ["devices", "-l"]:
    print("List of devices attached")
    if scenario == "offline":
        pass
    elif scenario == "multiple":
        print("SERIAL_A device product:a model:SM_A217F")
        print("SERIAL_B device product:b model:Pixel")
    else:
        print("SERIAL_A device product:a model:SM_A217F")
    raise SystemExit(0)

command = " ".join(args[3:]) if args[:2] == ["-s", "SERIAL_A"] and args[2:3] == ["shell"] else ""
if command == "dumpsys power":
    print("mWakefulness=Awake")
    if scenario != "noninteractive":
        print("mInteractive=true")
elif command == "dumpsys window":
    print("mShowingLockscreen=true" if scenario == "locked" else "mShowingLockscreen=false")
    print("mDreamingLockscreen=false")
    print("isStatusBarKeyguard=false")
elif command == "pm path com.topherofit.thf.pulse":
    if scenario != "package_missing":
        print("package:/data/app/com.topherofit.thf.pulse/base.apk")
elif command == "dumpsys package com.topherofit.thf.pulse":
    print("versionCode=51010 minSdk=26 targetSdk=36")
    print("versionName=5.0.0-v2-alpha10")
elif command == "pm list packages -i com.topherofit.thf.pulse":
    print("package:com.topherofit.thf.pulse  installer=com.android.vending")
elif command == "dumpsys activity services com.topherofit.thf.pulse/.ActivityTrackingService":
    if scenario == "active":
        print("ServiceRecord{abc com.topherofit.thf.pulse/.ActivityTrackingService}")
        print("isForeground=true")
        print("startRequested=true")
else:
    print("unexpected fake adb call: " + " ".join(args), file=sys.stderr)
    raise SystemExit(91)
'''


class FitnessPhonePreflightTests(unittest.TestCase):
    def run_preflight(self, scenario, *extra_args):
        with tempfile.TemporaryDirectory() as tmp:
            fake_adb = Path(tmp) / "adb"
            fake_adb.write_text(textwrap.dedent(FAKE_ADB), encoding="utf-8")
            fake_adb.chmod(fake_adb.stat().st_mode | stat.S_IXUSR)
            call_log = Path(tmp) / "calls.log"
            env = os.environ.copy()
            env.update(
                ADB_BIN=str(fake_adb),
                ADB_CALL_LOG=str(call_log),
                ADB_SCENARIO=scenario,
            )
            result = subprocess.run(
                ["bash", str(SCRIPT), *extra_args],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            calls = call_log.read_text(encoding="utf-8").splitlines() if call_log.exists() else []
            return result, calls

    def assert_read_only(self, calls):
        normalized = "\n" + "\n".join(f" {call} " for call in calls).lower() + "\n"
        for forbidden in FORBIDDEN:
            self.assertNotIn(forbidden, normalized)
        self.assertEqual(calls.count("devices -l"), 1)

    def test_no_device_fails_closed_after_one_inventory_call(self):
        result, calls = self.run_preflight("offline")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=ADB_OFFLINE", result.stdout)
        self.assertEqual(calls, ["devices -l"])
        self.assert_read_only(calls)

    def test_multiple_devices_fail_closed_before_shell_queries(self):
        result, calls = self.run_preflight("multiple")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=MULTIPLE_DEVICES", result.stdout)
        self.assertEqual(calls, ["devices -l"])
        self.assert_read_only(calls)

    def test_locked_device_fails_before_package_or_service_queries(self):
        result, calls = self.run_preflight("locked")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=DEVICE_LOCKED", result.stdout)
        self.assertFalse(any("pm path" in call for call in calls))
        self.assertFalse(any("activity services" in call for call in calls))
        self.assert_read_only(calls)

    def test_awake_but_noninteractive_device_fails_closed(self):
        result, calls = self.run_preflight("noninteractive")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=DEVICE_NOT_INTERACTIVE", result.stdout)
        self.assertFalse(any("dumpsys window" in call for call in calls))
        self.assert_read_only(calls)

    def test_unavailable_requested_serial_fails_before_shell_queries(self):
        result, calls = self.run_preflight("ready", "--serial", "OTHER_SERIAL")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=REQUESTED_DEVICE_UNAVAILABLE", result.stdout)
        self.assertEqual(calls, ["devices -l"])
        self.assert_read_only(calls)

    def test_missing_package_fails_before_service_query(self):
        result, calls = self.run_preflight("package_missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=PACKAGE_NOT_INSTALLED", result.stdout)
        self.assertFalse(any("activity services" in call for call in calls))
        self.assert_read_only(calls)

    def test_active_tracking_session_blocks_qa_and_reports_installed_identity(self):
        result, calls = self.run_preflight("active")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("qa_state=ACTIVE_TRACKING_SESSION", result.stdout)
        self.assertIn("installed_version_code=51010", result.stdout)
        self.assertIn("installed_version_name=5.0.0-v2-alpha10", result.stdout)
        self.assertIn("installer=com.android.vending", result.stdout)
        self.assert_read_only(calls)

    def test_idle_unlocked_device_is_ready_for_separate_manual_qa(self):
        result, calls = self.run_preflight("ready", "--serial", "SERIAL_A")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("qa_state=READY_FOR_MANUAL_QA", result.stdout)
        self.assertIn("device_serial=SERIAL_A", result.stdout)
        self.assert_read_only(calls)


if __name__ == "__main__":
    unittest.main()
