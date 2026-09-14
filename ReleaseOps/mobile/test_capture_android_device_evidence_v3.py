#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
# Make sibling validator importable when loading collector by file path.
sys.path.insert(0, str(HERE))
SPEC = importlib.util.spec_from_file_location("capture_device_v3", HERE / "capture_android_device_evidence_v3.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def cp(out: str = "", code: int = 0):
    return subprocess.CompletedProcess([], code, out, None)


class CaptureDeviceV3Tests(unittest.TestCase):
    def test_resume_requires_same_pid_and_does_not_force_stop(self):
        shell_calls = []

        def fake_shell(adb, serial, *args, timeout=30):
            shell_calls.append(args)
            if args[:2] == ("pidof", "com.test.game"):
                return cp("1234\n")
            return cp("")

        with patch.object(MOD, "shell", side_effect=fake_shell), \
             patch.object(MOD, "foreground_launch", return_value=(True, "1234")), \
             patch.object(MOD.time, "sleep", return_value=None):
            ok, pid = MOD.resume_without_restart("adb", "SERIAL", "com.test.game", "1234")
        self.assertTrue(ok)
        self.assertEqual("1234", pid)
        self.assertFalse(any(call[:2] == ("am", "force-stop") for call in shell_calls))
        self.assertTrue(any(call[:3] == ("input", "keyevent", "KEYCODE_HOME") for call in shell_calls))

    def test_resume_rejects_process_restart(self):
        with patch.object(MOD, "shell", return_value=cp("9999\n")), \
             patch.object(MOD, "foreground_launch") as launch, \
             patch.object(MOD.time, "sleep", return_value=None):
            ok, pid = MOD.resume_without_restart("adb", "SERIAL", "com.test.game", "1234")
        self.assertFalse(ok)
        self.assertEqual("9999", pid)
        launch.assert_not_called()

    def test_emulator_qemu_is_detected(self):
        values = {
            "ro.kernel.qemu": "1",
            "ro.boot.qemu": "",
            "ro.hardware": "ranchu",
            "ro.product.model": "sdk_gphone64_arm64",
            "ro.product.manufacturer": "Google",
            "ro.build.fingerprint": "generic/sdk/generic",
        }
        with patch.object(MOD, "prop", side_effect=lambda adb, serial, key: values[key]):
            detected, props = MOD.detect_emulator("adb", "SERIAL")
        self.assertTrue(detected)
        self.assertEqual("1", props["ro.kernel.qemu"])

    def test_physical_phone_is_not_detected_as_emulator(self):
        values = {
            "ro.kernel.qemu": "0",
            "ro.boot.qemu": "0",
            "ro.hardware": "tensor",
            "ro.product.model": "Pixel 10",
            "ro.product.manufacturer": "Google",
            "ro.build.fingerprint": "google/example/release-keys",
        }
        with patch.object(MOD, "prop", side_effect=lambda adb, serial, key: values[key]):
            detected, _ = MOD.detect_emulator("adb", "SERIAL")
        self.assertFalse(detected)

    def test_manual_template_starts_fail_closed(self):
        for product in MOD.PRODUCT_MANUAL:
            template = MOD.manual_template(product)
            self.assertTrue(template)
            self.assertTrue(all(v["pass"] is False and not v["evidence_ref"] for v in template.values()))


if __name__ == "__main__":
    unittest.main()
