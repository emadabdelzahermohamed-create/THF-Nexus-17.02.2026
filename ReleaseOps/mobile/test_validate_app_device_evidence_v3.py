#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from validate_app_device_evidence_v3 import validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV3Tests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.sha = "a" * 64
        self.source_sha = "e" * 64
        self.package = "com.topherofit.thf.core"
        self.sid = "device-session-1"
        self.registry = {
            "truth_boundary": {"all_pending": True, "final_or_play_ready": False},
            "required_checks": ["install", "launch"],
            "candidates": [{
                "name": "core", "package": self.package,
                "apk_sha256": self.sha, "source_sha256": self.source_sha,
                "status": "PENDING_PHYSICAL_PHONE"
            }],
        }
        self._write_objective()
        self._write_check("install", "2026-09-14T05:03:00Z")
        self._write_check("launch", "2026-09-14T05:04:00Z")
        self.evidence = {
            "product": "core", "package": self.package, "exact_candidate_sha256": self.sha,
            "device": {"physical_device": True, "emulator_detected": False, "fingerprint_sha256": "c" * 64},
            "session": {"session_id": self.sid, "started_at_utc": "2026-09-14T05:00:00Z", "ended_at_utc": "2026-09-14T05:10:00Z"},
            "objective": {
                "installed_apk_sha_verified": True,
                "installed_apk_sha256": self.sha,
                "installed_code_paths": ["/data/app/~~abc/com.topherofit.thf.core-xyz/base.apk"],
                "installed_apk_hash_method": "adb-exec-out-cat",
                "installed_apk_session_id": self.sid,
                "installed_apk_observed_at_utc": "2026-09-14T05:02:00Z",
                "package_dump_present": True,
                "evidence_ref": "objective.txt", "evidence_sha256": digest(self.root / "objective.txt"),
            },
            "checks": {
                "install": {"pass": True, "observed_at_utc": "2026-09-14T05:03:00Z", "evidence_ref": "install.txt", "evidence_sha256": digest(self.root / "install.txt")},
                "launch": {"pass": True, "observed_at_utc": "2026-09-14T05:04:00Z", "evidence_ref": "launch.txt", "evidence_sha256": digest(self.root / "launch.txt")},
            },
            "final_or_play_ready": False,
        }

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def _write_objective(self, **overrides: str) -> None:
        values = {
            "THF_APP_OBJECTIVE_V3": "1", "SESSION_ID": self.sid, "PACKAGE": self.package,
            "CANDIDATE_SHA256": self.sha, "SOURCE_SHA256": self.source_sha,
            "INSTALLED_APK_SHA256": self.sha, "HASH_METHOD": "adb-exec-out-cat",
            "CODE_PATH": "/data/app/~~abc/com.topherofit.thf.core-xyz/base.apk",
            "PACKAGE_DUMP_PRESENT": "true", "OBSERVED_AT_UTC": "2026-09-14T05:02:00Z",
        }
        values.update(overrides)
        (self.root / "objective.txt").write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")

    def _write_check(self, name: str, observed: str, **overrides: str) -> None:
        values = {
            "THF_APP_EVIDENCE_V3": "1", "SESSION_ID": self.sid, "PACKAGE": self.package,
            "CANDIDATE_SHA256": self.sha, "SOURCE_SHA256": self.source_sha,
            "CHECK": name, "RESULT": "PASS", "OBSERVED_AT_UTC": observed,
        }
        values.update(overrides)
        (self.root / f"{name}.txt").write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")

    def test_valid_capture_content_binding(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_check_cross_session_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("launch", "2026-09-14T05:04:00Z", SESSION_ID="other-session")
        item["checks"]["launch"]["evidence_sha256"] = digest(self.root / "launch.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_check_wrong_candidate_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("install", "2026-09-14T05:03:00Z", CANDIDATE_SHA256="b" * 64)
        item["checks"]["install"]["evidence_sha256"] = digest(self.root / "install.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_check_wrong_source_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("install", "2026-09-14T05:03:00Z", SOURCE_SHA256="f" * 64)
        item["checks"]["install"]["evidence_sha256"] = digest(self.root / "install.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_registry_missing_source_sha_blocks(self) -> None:
        registry = copy.deepcopy(self.registry); registry["candidates"][0]["source_sha256"] = None
        self.assertTrue(validate(registry, self.evidence, self.root))

    def test_check_wrong_package_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("launch", "2026-09-14T05:04:00Z", PACKAGE="com.example.other")
        item["checks"]["launch"]["evidence_sha256"] = digest(self.root / "launch.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_check_name_substitution_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("launch", "2026-09-14T05:04:00Z", CHECK="install")
        item["checks"]["launch"]["evidence_sha256"] = digest(self.root / "launch.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_declared_pass_but_capture_fail_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("install", "2026-09-14T05:03:00Z", RESULT="FAIL")
        item["checks"]["install"]["evidence_sha256"] = digest(self.root / "install.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_capture_timestamp_mismatch_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_check("launch", "2026-09-14T05:09:00Z")
        item["checks"]["launch"]["evidence_sha256"] = digest(self.root / "launch.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_objective_wrong_installed_sha_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_objective(INSTALLED_APK_SHA256="d" * 64)
        item["objective"]["evidence_sha256"] = digest(self.root / "objective.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_objective_wrong_source_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_objective(SOURCE_SHA256="f" * 64)
        item["objective"]["evidence_sha256"] = digest(self.root / "objective.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_objective_wrong_hash_method_capture_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); self._write_objective(HASH_METHOD="adb-pull")
        item["objective"]["evidence_sha256"] = digest(self.root / "objective.txt")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_canonical_field_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); p = self.root / "install.txt"
        p.write_text(p.read_text(encoding="utf-8") + f"SESSION_ID={self.sid}\n", encoding="utf-8")
        item["checks"]["install"]["evidence_sha256"] = digest(p)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_missing_canonical_field_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); p = self.root / "launch.txt"
        lines = [x for x in p.read_text(encoding="utf-8").splitlines() if not x.startswith("PACKAGE=")]
        p.write_text("\n".join(lines) + "\n", encoding="utf-8")
        item["checks"]["launch"]["evidence_sha256"] = digest(p)
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
