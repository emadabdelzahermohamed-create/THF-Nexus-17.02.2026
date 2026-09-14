#!/usr/bin/env python3
import copy
import unittest

from validate_game_authoritative_source_lock_v1 import REQUIRED_APPS, validate

SHA = "a" * 64


def registry():
    return {
        "schema": "thf-game-device-candidates-v1",
        "final_or_play_ready": False,
        "physical_device_status": "PENDING",
        "candidates": [{"app": app, "source_sha256": SHA} for app in sorted(REQUIRED_APPS)],
    }


def observed():
    return {
        "schema": "thf-game-authoritative-source-observation-v1",
        "read_only": True,
        "wave_untouched": True,
        "canonical_archives_mutated": False,
        "final_or_play_ready": False,
        "physical_device_evidence": "NOT_COLLECTED",
        "sources": [
            {"app": app, "source_sha256": SHA, "exists": True, "zip_integrity": True}
            for app in sorted(REQUIRED_APPS)
        ],
    }


class SourceLockTests(unittest.TestCase):
    def test_clean_lock_passes(self):
        self.assertEqual(validate(registry(), observed()), [])

    def test_source_drift_fails(self):
        o = observed()
        o["sources"][0]["source_sha256"] = "b" * 64
        self.assertTrue(any("SOURCE_DRIFT" in x for x in validate(registry(), o)))

    def test_missing_source_fails(self):
        o = observed()
        o["sources"][0]["exists"] = False
        self.assertTrue(any("authoritative_source_missing" in x for x in validate(registry(), o)))

    def test_zip_integrity_required(self):
        o = observed()
        o["sources"][0]["zip_integrity"] = False
        self.assertTrue(any("zip_integrity_not_proven" in x for x in validate(registry(), o)))

    def test_wave_isolation_required(self):
        o = observed(); o["wave_untouched"] = False
        self.assertIn("wave_isolation_not_proven", validate(registry(), o))

    def test_canonical_mutation_rejected(self):
        o = observed(); o["canonical_archives_mutated"] = True
        self.assertIn("canonical_mutation_detected", validate(registry(), o))

    def test_readiness_self_promotion_rejected(self):
        r = registry(); r["final_or_play_ready"] = True
        self.assertIn("registry_must_not_self_promote", validate(r, observed()))
        o = observed(); o["final_or_play_ready"] = True
        self.assertIn("observation_must_not_promote_readiness", validate(registry(), o))

    def test_exact_six_app_set_required(self):
        o = observed(); o["sources"].pop()
        self.assertIn("observation_app_set_mismatch", validate(registry(), o))


if __name__ == "__main__":
    unittest.main()
