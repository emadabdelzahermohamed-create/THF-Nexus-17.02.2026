from pathlib import Path
import xml.etree.ElementTree as ET
import unittest


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = (
    ROOT
    / "fitness-v2"
    / "android"
    / "app"
    / "src"
    / "main"
    / "AndroidManifest.xml"
)
ANDROID_NAME = "{http://schemas.android.com/apk/res/android}name"

# This is the current reviewed canonical scope, not a blanket approval for future
# Health data types. Expand it only with matching declaration/privacy and device
# evidence for the exact candidate.
CANONICAL_HEALTH_PERMISSIONS = {
    "android.permission.health.READ_STEPS",
    "android.permission.health.READ_EXERCISE",
    "android.permission.health.WRITE_EXERCISE",
    "android.permission.health.READ_DISTANCE",
    "android.permission.health.READ_ACTIVE_CALORIES_BURNED",
}

DEFERRED_HEALTH_PERMISSIONS = {
    "android.permission.health.READ_TOTAL_CALORIES_BURNED",
    "android.permission.health.READ_SLEEP",
    "android.permission.health.READ_HEART_RATE",
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


class HealthPermissionScopeGateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = ET.parse(MANIFEST_PATH).getroot()
        cls.permissions = {
            node.get(ANDROID_NAME)
            for node in root.findall("uses-permission")
            if (node.get(ANDROID_NAME) or "").startswith(
                "android.permission.health."
            )
        }

    def test_canonical_health_surface_matches_the_reviewed_allowlist(self):
        self.assertEqual(CANONICAL_HEALTH_PERMISSIONS, self.permissions)

    def test_existing_exercise_permission_covers_session_import_scope(self):
        self.assertIn("android.permission.health.READ_EXERCISE", self.permissions)
        self.assertFalse(any("SWIMMING" in item for item in self.permissions))

    def test_heart_rate_permission_stays_deferred_until_its_own_gate_passes(self):
        self.assertNotIn(
            "android.permission.health.READ_HEART_RATE", self.permissions
        )

    def test_broad_wellness_and_clinical_expansion_stays_out_of_canonical(self):
        self.assertTrue(DEFERRED_HEALTH_PERMISSIONS.isdisjoint(self.permissions))


if __name__ == "__main__":
    unittest.main()
