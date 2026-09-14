#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v6 import AppDeviceEvidenceV6Tests
from validate_app_device_evidence_v7 import validate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV7Tests(AppDeviceEvidenceV6Tests):
    def setUp(self) -> None:
        super().setUp()
        text = self.lifecycle.read_text(encoding="utf-8")
        text += f"THF_DEVICE_FINGERPRINT_SHA256={'c' * 64}\n"
        text += "THF_OBS_STARTED_AT_UTC=2026-09-14T05:04:30Z\n"
        text += "THF_OBS_ENDED_AT_UTC=2026-09-14T05:07:30Z\n"
        self.lifecycle.write_text(text, encoding="utf-8")
        self.evidence["lifecycle_touch_orientation_observation"]["evidence_sha256"] = digest(self.lifecycle)

    def _refresh_v7(self, item: dict) -> None:
        item["lifecycle_touch_orientation_observation"]["evidence_sha256"] = digest(self.lifecycle)

    def test_valid_v7_exact_device_bound_chain(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_substring_package_spoof_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        text = self.lifecycle.read_text(encoding="utf-8").replace(
            f"THF_PACKAGE={self.package}\n", f"THF_PACKAGE={self.package}.attacker\n"
        )
        self.lifecycle.write_text(text, encoding="utf-8")
        self._refresh_v7(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_identity_key_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        with self.lifecycle.open("a", encoding="utf-8") as fh:
            fh.write(f"THF_PACKAGE={self.package}\n")
        self._refresh_v7(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_device_fingerprint_substitution_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        text = self.lifecycle.read_text(encoding="utf-8").replace(
            f"THF_DEVICE_FINGERPRINT_SHA256={'c' * 64}",
            f"THF_DEVICE_FINGERPRINT_SHA256={'d' * 64}",
        )
        self.lifecycle.write_text(text, encoding="utf-8")
        self._refresh_v7(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_observation_interval_substitution_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        text = self.lifecycle.read_text(encoding="utf-8").replace(
            "THF_OBS_ENDED_AT_UTC=2026-09-14T05:07:30Z",
            "THF_OBS_ENDED_AT_UTC=2026-09-14T05:07:31Z",
        )
        self.lifecycle.write_text(text, encoding="utf-8")
        self._refresh_v7(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_truth_marker_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        with self.lifecycle.open("a", encoding="utf-8") as fh:
            fh.write("THF_TOUCH_OBSERVED=FALSE\n")
        self._refresh_v7(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_emulator_claim_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["device"]["emulator_detected"] = True
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
