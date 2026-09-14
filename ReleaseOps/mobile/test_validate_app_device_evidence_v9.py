#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v8 import AppDeviceEvidenceV8Tests
from validate_app_device_evidence_v9 import APPROVED_RAW_COMMANDS, RAW_CAPTURE_ORDER, RAW_KIND_MARKERS, SUMMARY_SHA_KEYS, validate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV9Tests(AppDeviceEvidenceV8Tests):
    def setUp(self) -> None:
        super().setUp()
        self.raw_paths = {}
        timestamps = {
            "offline": "2026-09-14T05:08:00Z",
            "local": "2026-09-14T05:08:30Z",
            "online": "2026-09-14T05:09:00Z",
        }
        for kind in RAW_CAPTURE_ORDER:
            path = self.root / f"raw-{kind}.v9.txt"
            self.raw_paths[kind] = path
            self._write_raw(kind, path, timestamps[kind])
        raw = {}
        for kind in RAW_CAPTURE_ORDER:
            raw[kind] = {
                "command": APPROVED_RAW_COMMANDS[kind],
                "captured_at_utc": timestamps[kind],
                "evidence_ref": self.raw_paths[kind].name,
                "evidence_sha256": digest(self.raw_paths[kind]),
            }
        self.evidence["offline_network_observation"]["raw_captures"] = raw
        self._bind_summary(raw)

    def _write_raw(self, kind, path, captured_at, *, package=None, command=None, exit_code="0", extra=""):
        values = {
            "THF_SESSION_ID": self.sid,
            "THF_PACKAGE": package or self.package,
            "THF_CANDIDATE_SHA256": self.sha,
            "THF_SOURCE_SHA256": self.source_sha,
            "THF_DEVICE_FINGERPRINT_SHA256": "c" * 64,
            "THF_CAPTURED_AT_UTC": captured_at,
            "THF_ADB_COMMAND": command or APPROVED_RAW_COMMANDS[kind],
            "THF_ADB_EXIT_CODE": exit_code,
        }
        body = "".join(f"{k}={v}\n" for k, v in values.items())
        body += RAW_KIND_MARKERS[kind] + "\n"
        body += f"RAW_ADB_STDOUT={kind}-capture-distinct\n{extra}"
        path.write_text(body, encoding="utf-8")

    def _bind_summary(self, raw):
        text = self.network.read_text(encoding="utf-8")
        text += "".join(f"{SUMMARY_SHA_KEYS[k]}={raw[k]['evidence_sha256']}\n" for k in RAW_CAPTURE_ORDER)
        self.network.write_text(text, encoding="utf-8")
        self.evidence["offline_network_observation"]["evidence_sha256"] = digest(self.network)

    def _refresh_raw(self, item, kind):
        sha = digest(self.raw_paths[kind])
        item["offline_network_observation"]["raw_captures"][kind]["evidence_sha256"] = sha
        # Replace exactly the summary binding for this kind and refresh summary digest.
        key = SUMMARY_SHA_KEYS[kind]
        lines = self.network.read_text(encoding="utf-8").splitlines()
        lines = [f"{key}={sha}" if line.startswith(key + "=") else line for line in lines]
        self.network.write_text("\n".join(lines) + "\n", encoding="utf-8")
        item["offline_network_observation"]["evidence_sha256"] = digest(self.network)

    def test_valid_v9_raw_adb_chain(self):
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_raw_captures_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"].pop("raw_captures")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_missing_one_raw_capture_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["raw_captures"].pop("local")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_raw_command_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["raw_captures"]["offline"]["command"] = "manual-toggle"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_package_substitution_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_raw("offline", self.raw_paths["offline"], "2026-09-14T05:08:00Z", package=self.package + ".attacker")
        self._refresh_raw(item, "offline")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_failed_adb_command_blocks(self):
        item = copy.deepcopy(self.evidence)
        self._write_raw("online", self.raw_paths["online"], "2026-09-14T05:09:00Z", exit_code="1")
        self._refresh_raw(item, "online")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_timestamp_reorder_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["raw_captures"]["local"]["captured_at_utc"] = "2026-09-14T05:07:50Z"
        self._write_raw("local", self.raw_paths["local"], "2026-09-14T05:07:50Z")
        self._refresh_raw(item, "local")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_raw_timestamp_outside_observation_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["raw_captures"]["offline"]["captured_at_utc"] = "2026-09-14T05:07:00Z"
        self._write_raw("offline", self.raw_paths["offline"], "2026-09-14T05:07:00Z")
        self._refresh_raw(item, "offline")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_raw_file_blocks(self):
        item = copy.deepcopy(self.evidence)
        src = item["offline_network_observation"]["raw_captures"]["offline"]
        item["offline_network_observation"]["raw_captures"]["online"]["evidence_ref"] = src["evidence_ref"]
        item["offline_network_observation"]["raw_captures"]["online"]["evidence_sha256"] = src["evidence_sha256"]
        self.assertTrue(validate(self.registry, item, self.root))

    def test_summary_raw_sha_substitution_blocks(self):
        item = copy.deepcopy(self.evidence)
        key = SUMMARY_SHA_KEYS["local"]
        text = self.network.read_text(encoding="utf-8").replace(
            f"{key}={item['offline_network_observation']['raw_captures']['local']['evidence_sha256']}",
            f"{key}={'f' * 64}",
        )
        self.network.write_text(text, encoding="utf-8")
        item["offline_network_observation"]["evidence_sha256"] = digest(self.network)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_extra_raw_capture_blocks(self):
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["raw_captures"]["extra"] = copy.deepcopy(
            item["offline_network_observation"]["raw_captures"]["offline"]
        )
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
