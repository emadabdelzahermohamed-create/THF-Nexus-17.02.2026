#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v10 import AppDeviceEvidenceV10Tests
from validate_app_device_evidence_v11 import FOREGROUND_CHECKS, PROCESS_METHOD, validate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV11Tests(AppDeviceEvidenceV10Tests):
    def setUp(self) -> None:
        super().setUp()
        self.proc_paths = {}
        provenance = {}
        for index, check in enumerate(FOREGROUND_CHECKS, start=1):
            path = self.root / f"process-{check}.v11.txt"
            self.proc_paths[check] = path
            self._write_process(check, path, pid=str(4200 + index))
            provenance[check] = {
                "evidence_ref": path.name,
                "evidence_sha256": digest(path),
            }
        self.evidence["process_provenance"] = provenance

    def _semantic_sha(self, check):
        return self.evidence["semantic_observations"][check]["evidence_sha256"]

    def _write_process(self, check, path, *, pid="4242", resumed_pid=None, package=None, semantic_sha=None, method=None):
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
            "THF_SEMANTIC_EVIDENCE_SHA256": semantic_sha or self._semantic_sha(check),
        }
        path.write_text("".join(f"{k}={v}\n" for k, v in values.items()), encoding="utf-8")

    def _refresh(self, item, check):
        item["process_provenance"][check]["evidence_sha256"] = digest(self.proc_paths[check])

    def test_valid_v11_foreground_process_chain(self):
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_process_provenance_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["process_provenance"].pop("core_user_journey")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_foreground_package_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = "touch"
        self._write_process(check, self.proc_paths[check], package=self.package + ".other")
        self._refresh(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_semantic_sha_substitution_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = "core_user_journey"
        self._write_process(check, self.proc_paths[check], semantic_sha="f" * 64)
        self._refresh(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_resumed_pid_mismatch_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = "background_resume"
        self._write_process(check, self.proc_paths[check], pid="4242", resumed_pid="4243")
        self._refresh(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_invalid_process_method_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = "launch"
        self._write_process(check, self.proc_paths[check], method="MANUAL_NOTE")
        self._refresh(item, check)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_process_file_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["process_provenance"]["touch"] = copy.deepcopy(item["process_provenance"]["launch"])
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
