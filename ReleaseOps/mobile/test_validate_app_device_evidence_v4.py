#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import tempfile
import unittest

from test_validate_app_device_evidence_v3 import AppDeviceEvidenceV3Tests
from validate_app_device_evidence_v4 import validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV4Tests(AppDeviceEvidenceV3Tests):
    def setUp(self) -> None:
        super().setUp()
        self.log = self.root / "logcat.txt"
        self.log.write_text(
            "09-14 05:03:10 ActivityTaskManager: START u0 com.topherofit.thf.core/.MainActivity\n"
            "09-14 05:07:50 ActivityManager: process com.topherofit.thf.core still running\n",
            encoding="utf-8",
        )
        self.evidence["crash_observation"] = {
            "session_id": self.sid,
            "package": self.package,
            "method": "adb-logcat-epoch-package-filter",
            "started_at_utc": "2026-09-14T05:03:00Z",
            "ended_at_utc": "2026-09-14T05:08:00Z",
            "process_alive_after_core_journey": True,
            "crash_free": True,
            "evidence_ref": "logcat.txt",
            "evidence_sha256": digest(self.log),
        }

    def _refresh(self, item: dict) -> None:
        item["crash_observation"]["evidence_sha256"] = digest(self.log)

    def test_valid_logcat_binding(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_crash_observation_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item.pop("crash_observation")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_session_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["session_id"] = "other"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_package_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["package"] = "com.example.other"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_unapproved_method_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["method"] = "manual-copy"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_interval_outside_session_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["ended_at_utc"] = "2026-09-14T05:11:00Z"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_sha_tamper_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["evidence_sha256"] = "f" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_package_absent_from_log_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self.log.write_text("09-14 05:04:00 ActivityManager: unrelated process\n", encoding="utf-8")
        self._refresh(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_fatal_exception_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self.log.write_text(f"{self.package}\nFATAL EXCEPTION: main\n", encoding="utf-8")
        self._refresh(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_android_runtime_marker_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self.log.write_text(f"{self.package}\nAndroidRuntime: crash\n", encoding="utf-8")
        self._refresh(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_process_alive_false_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["process_alive_after_core_journey"] = False
        self.assertTrue(validate(self.registry, item, self.root))

    def test_declared_crash_free_false_blocks(self) -> None:
        item = copy.deepcopy(self.evidence); item["crash_observation"]["crash_free"] = False
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
