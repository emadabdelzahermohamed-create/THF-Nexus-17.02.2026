#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("device_evidence_v3", HERE / "validate_game_device_evidence_v3.py")
MOD = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MOD
SPEC.loader.exec_module(MOD)


def registry_doc() -> dict:
    rows = []
    for app, package, apk in (
        ("terra", "com.topherofit.thf.terra", "1" * 64),
        ("rift", "com.topherofit.thf.rift", "2" * 64),
        ("spark", "com.topherofit.thf.spark", "3" * 64),
        ("rush", "com.topherofit.thf.rush", "4" * 64),
        ("learn_games", "com.thf.topherofit.learngames", "5" * 64),
        ("fitness_games", "com.thf.topherofit.fitnessgames", "6" * 64),
    ):
        rows.append({"app": app, "package": package, "apk_sha256": apk})
    return {"schema": "thf-game-device-candidates-v1", "candidates": rows}


def registry_bytes(doc: dict) -> bytes:
    return (json.dumps(doc, indent=2) + "\n").encode()


def evidence(product: str, registry_sha: str) -> dict:
    reg = registry_doc()
    row = next(x for x in reg["candidates"] if x["app"] == product)
    keys = list(MOD.COMMON_MANUAL) + list(MOD.PRODUCT_MANUAL[product])
    manual = {
        key: {"pass": True, "observed_at_utc": "2026-09-14T00:00:00Z", "evidence_ref": f"evidence/{product}/{key}.mp4"}
        for key in keys
    }
    return {
        "schema": MOD.SCHEMA,
        "product": product,
        "registry_sha256": registry_sha,
        "package": row["package"],
        "exact_candidate_sha256": row["apk_sha256"],
        "device": {
            "physical_device": True,
            "emulator_detected": False,
            "fingerprint_sha256": "a" * 64,
            "model": "Physical Phone",
            "sdk": "36",
        },
        "objective": {
            "install_pass": True,
            "cold_launch_pass": True,
            "background_resume_pass": True,
            "crash_free_smoke_pass": True,
            "total_pss_kb": 123456,
            "framestats_rows": 120,
            "thermal_snapshot_present": True,
            "fatal_runtime_markers": [],
        },
        "performance_observation": {
            "fps_observed": 55.0,
            "ram_mb_observed": 321.5,
            "thermal_status_observed": "nominal",
            "observation_seconds": 60,
        },
        "manual_observations": manual,
        "online_state_not_faked": True,
        "local_mode_genuinely_local": True,
        "final_or_play_ready": False,
    }


class DeviceEvidenceV3Tests(unittest.TestCase):
    def setUp(self):
        self.registry = registry_doc()
        self.raw = registry_bytes(self.registry)
        self.registry_sha = hashlib.sha256(self.raw).hexdigest()

    def errors(self, product: str, mutate=None):
        doc = evidence(product, self.registry_sha)
        if mutate:
            mutate(doc)
        return MOD.validate(self.registry, self.registry_sha, doc)

    def test_all_products_accept_complete_exact_physical_evidence(self):
        for product in MOD.PRODUCT_MANUAL:
            with self.subTest(product=product):
                self.assertEqual([], self.errors(product))

    def test_rejects_registry_replay_or_rebind(self):
        errors = self.errors("terra", lambda d: d.__setitem__("registry_sha256", "f" * 64))
        self.assertTrue(any("registry SHA mismatch" in x for x in errors))

    def test_rejects_wrong_apk_sha(self):
        errors = self.errors("spark", lambda d: d.__setitem__("exact_candidate_sha256", "e" * 64))
        self.assertTrue(any("APK SHA mismatch" in x for x in errors))

    def test_rejects_emulator(self):
        def mutate(d):
            d["device"]["physical_device"] = False
            d["device"]["emulator_detected"] = True
        errors = self.errors("terra", mutate)
        self.assertTrue(any("emulator" in x.lower() or "physical_device" in x for x in errors))

    def test_rift_requires_combat_observation_and_ref(self):
        def mutate(d):
            d["manual_observations"]["combat"] = {"pass": False, "observed_at_utc": "", "evidence_ref": ""}
        errors = self.errors("rift", mutate)
        self.assertTrue(any("combat" in x for x in errors))

    def test_rush_requires_sensor_and_repetition_evidence(self):
        def mutate(d):
            d["manual_observations"].pop("sensor_motion")
            d["manual_observations"].pop("repetition_counting")
        errors = self.errors("rush", mutate)
        self.assertTrue(any("sensor_motion" in x for x in errors))
        self.assertTrue(any("repetition_counting" in x for x in errors))

    def test_rejects_fake_online_or_nonlocal_local_mode(self):
        def mutate(d):
            d["online_state_not_faked"] = False
            d["local_mode_genuinely_local"] = False
        errors = self.errors("learn_games", mutate)
        self.assertTrue(any("online_state_not_faked" in x for x in errors))
        self.assertTrue(any("local_mode_genuinely_local" in x for x in errors))

    def test_requires_real_frame_and_performance_observation(self):
        def mutate(d):
            d["objective"]["framestats_rows"] = 0
            d["performance_observation"]["fps_observed"] = 0
        errors = self.errors("fitness_games", mutate)
        self.assertTrue(any("framestats_rows" in x for x in errors))
        self.assertTrue(any("fps_observed" in x for x in errors))

    def test_input_cannot_self_declare_final(self):
        errors = self.errors("terra", lambda d: d.__setitem__("final_or_play_ready", True))
        self.assertTrue(any("FINAL" in x for x in errors))


if __name__ == "__main__":
    unittest.main()
