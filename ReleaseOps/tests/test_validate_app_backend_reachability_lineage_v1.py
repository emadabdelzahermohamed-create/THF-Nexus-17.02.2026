import json
import tempfile
import unittest
from pathlib import Path

from ReleaseOps.validators.validate_app_backend_reachability_lineage_v1 import validate


SHA = {
    "pulse": "1" * 64,
    "forge": "2" * 64,
    "spark": "3" * 64,
}


def registry(*, spark_status="PENDING_PHYSICAL_PHONE"):
    return {
        "policy": "MOBILE_REAL_FUNCTION_RELEASE_POLICY",
        "truth_boundary": {"final_or_play_ready": False},
        "candidates": [
            {"name": "core", "source_sha256": "0" * 64, "status": "PENDING_PHYSICAL_PHONE"},
            {"name": "pulse", "source_sha256": SHA["pulse"], "status": "PENDING_PHYSICAL_PHONE"},
            {"name": "forge", "source_sha256": SHA["forge"], "status": "PENDING_PHYSICAL_PHONE"},
            {"name": "spark", "source_sha256": SHA["spark"], "status": spark_status},
        ],
        "superseded_candidates": [
            {"name": "spark", "source_sha256": "9" * 64},
        ],
    }


def matrix(**overrides):
    values = dict(SHA)
    values.update(overrides)
    return "".join(
        f"{app}\tRC4\t{values[app]}\tdrive-{app}\n"
        for app in ("pulse", "forge", "spark")
    )


class BackendReachabilityLineageTests(unittest.TestCase):
    def run_validate(self, matrix_text, registry_data):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            m = root / "matrix.tsv"
            r = root / "registry.json"
            m.write_text(matrix_text, encoding="utf-8")
            r.write_text(json.dumps(registry_data), encoding="utf-8")
            return validate(m, r)

    def test_current_lineage_passes_without_promoting_readiness(self):
        report = self.run_validate(matrix(), registry())
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["bound_app_count"], 3)
        self.assertFalse(report["physical_device_pass"])
        self.assertFalse(report["final_or_play_ready"])

    def test_current_sha_drift_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "authoritative candidate SHA"):
            self.run_validate(matrix(spark="8" * 64), registry())

    def test_superseded_source_is_explicitly_rejected(self):
        with self.assertRaisesRegex(ValueError, "superseded source SHA"):
            self.run_validate(matrix(spark="9" * 64), registry())

    def test_missing_app_fails_closed(self):
        incomplete = matrix().splitlines()[:-1]
        with self.assertRaisesRegex(ValueError, "app set drift"):
            self.run_validate("\n".join(incomplete) + "\n", registry())

    def test_duplicate_app_fails_closed(self):
        duplicate = matrix() + f"spark\tRC4\t{SHA['spark']}\tdrive-spark-2\n"
        with self.assertRaisesRegex(ValueError, "duplicate backend matrix app"):
            self.run_validate(duplicate, registry())

    def test_promoted_device_status_is_not_accepted_by_network_evidence_gate(self):
        with self.assertRaisesRegex(ValueError, "unexpected candidate status"):
            self.run_validate(matrix(), registry(spark_status="PASS"))


if __name__ == "__main__":
    unittest.main()
