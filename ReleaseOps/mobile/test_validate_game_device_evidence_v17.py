#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, sys, tempfile, unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
S = importlib.util.spec_from_file_location("v17", HERE / "validate_game_device_evidence_v17.py")
M = importlib.util.module_from_spec(S); sys.modules[S.name] = M; S.loader.exec_module(M)
T = importlib.util.spec_from_file_location("t16", HERE / "test_validate_game_device_evidence_v16.py")
T16 = importlib.util.module_from_spec(T); sys.modules[T.name] = T16; T.loader.exec_module(T16)
V3 = M.V3

BOOT_A = "11111111-2222-4333-8444-555555555555"
BOOT_B = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"


def evidence(product, rsha, root, boot_id=BOOT_A):
    d = T16.evidence(product, rsha, root)
    req = dict(T16.T15.T14.M.BASE)
    req.update(T16.T15.T14.M.PRODUCT.get(product, {}))
    for key in req:
        row = d["process_provenance"][key]
        p = root / row["evidence_ref"]
        p.write_text(p.read_text(encoding="utf-8") + "\n".join([
            "THF_ANDROID_BOOT_ID=" + boot_id,
            "THF_BOOT_ID_CAPTURE_METHOD=ADB_CAT_PROC_BOOT_ID",
            "THF_BOOT_ID_CAPTURE_COMMAND=cat /proc/sys/kernel/random/boot_id",
            "THF_BOOT_ID_CAPTURE_EXIT_CODE=0",
            "",
        ]), encoding="utf-8")
        row["evidence_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()
    return d


def mutate(d, root, key, old, new):
    row = d["process_provenance"][key]
    p = root / row["evidence_ref"]
    p.write_text(p.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")
    row["evidence_sha256"] = hashlib.sha256(p.read_bytes()).hexdigest()


class V17(unittest.TestCase):
    def setUp(self):
        self.reg = T16.T15.T14.T13.T12.T11.T10.T9.T8.T7.T6.registry_doc()
        self.rsha = "f" * 64

    def test_all_six_pass_one_boot(self):
        for product in V3.PRODUCT_MANUAL:
            with self.subTest(product=product), tempfile.TemporaryDirectory() as td:
                root = Path(td)
                self.assertEqual([], M.validate_bundle(self.reg, self.rsha, evidence(product, self.rsha, root), root))

    def test_cross_reboot_capability_mix_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence("terra", self.rsha, root)
            mutate(d, root, "camera", "THF_ANDROID_BOOT_ID=" + BOOT_A, "THF_ANDROID_BOOT_ID=" + BOOT_B)
            errors = M.validate_bundle(self.reg, self.rsha, d, root)
            self.assertTrue(any("multiple Android boot sessions" in x for x in errors))

    def test_invalid_boot_uuid_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence("rift", self.rsha, root)
            mutate(d, root, "combat", "THF_ANDROID_BOOT_ID=" + BOOT_A, "THF_ANDROID_BOOT_ID=not-a-uuid")
            self.assertTrue(any("canonical Android boot UUID required" in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_wrong_boot_capture_method_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence("spark", self.rsha, root)
            mutate(d, root, "learning_progression", "THF_BOOT_ID_CAPTURE_METHOD=ADB_CAT_PROC_BOOT_ID", "THF_BOOT_ID_CAPTURE_METHOD=MANUAL")
            self.assertTrue(any("THF_BOOT_ID_CAPTURE_METHOD mismatch" in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_wrong_boot_capture_command_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence("rush", self.rsha, root)
            mutate(d, root, "sensor_motion", "THF_BOOT_ID_CAPTURE_COMMAND=cat /proc/sys/kernel/random/boot_id", "THF_BOOT_ID_CAPTURE_COMMAND=getprop ro.boot.serialno")
            self.assertTrue(any("THF_BOOT_ID_CAPTURE_COMMAND mismatch" in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_failed_boot_capture_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence("fitness_games", self.rsha, root)
            mutate(d, root, "repetition_counting", "THF_BOOT_ID_CAPTURE_EXIT_CODE=0", "THF_BOOT_ID_CAPTURE_EXIT_CODE=1")
            self.assertTrue(any("THF_BOOT_ID_CAPTURE_EXIT_CODE mismatch" in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))

    def test_v17_remains_non_promotional(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); d = evidence("learn_games", self.rsha, root); d["final_or_play_ready"] = True
            self.assertTrue(any("cannot self-promote" in x for x in M.validate_bundle(self.reg, self.rsha, d, root)))


if __name__ == "__main__":
    unittest.main()
