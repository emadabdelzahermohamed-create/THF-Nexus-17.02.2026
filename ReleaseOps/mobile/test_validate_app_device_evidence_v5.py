#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
from pathlib import Path
import unittest

from test_validate_app_device_evidence_v4 import AppDeviceEvidenceV4Tests
from validate_app_device_evidence_v5 import APPROVED_METHODS, RAW_MARKERS, validate


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV5Tests(AppDeviceEvidenceV4Tests):
    def setUp(self) -> None:
        super().setUp()
        self.evidence["semantic_observations"] = {}
        self._semantic("install", "2026-09-14T05:03:20Z")
        self._semantic("launch", "2026-09-14T05:04:20Z")

    def _raw_text(self, check: str) -> str:
        return "\n".join(RAW_MARKERS[check]) + "\n"

    def _semantic(self, check: str, observed: str) -> None:
        raw = self.root / f"{check}.raw.txt"
        raw.write_text(self._raw_text(check), encoding="utf-8")
        raw_sha = digest(raw)
        manifest = self.root / f"{check}.semantic.v5.txt"
        values = {
            "THF_APP_SEMANTIC_V5": "1",
            "SESSION_ID": self.sid,
            "PACKAGE": self.package,
            "CANDIDATE_SHA256": self.sha,
            "SOURCE_SHA256": self.source_sha,
            "CHECK": check,
            "METHOD": APPROVED_METHODS[check],
            "RESULT": "PASS",
            "OBSERVED_AT_UTC": observed,
            "RAW_EVIDENCE_SHA256": raw_sha,
        }
        manifest.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")
        self.evidence["semantic_observations"][check] = {
            "pass": True,
            "method": APPROVED_METHODS[check],
            "observed_at_utc": observed,
            "evidence_ref": manifest.name,
            "evidence_sha256": digest(manifest),
            "raw_evidence_ref": raw.name,
            "raw_evidence_sha256": raw_sha,
        }

    def _rewrite_manifest(self, check: str, key: str, value: str) -> None:
        item = self.evidence["semantic_observations"][check]
        path = self.root / item["evidence_ref"]
        lines = path.read_text(encoding="utf-8").splitlines()
        lines = [f"{key}={value}" if line.startswith(f"{key}=") else line for line in lines]
        path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        item["evidence_sha256"] = digest(path)

    def test_valid_semantic_probe_chain(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_declared_v3_pass_without_semantic_probe_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item.pop("semantic_observations")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_missing_required_semantic_check_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["semantic_observations"].pop("launch")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_unregistered_extra_semantic_check_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["semantic_observations"]["fake"] = copy.deepcopy(item["semantic_observations"]["launch"])
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_probe_method_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["semantic_observations"]["launch"]["method"] = "manual-observation"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_capture_sha_tamper_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["semantic_observations"]["launch"]["raw_evidence_sha256"] = "f" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_capture_missing_required_marker_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        raw = self.root / item["semantic_observations"]["launch"]["raw_evidence_ref"]
        raw.write_text("ACTIVITY com.topherofit.thf.core/.MainActivity\n", encoding="utf-8")
        item["semantic_observations"]["launch"]["raw_evidence_sha256"] = digest(raw)
        self._rewrite_manifest("launch", "RAW_EVIDENCE_SHA256", digest(raw))
        item["semantic_observations"]["launch"]["evidence_sha256"] = digest(self.root / item["semantic_observations"]["launch"]["evidence_ref"])
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_capture_must_be_distinct_from_manifest(self) -> None:
        item = copy.deepcopy(self.evidence)
        sem = item["semantic_observations"]["install"]
        sem["raw_evidence_ref"] = sem["evidence_ref"]
        sem["raw_evidence_sha256"] = sem["evidence_sha256"]
        self.assertTrue(validate(self.registry, item, self.root))

    def test_semantic_manifest_wrong_package_blocks(self) -> None:
        self._rewrite_manifest("launch", "PACKAGE", "com.example.other")
        self.assertTrue(validate(self.registry, self.evidence, self.root))

    def test_semantic_observation_outside_session_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["semantic_observations"]["launch"]["observed_at_utc"] = "2026-09-14T06:00:00Z"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_semantic_pass_false_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["semantic_observations"]["launch"]["pass"] = False
        self.assertTrue(validate(self.registry, item, self.root))

    def test_policy_method_coverage_is_complete(self) -> None:
        policy = {
            "install", "launch", "touch", "responsive_layout", "orientation",
            "background_resume", "offline_network", "core_user_journey",
            "accessibility", "data_saver", "rtl", "localization_20_language_readiness",
            "notification_permission", "notification_channel", "notification_receive",
            "notification_tap_deeplink",
        }
        self.assertEqual(set(APPROVED_METHODS), policy)
        self.assertEqual(set(RAW_MARKERS), policy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
