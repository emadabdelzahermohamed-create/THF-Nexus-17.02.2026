#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json, sys, tempfile, unittest
from pathlib import Path
from types import SimpleNamespace

HERE = Path(__file__).resolve().parent
S = importlib.util.spec_from_file_location("capturev17", HERE / "capture_game_process_provenance_v17.py")
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)

BOOT = "11111111-2222-4333-8444-555555555555"


def cp(code=0, out=""):
    return SimpleNamespace(returncode=code, stdout=out)


class CaptureV17(unittest.TestCase):
    def make_inputs(self, root: Path):
        evidence = {"device": {"fingerprint_sha256": "f" * 64}, "final_or_play_ready": False}
        p = root / "evidence.json"
        p.write_text(json.dumps(evidence), encoding="utf-8")
        return p

    def install_fakes(self, boot=BOOT, boot_code=0, fp="f" * 64):
        old = (M.V16.capture, M.V16.one_device, M.V16.device_fingerprint, M.V16.shell)
        def fake_capture(evidence_path, capability, evidence_root, out, adb):
            out.write_text("THF_SESSION_ID=S1\n", encoding="utf-8")
            return {"status": "CAPTURED_V16_PROCESS_PROVENANCE", "evidence_sha256": "0" * 64, "final_or_play_ready": False}
        M.V16.capture = fake_capture
        M.V16.one_device = lambda adb: "PHONE123"
        M.V16.device_fingerprint = lambda adb, serial: (fp, {})
        M.V16.shell = lambda adb, serial, *args: cp(boot_code, boot + "\n" if boot_code == 0 else "failed")
        return old

    def restore(self, old):
        M.V16.capture, M.V16.one_device, M.V16.device_fingerprint, M.V16.shell = old

    def test_capture_appends_boot_binding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); e = self.make_inputs(root); out = root / "proc.txt"; old = self.install_fakes()
            try:
                result = M.capture(e, "camera", root, out, "adb")
            finally:
                self.restore(old)
            text = out.read_text()
            self.assertEqual("CAPTURED_V17_BOOT_BOUND_PROCESS_PROVENANCE", result["status"])
            self.assertEqual(BOOT, result["android_boot_id"])
            self.assertIn("THF_ANDROID_BOOT_ID=" + BOOT, text)
            self.assertIn("THF_BOOT_ID_CAPTURE_METHOD=ADB_CAT_PROC_BOOT_ID", text)
            self.assertIn("THF_BOOT_ID_CAPTURE_COMMAND=cat /proc/sys/kernel/random/boot_id", text)
            self.assertIn("THF_BOOT_ID_CAPTURE_EXIT_CODE=0", text)
            self.assertFalse(result["final_or_play_ready"])

    def test_invalid_boot_uuid_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); e = self.make_inputs(root); old = self.install_fakes(boot="not-a-uuid")
            try:
                with self.assertRaisesRegex(RuntimeError, "invalid Android boot UUID"):
                    M.capture(e, "camera", root, root / "out.txt", "adb")
            finally:
                self.restore(old)

    def test_boot_capture_exit_failure_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); e = self.make_inputs(root); old = self.install_fakes(boot_code=1)
            try:
                with self.assertRaisesRegex(RuntimeError, "boot-id capture failed"):
                    M.capture(e, "camera", root, root / "out.txt", "adb")
            finally:
                self.restore(old)

    def test_device_change_before_boot_capture_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); e = self.make_inputs(root); old = self.install_fakes(fp="0" * 64)
            try:
                with self.assertRaisesRegex(RuntimeError, "device changed"):
                    M.capture(e, "camera", root, root / "out.txt", "adb")
            finally:
                self.restore(old)


if __name__ == "__main__":
    unittest.main()
