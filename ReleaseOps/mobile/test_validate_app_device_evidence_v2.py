#!/usr/bin/env python3
from __future__ import annotations

import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from validate_app_device_evidence_v2 import validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV2Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        for name in ("objective.txt", "install.txt", "launch.txt"):
            (self.root / name).write_text(name + "\n", encoding="utf-8")
        self.sha = "a" * 64
        self.registry = {
            "truth_boundary": {"all_pending": True, "final_or_play_ready": False},
            "required_checks": ["install", "launch"],
            "candidates": [{
                "name": "core", "package": "com.topherofit.thf.core",
                "apk_sha256": self.sha, "status": "PENDING_PHYSICAL_PHONE"
            }],
            "superseded_candidates": [{
                "name": "core", "package": "com.topherofit.thf.core",
                "apk_sha256": "b" * 64, "status": "SUPERSEDED"
            }],
        }
        self.evidence = {
            "product": "core",
            "package": "com.topherofit.thf.core",
            "exact_candidate_sha256": self.sha,
            "device": {"physical_device": True, "emulator_detected": False, "fingerprint_sha256": "c" * 64},
            "session": {"session_id": "device-session-1", "started_at_utc": "2026-09-14T05:00:00Z", "ended_at_utc": "2026-09-14T05:10:00Z"},
            "objective": {
                "installed_apk_sha_verified": True,
                "installed_apk_sha256": self.sha,
                "installed_code_paths": ["/data/app/~~abc/com.topherofit.thf.core-xyz/base.apk"],
                "installed_apk_hash_method": "adb-exec-out-cat",
                "installed_apk_session_id": "device-session-1",
                "installed_apk_observed_at_utc": "2026-09-14T05:02:00Z",
                "package_dump_present": True,
                "evidence_ref": "objective.txt",
                "evidence_sha256": digest(self.root / "objective.txt"),
            },
            "checks": {
                "install": {"pass": True, "observed_at_utc": "2026-09-14T05:03:00Z", "evidence_ref": "install.txt", "evidence_sha256": digest(self.root / "install.txt")},
                "launch": {"pass": True, "observed_at_utc": "2026-09-14T05:04:00Z", "evidence_ref": "launch.txt", "evidence_sha256": digest(self.root / "launch.txt")},
            },
            "final_or_play_ready": False,
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def assertBlocked(self, mutation) -> None:
        item = copy.deepcopy(self.evidence)
        mutation(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_valid_exact_installed_bytes(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_installed_sha_mismatch_blocks(self) -> None:
        self.assertBlocked(lambda e: e["objective"].update(installed_apk_sha256="d" * 64))

    def test_preinstall_candidate_mismatch_blocks(self) -> None:
        self.assertBlocked(lambda e: e.update(exact_candidate_sha256="b" * 64))

    def test_emulator_blocks(self) -> None:
        self.assertBlocked(lambda e: e["device"].update(physical_device=False, emulator_detected=True))

    def test_split_code_paths_block(self) -> None:
        self.assertBlocked(lambda e: e["objective"].update(installed_code_paths=["/data/app/a/base.apk", "/data/app/b/base.apk"]))

    def test_cross_session_identity_blocks(self) -> None:
        self.assertBlocked(lambda e: e["objective"].update(installed_apk_session_id="other-session"))

    def test_out_of_session_timestamp_blocks(self) -> None:
        self.assertBlocked(lambda e: e["objective"].update(installed_apk_observed_at_utc="2026-09-14T06:00:00Z"))

    def test_missing_required_check_blocks(self) -> None:
        self.assertBlocked(lambda e: e["checks"]["launch"].update(pass_=False) if False else e["checks"]["launch"].update({"pass": False}))

    def test_tampered_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        (self.root / "launch.txt").write_text("tampered\n", encoding="utf-8")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_self_promotion_blocks(self) -> None:
        self.assertBlocked(lambda e: e.update(final_or_play_ready=True))

    def test_registry_non_pending_blocks(self) -> None:
        registry = copy.deepcopy(self.registry)
        registry["candidates"][0]["status"] = "READY"
        self.assertTrue(validate(registry, self.evidence, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
