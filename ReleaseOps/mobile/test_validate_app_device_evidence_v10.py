#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v9 import AppDeviceEvidenceV9Tests
from validate_app_device_evidence_v10 import STDOUT_BEGIN, STDOUT_END, validate
from validate_app_device_evidence_v9 import APPROVED_RAW_COMMANDS, RAW_KIND_MARKERS, SUMMARY_SHA_KEYS


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV10Tests(AppDeviceEvidenceV9Tests):
    def setUp(self) -> None:
        super().setUp()
        self._write_semantic("offline", "2026-09-14T05:08:00Z")
        self._write_semantic("local", "2026-09-14T05:08:30Z")
        self._write_semantic("online", "2026-09-14T05:09:00Z")
        for kind in ("offline", "local", "online"):
            self._refresh_raw(self.evidence, kind)

    def _payload(self, kind):
        if kind == "offline":
            return "ConnectivityService\nNetworkAgentInfo [WIFI () - 100] NetworkCapabilities: INTERNET NOT_RESTRICTED"
        if kind == "local":
            return f'<?xml version="1.0" encoding="UTF-8"?><hierarchy><node package="{self.package}" text="Offline content" /></hierarchy>'
        return "ConnectivityService\nNetworkAgentInfo [WIFI () - 100] NetworkCapabilities: INTERNET VALIDATED NOT_RESTRICTED"

    def _write_semantic(self, kind, captured_at, payload=None):
        values = {
            "THF_SESSION_ID": self.sid,
            "THF_PACKAGE": self.package,
            "THF_CANDIDATE_SHA256": self.sha,
            "THF_SOURCE_SHA256": self.source_sha,
            "THF_DEVICE_FINGERPRINT_SHA256": "c" * 64,
            "THF_CAPTURED_AT_UTC": captured_at,
            "THF_ADB_COMMAND": APPROVED_RAW_COMMANDS[kind],
            "THF_ADB_EXIT_CODE": "0",
        }
        body = "".join(f"{k}={v}\n" for k, v in values.items())
        body += RAW_KIND_MARKERS[kind] + "\n"
        body += STDOUT_BEGIN + "\n" + (payload if payload is not None else self._payload(kind)) + "\n" + STDOUT_END + "\n"
        self.raw_paths[kind].write_text(body, encoding="utf-8")

    def test_valid_v10_semantic_raw_chain(self):
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_offline_validated_network_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_semantic("offline", "2026-09-14T05:08:00Z", "ConnectivityService NetworkCapabilities: INTERNET VALIDATED")
        self._refresh_raw(item, "offline")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_online_without_validated_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_semantic("online", "2026-09-14T05:09:00Z", "ConnectivityService NetworkCapabilities: INTERNET NOT_RESTRICTED")
        self._refresh_raw(item, "online")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_local_wrong_package_blocks(self):
        item = copy.deepcopy(self.evidence)
        payload = '<?xml version="1.0"?><hierarchy><node package="com.example.other" text="Fake" /></hierarchy>'
        self._write_semantic("local", "2026-09-14T05:08:30Z", payload)
        self._refresh_raw(item, "local")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_local_non_uiautomator_payload_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_semantic("local", "2026-09-14T05:08:30Z", f"package={self.package}")
        self._refresh_raw(item, "local")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_missing_stdout_bounds_blocks(self):
        item = copy.deepcopy(self.evidence)
        path = self.raw_paths["offline"]
        text = path.read_text(encoding="utf-8").replace(STDOUT_BEGIN + "\n", "").replace("\n" + STDOUT_END, "")
        path.write_text(text, encoding="utf-8")
        self._refresh_raw(item, "offline")
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
