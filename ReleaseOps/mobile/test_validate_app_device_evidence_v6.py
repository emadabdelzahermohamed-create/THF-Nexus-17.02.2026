#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import unittest

from test_validate_app_device_evidence_v5 import AppDeviceEvidenceV5Tests
from validate_app_device_evidence_v6 import APPROVED_LIFECYCLE_METHOD, validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV6Tests(AppDeviceEvidenceV5Tests):
    def setUp(self) -> None:
        super().setUp()
        self.lifecycle = self.root / "lifecycle.v6.txt"
        self._write_lifecycle()
        self.evidence["lifecycle_touch_orientation_observation"] = {
            "session_id": self.sid,
            "package": self.package,
            "candidate_sha256": self.sha,
            "source_sha256": self.source_sha,
            "method": APPROVED_LIFECYCLE_METHOD,
            "touch_observed": True,
            "portrait_observed": True,
            "landscape_observed": True,
            "responsive_layout_observed": True,
            "safe_area_observed": True,
            "background_resume_same_pid": True,
            "started_at_utc": "2026-09-14T05:04:30Z",
            "ended_at_utc": "2026-09-14T05:07:30Z",
            "evidence_ref": self.lifecycle.name,
            "evidence_sha256": digest(self.lifecycle),
        }

    def _write_lifecycle(self, **overrides: str) -> None:
        values = {
            "THF_SESSION_ID": self.sid,
            "THF_PACKAGE": self.package,
            "THF_CANDIDATE_SHA256": self.sha,
            "THF_SOURCE_SHA256": self.source_sha,
            "THF_TOUCH_OBSERVED": "TRUE",
            "THF_PORTRAIT_OBSERVED": "TRUE",
            "THF_LANDSCAPE_OBSERVED": "TRUE",
            "THF_RESPONSIVE_LAYOUT_OBSERVED": "TRUE",
            "THF_SAFE_AREA_OBSERVED": "TRUE",
            "THF_BACKGROUND_PID_BEFORE": "4242",
            "THF_BACKGROUND_PID_AFTER": "4242",
            "THF_BACKGROUND_RESUME_SAME_PID": "TRUE",
        }
        values.update(overrides)
        self.lifecycle.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")

    def _refresh_lifecycle(self, item: dict) -> None:
        item["lifecycle_touch_orientation_observation"]["evidence_sha256"] = digest(self.lifecycle)

    def test_valid_v6_lifecycle_chain(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_lifecycle_observation_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item.pop("lifecycle_touch_orientation_observation")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_cross_session_lifecycle_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["lifecycle_touch_orientation_observation"]["session_id"] = "other-session"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_candidate_lineage_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["lifecycle_touch_orientation_observation"]["candidate_sha256"] = "b" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_source_lineage_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["lifecycle_touch_orientation_observation"]["source_sha256"] = "f" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_transcript_identity_substitution_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self._write_lifecycle(THF_PACKAGE="com.example.other")
        self._refresh_lifecycle(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_missing_touch_marker_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        text = self.lifecycle.read_text(encoding="utf-8").replace("THF_TOUCH_OBSERVED=TRUE\n", "")
        self.lifecycle.write_text(text, encoding="utf-8")
        self._refresh_lifecycle(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_pid_change_across_resume_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self._write_lifecycle(THF_BACKGROUND_PID_AFTER="4243")
        self._refresh_lifecycle(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_non_numeric_pid_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self._write_lifecycle(THF_BACKGROUND_PID_BEFORE="pid42", THF_BACKGROUND_PID_AFTER="pid42")
        self._refresh_lifecycle(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_outside_session_interval_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["lifecycle_touch_orientation_observation"]["ended_at_utc"] = "2026-09-14T05:11:00Z"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_sha_tamper_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["lifecycle_touch_orientation_observation"]["evidence_sha256"] = "f" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_self_promotion_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["final_or_play_ready"] = True
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
