#!/usr/bin/env python3
import unittest

import evidence_artifact_binding
import github_evidence_metadata as metadata

HEAD = "a" * 40
CAPTURED = "2026-09-12T15:00:00Z"
RUN_ID = 34698167873
ARTIFACT_ID = 10298854247


def run_fixture():
    return {
        "id": RUN_ID,
        "name": "THF Token Read-Only Audit",
        "path": ".github/workflows/thf-token-readonly-audit.yml",
        "head_branch": evidence_artifact_binding.TOKENOPS_BRANCH,
        "head_sha": HEAD,
        "event": "push",
        "status": "completed",
        "conclusion": "success",
        "run_attempt": 1,
        "created_at": "2026-09-12T14:03:40Z",
        "run_started_at": "2026-09-12T14:03:40Z",
        "updated_at": "2026-09-12T14:04:21Z",
    }


def artifact_fixture():
    return {
        "id": ARTIFACT_ID,
        "name": evidence_artifact_binding.READONLY_ARTIFACT_NAME,
        "size_in_bytes": 5150,
        "digest": "sha256:" + ("b" * 64),
        "expired": False,
        "created_at": "2026-09-12T14:04:19Z",
        "updated_at": "2026-09-12T14:04:19Z",
        "expires_at": "2026-10-12T14:04:19Z",
        "workflow_run": {
            "id": RUN_ID,
            "head_branch": evidence_artifact_binding.TOKENOPS_BRANCH,
            "head_sha": HEAD,
        },
    }


class GithubEvidenceMetadataTests(unittest.TestCase):
    def build(self):
        return metadata.build(
            run_fixture(), artifact_fixture(),
            evidence_artifact_binding.READONLY_ARTIFACT_NAME,
            HEAD, CAPTURED,
        )

    def test_build_and_verify(self):
        out = self.build()
        verified = metadata.verify(out)
        self.assertTrue(verified["verified"])
        self.assertFalse(out["transaction_created"])
        self.assertFalse(out["transaction_signed"])
        self.assertFalse(out["broadcast_allowed"])
        self.assertFalse(out["financial_effect"])
        self.assertEqual(out["artifact"]["artifact_id"], ARTIFACT_ID)
        self.assertEqual(out["workflow_run"]["workflow_run_id"], RUN_ID)

    def test_tamper_fails_closed(self):
        out = self.build()
        out["artifact"]["artifact_id"] += 1
        with self.assertRaises(ValueError):
            metadata.verify(out)

    def test_run_artifact_mismatch_fails_closed(self):
        artifact = artifact_fixture()
        artifact["workflow_run"]["id"] += 1
        with self.assertRaises(ValueError):
            metadata.build(
                run_fixture(), artifact,
                evidence_artifact_binding.READONLY_ARTIFACT_NAME,
                HEAD, CAPTURED,
            )

    def test_head_mismatch_fails_closed(self):
        artifact = artifact_fixture()
        artifact["workflow_run"]["head_sha"] = "c" * 40
        with self.assertRaises(ValueError):
            metadata.build(
                run_fixture(), artifact,
                evidence_artifact_binding.READONLY_ARTIFACT_NAME,
                HEAD, CAPTURED,
            )

    def test_expired_artifact_fails_closed(self):
        artifact = artifact_fixture()
        artifact["expired"] = True
        with self.assertRaises(ValueError):
            metadata.build(
                run_fixture(), artifact,
                evidence_artifact_binding.READONLY_ARTIFACT_NAME,
                HEAD, CAPTURED,
            )

    def test_artifact_expired_by_capture_time_fails_closed(self):
        artifact = artifact_fixture()
        artifact["expires_at"] = "2026-09-12T14:30:00Z"
        with self.assertRaises(ValueError):
            metadata.build(
                run_fixture(), artifact,
                evidence_artifact_binding.READONLY_ARTIFACT_NAME,
                HEAD, CAPTURED,
            )

    def test_unsuccessful_run_fails_closed(self):
        run = run_fixture()
        run["conclusion"] = "failure"
        with self.assertRaises(ValueError):
            metadata.build(
                run, artifact_fixture(),
                evidence_artifact_binding.READONLY_ARTIFACT_NAME,
                HEAD, CAPTURED,
            )

    def test_secret_field_fails_closed(self):
        run = run_fixture()
        run["private_key"] = "forbidden"
        with self.assertRaises(ValueError):
            metadata.build(
                run, artifact_fixture(),
                evidence_artifact_binding.READONLY_ARTIFACT_NAME,
                HEAD, CAPTURED,
            )


if __name__ == "__main__":
    unittest.main()
