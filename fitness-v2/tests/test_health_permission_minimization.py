import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "fitness-v2" / "android" / "app" / "src" / "main" / "AndroidManifest.xml"
RECONCILIATION = ROOT / "ReleaseOps" / "FitnessStandalone" / "HEALTH_PERMISSION_RECONCILIATION_20261026.md"

BASELINE = {
    "android.permission.health.READ_STEPS",
    "android.permission.health.READ_EXERCISE",
    "android.permission.health.WRITE_EXERCISE",
    "android.permission.health.READ_DISTANCE",
    "android.permission.health.READ_ACTIVE_CALORIES_BURNED",
}
OPTIONAL_P0_HEART_RATE = "android.permission.health.READ_HEART_RATE"
DEFERRED_SCOPES = {
    "android.permission.health.READ_TOTAL_CALORIES_BURNED",
    "android.permission.health.READ_SLEEP",
    "android.permission.health.READ_RESTING_HEART_RATE",
    "android.permission.health.READ_WEIGHT",
    "android.permission.health.READ_HEIGHT",
    "android.permission.health.READ_BODY_FAT",
    "android.permission.health.READ_BASAL_METABOLIC_RATE",
    "android.permission.health.READ_OXYGEN_SATURATION",
    "android.permission.health.READ_VO2_MAX",
    "android.permission.health.READ_SPEED",
    "android.permission.health.READ_NUTRITION",
    "android.permission.health.READ_BLOOD_PRESSURE",
    "android.permission.health.READ_BLOOD_GLUCOSE",
}


class HealthPermissionMinimizationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = MANIFEST.read_text(encoding="utf-8")
        cls.reconciliation = RECONCILIATION.read_text(encoding="utf-8")
        cls.declared = set(re.findall(
            r'android:name="(android\\.permission\\.health\\.[^"]+)"',
            cls.manifest,
        ))

    def test_manifest_keeps_only_baseline_plus_optional_heart_rate(self):
        self.assertTrue(BASELINE <= self.declared)
        self.assertLessEqual(self.declared, BASELINE | {OPTIONAL_P0_HEART_RATE})
        self.assertFalse(self.declared & DEFERRED_SCOPES)

    def test_reconciliation_keeps_broad_expansion_held_and_heart_rate_narrow(self):
        self.assertIn("HOLD PR #98 unchanged", self.reconciliation)
        self.assertIn("READ_HEART_RATE only", self.reconciliation)
        self.assertIn("do not claim", self.reconciliation.lower())
        self.assertIn("physical", self.reconciliation.lower())

    def test_resting_heart_rate_is_not_substituted_for_workout_samples(self):
        self.assertNotIn("android.permission.health.READ_RESTING_HEART_RATE", self.declared)
        self.assertIn(OPTIONAL_P0_HEART_RATE, self.reconciliation)


if __name__ == "__main__":
    unittest.main()
