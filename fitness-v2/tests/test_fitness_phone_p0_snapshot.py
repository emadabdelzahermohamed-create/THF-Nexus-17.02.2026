import os
import stat
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "fitness_phone_p0_snapshot.sh"

FAKE_ADB = r'''#!/usr/bin/env python3
import os
import sys

args = sys.argv[1:]
with open(os.environ["ADB_CALL_LOG"], "a", encoding="utf-8") as handle:
    handle.write(" ".join(args) + "\n")

scenario = os.environ.get("ADB_SCENARIO", "ready")
if args == ["devices", "-l"]:
    print("List of devices attached")
    print("SERIAL_A device product:a model:SM_A217F")
    if scenario == "multiple":
        print("SERIAL_B device product:b model:Pixel")
    raise SystemExit(0)

command = " ".join(args[3:]) if args[:2] == ["-s", "SERIAL_A"] and args[2:3] == ["shell"] else ""
if args[:3] == ["-s", "SERIAL_A", "get-state"]:
    print("device")
elif args[:4] == ["-s", "SERIAL_A", "exec-out", "screencap"]:
    sys.stdout.buffer.write(b"PNG-EVIDENCE")
elif args[:4] == ["-s", "SERIAL_A", "logcat", "-d"]:
    print("10-26 18:00:00.000 I THF: checkpoint")
elif command == "dumpsys package com.topherofit.thf.pulse":
    print("versionCode=51012 minSdk=26 targetSdk=36")
    print("versionName=5.0.0-v2-alpha12")
elif command == "pm list packages -i com.topherofit.thf.pulse":
    print("package:com.topherofit.thf.pulse installer=com.android.vending")
elif command == "pm path com.topherofit.thf.pulse":
    print("package:/data/app/com.topherofit.thf.pulse/base.apk")
elif command.startswith("getprop "):
    print("SM-A217F")
else:
    print("read-only evidence for " + command)
'''


class FitnessPhoneP0SnapshotTests(unittest.TestCase):
    def run_snapshot(self, scenario="ready", *extra_args):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake_adb = root / "adb"
            fake_adb.write_text(textwrap.dedent(FAKE_ADB), encoding="utf-8")
            fake_adb.chmod(fake_adb.stat().st_mode | stat.S_IXUSR)
            call_log = root / "calls.log"
            output = root / "evidence"
            env = os.environ.copy()
            env.update(ADB_BIN=str(fake_adb), ADB_CALL_LOG=str(call_log), ADB_SCENARIO=scenario)
            result = subprocess.run(
                ["bash", str(SCRIPT), "--label", "stationary-start", "--out", str(output), *extra_args],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            calls = call_log.read_text(encoding="utf-8").splitlines() if call_log.exists() else []
            files = {path.name: path.read_bytes() for path in output.iterdir()} if output.exists() else {}
            return result, calls, files

    def test_snapshot_captures_identity_runtime_gps_notification_and_checksums(self):
        result, calls, files = self.run_snapshot()

        self.assertEqual(0, result.returncode, result.stderr)
        for name in (
            "checkpoint.txt", "package.txt", "installer.txt", "service.txt", "activity.txt",
            "location.txt", "notification.txt", "power.txt", "window.txt", "sensorservice.txt",
            "runtime_permissions.txt", "appops.txt", "logcat.txt", "screen.png", "SHA256SUMS",
        ):
            self.assertIn(name, files)
            self.assertTrue(files[name], name)
        self.assertIn(b"versionCode=51012", files["package.txt"])
        self.assertIn(b"installer=com.android.vending", files["installer.txt"])
        self.assertEqual(b"PNG-EVIDENCE", files["screen.png"])
        self.assertIn("snapshot_state=CAPTURED", result.stdout)
        self.assertEqual(1, calls.count("devices -l"))

        normalized = "\n" + "\n".join(f" {call.lower()} " for call in calls) + "\n"
        for forbidden in (
            " connect ", " pair ", " install ", " uninstall ", " force-stop", " monkey",
            " input ", " am start", " pm clear", " settings put", " svc ",
        ):
            self.assertNotIn(forbidden, normalized)

    def test_multiple_devices_fail_before_any_shell_or_capture(self):
        result, calls, files = self.run_snapshot("multiple")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("snapshot_state=MULTIPLE_DEVICES", result.stdout)
        self.assertEqual(["devices -l"], calls)
        self.assertEqual({}, files)

    def test_unknown_checkpoint_label_fails_before_adb(self):
        result, calls, files = self.run_snapshot("ready", "--label", "invented")

        self.assertNotEqual(0, result.returncode)
        self.assertIn("unknown --label", result.stderr)
        self.assertEqual([], calls)
        self.assertEqual({}, files)


if __name__ == "__main__":
    unittest.main()
