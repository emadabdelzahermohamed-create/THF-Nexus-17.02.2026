"""Host-only regression tests for the fail-closed physical QA preflight.

All ADB calls are routed to a temporary fake executable. These tests never
contact or modify a physical device.
"""
import hashlib
import os
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "fitness_phone_p0_preflight.sh"
)


FAKE_ADB = r'''#!/usr/bin/env bash
set -u
printf '%s\n' "$*" >> "$FAKE_ADB_LOG"

mode="${FAKE_ADB_MODE:-ready}"
if [[ "${1:-}" == "devices" ]]; then
  printf 'List of devices attached\n'
  if [[ "$mode" != "offline" ]]; then
    printf 'SERIAL device product:mock model:MockPhone\n'
  fi
  exit 0
fi

if [[ "${1:-}" == "-s" ]]; then
  shift 2
fi
if [[ "${1:-}" == "get-state" ]]; then
  printf 'device\n'
  exit 0
fi
if [[ "${1:-}" != "shell" ]]; then
  exit 0
fi
shift

case "${1:-}" in
  date)
    printf '2026-10-27T09:20:00Z\n'
    ;;
  pm)
    printf 'package:com.topherofit.thf.pulse installer=com.android.vending\n'
    ;;
  dumpsys)
    case "${2:-}" in
      package)
        printf 'Package [com.topherofit.thf.pulse] versionCode=%s versionName=5.0.0-v2-alpha18 targetSdk=36\n' "${FAKE_VERSION_CODE:-51018}"
        ;;
      activity)
        case "${3:-}" in
          services)
            if [[ "$mode" == "active_service" ]]; then
              printf 'ServiceRecord{com.topherofit.thf.pulse/.ActivityTrackingService isForeground=true startRequested=true}\n'
            else
              printf 'No matching services\n'
            fi
            ;;
          activities)
            printf 'mResumedActivity: ActivityRecord{com.android.settings/.Settings}\n'
            ;;
          *)
            printf 'No matching activity data\n'
            ;;
        esac
        ;;
      notification)
        if [[ "$mode" == "active_notification" ]]; then
          printf 'NotificationRecord{com.topherofit.thf.pulse ongoing=true}\n'
        else
          printf 'No active notifications\n'
        fi
        ;;
      power)
        printf 'mWakefulness=Awake mInteractive=true\n'
        ;;
      window)
        if [[ "$mode" == "locked" ]]; then
          printf 'mShowingLockscreen=true\n'
        else
          printf 'mShowingLockscreen=false\n'
        fi
        ;;
      keyguard)
        if [[ "$mode" == "locked" ]]; then
          printf 'isKeyguardLocked=true\n'
        else
          printf 'isKeyguardLocked=false\n'
        fi
        ;;
      *)
        printf 'No matching dump\n'
        ;;
    esac
    ;;
  *)
    printf 'Unexpected fake ADB command\n' >&2
    exit 2
    ;;
esac
'''


class FitnessPhonePreflightTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.adb = self.root / "fake-adb"
        self.log = self.root / "adb-calls.log"
        self.adb.write_text(FAKE_ADB, encoding="utf-8")
        self.adb.chmod(0o755)

    def tearDown(self):
        self.tmp.cleanup()

    def run_preflight(self, mode="ready", version="51018", owner_idle=True,
                      output=None):
        output = output or (self.root / "evidence")
        env = os.environ.copy()
        env.update({
            "ADB_BIN": str(self.adb),
            "FAKE_ADB_LOG": str(self.log),
            "FAKE_ADB_MODE": mode,
            "FAKE_VERSION_CODE": version,
        })
        args = [
            "bash", str(SCRIPT),
            "--expected-version-code", "51018",
            "--out", str(output),
        ]
        if owner_idle:
            args.append("--owner-confirmed-idle")
        result = subprocess.run(
            args, env=env, text=True, capture_output=True, check=False
        )
        calls = self.log.read_text(encoding="utf-8").splitlines() if self.log.exists() else []
        return result, output, calls

    def test_ready_requires_every_gate_and_writes_checksums(self):
        result, output, calls = self.run_preflight()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("preflight_state=PREFLIGHT_READY", report)
        for gate in (
            "installed_version", "google_play_installer", "keyguard_unlocked",
            "device_awake", "device_interactive", "tracking_service_absent",
            "workout_notification_absent", "app_not_resumed",
            "owner_idle_confirmation",
        ):
            self.assertIn(f"check_{gate}=PASS", report)
        self.assertTrue((output / "SHA256SUMS").is_file())
        self.assertGreater(len(calls), 0)

    def test_locked_device_fails_closed(self):
        result, output, _ = self.run_preflight(mode="locked")
        self.assertEqual(30, result.returncode)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("check_keyguard_unlocked=FAIL", report)
        self.assertIn("preflight_state=PREFLIGHT_BLOCKED", report)
        self.assertNotIn("PREFLIGHT_READY", report)

    def test_active_tracking_service_fails_closed(self):
        result, output, _ = self.run_preflight(mode="active_service")
        self.assertEqual(30, result.returncode)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("check_tracking_service_absent=FAIL", report)

    def test_ongoing_fitness_notification_fails_closed(self):
        result, output, _ = self.run_preflight(mode="active_notification")
        self.assertEqual(30, result.returncode)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("check_workout_notification_absent=FAIL", report)

    def test_wrong_installed_version_fails_closed(self):
        result, output, _ = self.run_preflight(version="51016")
        self.assertEqual(30, result.returncode)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("check_installed_version=FAIL", report)

    def test_missing_owner_idle_attestation_fails_closed(self):
        result, output, _ = self.run_preflight(owner_idle=False)
        self.assertEqual(30, result.returncode)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("check_owner_idle_confirmation=FAIL", report)

    def test_offline_device_fails_closed_and_records_device_list(self):
        result, output, _ = self.run_preflight(mode="offline")
        self.assertEqual(30, result.returncode)
        report = (output / "preflight.txt").read_text(encoding="utf-8")
        self.assertIn("preflight_state=ADB_OFFLINE", report)
        self.assertTrue((output / "devices.txt").is_file())
        manifest = output / "SHA256SUMS"
        self.assertTrue(manifest.is_file())
        for line in manifest.read_text(encoding="utf-8").splitlines():
            digest, relative_name = line.split(maxsplit=1)
            evidence = output / relative_name.strip()
            self.assertTrue(evidence.is_file())
            self.assertEqual(digest, hashlib.sha256(evidence.read_bytes()).hexdigest())

    def test_existing_output_directory_fails_before_adb(self):
        output = self.root / "already-exists"
        output.mkdir()
        result, _, calls = self.run_preflight(output=output)
        self.assertEqual(3, result.returncode)
        self.assertEqual([], calls)

    def test_preflight_never_invokes_mutating_adb_commands(self):
        result, _, calls = self.run_preflight()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        forbidden = re.compile(
            r"\b(am\s+start|input\s+(tap|swipe|keyevent)|force-stop|"
            r"install|uninstall|clear|wake|settings\s+put|"
            r"keyevent|pair|connect)\b",
            re.IGNORECASE,
        )
        for call in calls:
            self.assertIsNone(forbidden.search(call), f"mutating ADB command: {call}")


    def test_sha256_manifest_matches_final_evidence(self):
        result, output, _ = self.run_preflight()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        manifest = output / "SHA256SUMS"
        self.assertTrue(manifest.is_file())
        entries = [line.split(maxsplit=1) for line in manifest.read_text(encoding="utf-8").splitlines()]
        self.assertTrue(entries)
        for digest, relative_name in entries:
            name = relative_name.strip().lstrip("*")
            evidence = output / name
            self.assertTrue(evidence.is_file(), f"manifest entry missing: {name}")
            actual = hashlib.sha256(evidence.read_bytes()).hexdigest()
            self.assertEqual(digest, actual, f"checksum mismatch: {name}")


if __name__ == "__main__":
    unittest.main()
