#!/usr/bin/env python3
from __future__ import annotations

import copy
import hashlib
import unittest

from test_validate_app_device_evidence_v7 import AppDeviceEvidenceV7Tests
from validate_app_device_evidence_v8 import APPROVED_NETWORK_METHOD, validate


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class AppDeviceEvidenceV8Tests(AppDeviceEvidenceV7Tests):
    def setUp(self) -> None:
        super().setUp()
        self.network = self.root / "network.v8.txt"
        self._write_network()
        self.evidence["offline_network_observation"] = {
            "session_id": self.sid,
            "package": self.package,
            "candidate_sha256": self.sha,
            "source_sha256": self.source_sha,
            "device_fingerprint_sha256": "c" * 64,
            "method": APPROVED_NETWORK_METHOD,
            "offline_reached": True,
            "local_mode_stayed_local": True,
            "no_online_state_faked": True,
            "online_restored": True,
            "process_same_pid": True,
            "started_at_utc": "2026-09-14T05:07:35Z",
            "ended_at_utc": "2026-09-14T05:09:30Z",
            "evidence_ref": self.network.name,
            "evidence_sha256": digest(self.network),
        }

    def _write_network(self, extra: str = "", **overrides: str) -> None:
        values = {
            "THF_SESSION_ID": self.sid,
            "THF_PACKAGE": self.package,
            "THF_CANDIDATE_SHA256": self.sha,
            "THF_SOURCE_SHA256": self.source_sha,
            "THF_DEVICE_FINGERPRINT_SHA256": "c" * 64,
            "THF_OBS_STARTED_AT_UTC": "2026-09-14T05:07:35Z",
            "THF_OBS_ENDED_AT_UTC": "2026-09-14T05:09:30Z",
            "THF_OFFLINE_REACHED": "TRUE",
            "THF_LOCAL_MODE_STAYED_LOCAL": "TRUE",
            "THF_ONLINE_STATE_FAKED": "FALSE",
            "THF_ONLINE_RESTORED": "TRUE",
            "THF_NETWORK_PID_SAME": "TRUE",
            "THF_NETWORK_PID_BEFORE": "4242",
            "THF_NETWORK_PID_AFTER": "4242",
        }
        values.update(overrides)
        head = "".join(f"{k}={v}\n" for k, v in values.items())
        stages = "THF_STAGE=OFFLINE_CONFIRMED\nTHF_STAGE=LOCAL_APP_OPERATION_OBSERVED\nTHF_STAGE=ONLINE_RESTORED\n"
        self.network.write_text(head + stages + extra, encoding="utf-8")

    def _refresh_network(self, item: dict) -> None:
        item["offline_network_observation"]["evidence_sha256"] = digest(self.network)

    def test_valid_v8_network_chain(self) -> None:
        self.assertEqual(validate(self.registry, self.evidence, self.root), [])

    def test_missing_network_observation_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item.pop("offline_network_observation")
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_package_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["package"] = "com.example.other"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_cross_session_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["session_id"] = "other-session"
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_source_lineage_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["source_sha256"] = "f" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_wrong_device_fingerprint_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["device_fingerprint_sha256"] = "d" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_false_local_mode_claim_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["local_mode_stayed_local"] = False
        self.assertTrue(validate(self.registry, item, self.root))

    def test_stage_reorder_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        text = self.network.read_text(encoding="utf-8")
        old = "THF_STAGE=OFFLINE_CONFIRMED\nTHF_STAGE=LOCAL_APP_OPERATION_OBSERVED\nTHF_STAGE=ONLINE_RESTORED\n"
        new = "THF_STAGE=LOCAL_APP_OPERATION_OBSERVED\nTHF_STAGE=OFFLINE_CONFIRMED\nTHF_STAGE=ONLINE_RESTORED\n"
        self.network.write_text(text.replace(old, new), encoding="utf-8")
        self._refresh_network(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_duplicate_online_truth_marker_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self._write_network(extra="THF_ONLINE_RESTORED=TRUE\n")
        self._refresh_network(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_pid_change_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        self._write_network(THF_NETWORK_PID_AFTER="4243")
        self._refresh_network(item)
        self.assertTrue(validate(self.registry, item, self.root))

    def test_sha_tamper_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["evidence_sha256"] = "f" * 64
        self.assertTrue(validate(self.registry, item, self.root))

    def test_unapproved_method_blocks(self) -> None:
        item = copy.deepcopy(self.evidence)
        item["offline_network_observation"]["method"] = "manual-toggle"
        self.assertTrue(validate(self.registry, item, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
