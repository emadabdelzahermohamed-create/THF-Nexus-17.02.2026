#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v11 import AppDeviceEvidenceV11Tests, digest
from validate_app_device_evidence_v11 import FOREGROUND_CHECKS
from validate_app_device_evidence_v12 import BOOT_METHOD, validate


BOOT_UUID = "123e4567-e89b-12d3-a456-426614174000"
BOOT_SHA = hashlib.sha256(BOOT_UUID.encode("utf-8")).hexdigest()


class AppDeviceEvidenceV12Tests(AppDeviceEvidenceV11Tests):
    def setUp(self) -> None:
        super().setUp()
        self.boot_path = self.root / "android-boot.v12.txt"
        self._write_boot()
        self.evidence["device_boot"] = {
            "evidence_ref": self.boot_path.name,
            "evidence_sha256": digest(self.boot_path),
            "boot_id_sha256": BOOT_SHA,
        }
        for check in FOREGROUND_CHECKS:
            path = self.proc_paths[check]
            text = path.read_text(encoding="utf-8")
            path.write_text(text + f"THF_BOOT_ID_SHA256={BOOT_SHA}\n", encoding="utf-8")
            self.evidence["process_provenance"][check]["evidence_sha256"] = digest(path)

    def _write_boot(self, *, raw_uuid=BOOT_UUID, declared_sha=BOOT_SHA, method=BOOT_METHOD, exit_code="0"):
        text = (
            f"THF_SESSION_ID={self.sid}\n"
            f"THF_DEVICE_FINGERPRINT_SHA256={'c' * 64}\n"
            f"THF_BOOT_CAPTURE_METHOD={method}\n"
            f"THF_BOOT_ID_SHA256={declared_sha}\n"
            f"THF_ADB_EXIT_CODE={exit_code}\n"
            "THF_ADB_STDOUT_BEGIN\n"
            f"{raw_uuid}\n"
            "THF_ADB_STDOUT_END\n"
        )
        self.boot_path.write_text(text, encoding="utf-8")

    def _refresh_boot(self, item):
        item["device_boot"]["evidence_sha256"] = digest(self.boot_path)

    def _replace_process_boot(self, check, new_sha):
        path = self.proc_paths[check]
        text = path.read_text(encoding="utf-8")
        text = text.replace(f"THF_BOOT_ID_SHA256={BOOT_SHA}", f"THF_BOOT_ID_SHA256={new_sha}")
        path.write_text(text, encoding="utf-8")

    def test_valid_v12_boot_chain(self):
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_boot_evidence_blocks(self):
        item = copy.deepcopy(self.evidence)
        item.pop("device_boot")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_boot_uuid_substitution_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_boot(raw_uuid="223e4567-e89b-12d3-a456-426614174000")
        self._refresh_boot(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_declared_boot_hash_substitution_blocks(self):
        item = copy.deepcopy(self.evidence)
        wrong = "f" * 64
        item["device_boot"]["boot_id_sha256"] = wrong
        self._write_boot(declared_sha=wrong)
        self._refresh_boot(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_boot_capture_method_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_boot(method="MANUAL_NOTE")
        self._refresh_boot(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_failed_adb_boot_capture_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_boot(exit_code="1")
        self._refresh_boot(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_process_from_other_boot_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = "core_user_journey"
        self._replace_process_boot(check, "e" * 64)
        item["process_provenance"][check]["evidence_sha256"] = digest(self.proc_paths[check])
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_process_boot_marker_blocks(self):
        item = copy.deepcopy(self.evidence)
        check = "touch"
        path = self.proc_paths[check]
        path.write_text(path.read_text(encoding="utf-8") + f"THF_BOOT_ID_SHA256={BOOT_SHA}\n", encoding="utf-8")
        item["process_provenance"][check]["evidence_sha256"] = digest(path)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_boot_file_aliasing_process_file_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["device_boot"]["evidence_ref"] = item["process_provenance"]["launch"]["evidence_ref"]
        item["device_boot"]["evidence_sha256"] = item["process_provenance"]["launch"]["evidence_sha256"]
        self.assertTrue(validate(self.registry, item, self.root))

    def test_noncanonical_boot_uuid_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_boot(raw_uuid=BOOT_UUID.upper())
        self._refresh_boot(item)
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
