#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v10 import AppDeviceEvidenceV10Tests
from validate_app_device_evidence_v11 import (
    FOREGROUND_CHECKS,
    LIFECYCLE_CHECKS,
    PROCESS_METHOD,
    _active_foreground_checks,
    validate,
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV11Tests(AppDeviceEvidenceV10Tests):
    def setUp(self) -> None:
        super().setUp()
        self.active_checks = _active_foreground_checks(self.registry)
        if not self.active_checks:
            raise AssertionError("V10 fixture must activate at least one V11 foreground check")
        self.proc_paths = {}
        provenance = {}
        for index, check in enumerate(self.active_checks, start=1):
            path = self.root / f"process-{check}.v11.txt"
            self.proc_paths[check] = path
            self._write_process(check, path, pid=str(4200 + index))
            provenance[check] = {
                "evidence_ref": path.name,
                "evidence_sha256": digest(path),
            }
        self.evidence["process_provenance"] = provenance

    def _pick(self, preferred=None, *, exclude=None):
        if preferred in self.active_checks and preferred != exclude:
            return preferred
        for check in self.active_checks:
            if check != exclude:
                return check
        raise AssertionError("not enough active foreground checks")

    def _bound_sha(self, check):
        semantic = self.evidence.get("semantic_observations", {})
        if check in semantic:
            return semantic[check]["evidence_sha256"]
        if check in LIFECYCLE_CHECKS:
            return self.evidence["lifecycle_touch_orientation_observation"]["evidence_sha256"]
        if check == "offline_network":
            return self.evidence["offline_network_observation"]["evidence_sha256"]
        raise KeyError(check)

    def _write_process(self, check, path, *, pid="4242", resumed_pid=None, package=None, bound_sha=None, method=None):
        values = {
            "THF_SESSION_ID": self.sid,
            "THF_PACKAGE": package or self.package,
            "THF_CANDIDATE_SHA256": self.sha,
            "THF_SOURCE_SHA256": self.source_sha,
            "THF_DEVICE_FINGERPRINT_SHA256": "c" * 64,
            "THF_CHECK": check,
            "THF_FOREGROUND_PACKAGE": package or self.package,
            "THF_FOREGROUND_PID": pid,
            "THF_RESUMED_PID": resumed_pid if resumed_pid is not None else pid,
            "THF_ACTIVITY_RESUMED": "TRUE",
            "THF_PROCESS_CAPTURE_METHOD": method or PROCESS_METHOD,
            "THF_PROCESS_ALIVE_AFTER": "TRUE",
            "THF_BOUND_EVIDENCE_SHA256": bound_sha or self._bound_sha(check),
        }
        path.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")

    def _refresh_process(self, item, check):
        item["process_provenance"][check]["evidence_sha256"] = digest(self.proc_paths[check])

    def test_valid_v11_foreground_process_chain(self):
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_process_provenance_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = self._pick("core_user_journey")
        item["process_provenance"].pop(check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_foreground_package_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = self._pick("touch")
        self._write_process(check, self.proc_paths[check], package=self.package + ".other")
        self._refresh_process(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_bound_sha_substitution_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = self._pick("core_user_journey")
        self._write_process(check, self.proc_paths[check], bound_sha="f" * 64)
        self._refresh_process(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_resumed_pid_mismatch_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = self._pick("background_resume")
        self._write_process(check, self.proc_paths[check], pid="4242", resumed_pid="4243")
        self._refresh_process(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_invalid_process_method_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = self._pick("launch")
        self._write_process(check, self.proc_paths[check], method="MANUAL_NOTE")
        self._refresh_process(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_process_file_blocks(self):
        if len(self.active_checks) < 2:
            self.skipTest("fixture has fewer than two active foreground checks")
        item = copy.deepcopy(self.evidence)
        first = self.active_checks[0]
        second = self.active_checks[1]
        item["process_provenance"][second] = copy.deepcopy(item["process_provenance"][first])
        self.assertTrue(validate(self.registry, item, self.root))

    def test_production_foreground_policy_constant_is_nontrivial(self):
        self.assertIn("touch", FOREGROUND_CHECKS)
        self.assertIn("background_resume", FOREGROUND_CHECKS)
        self.assertIn("core_user_journey", FOREGROUND_CHECKS)
        self.assertIn("notification_tap_deeplink", FOREGROUND_CHECKS)


if __name__ == "__main__":
    unittest.main(verbosity=2)
