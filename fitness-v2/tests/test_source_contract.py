import json
from pathlib import Path
import re
import unittest
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
ANDROID = ROOT / "fitness-v2" / "android"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


class FitnessV2SourceContractTest(unittest.TestCase):
    def test_android_identity_api_level_and_noncolliding_version(self):
        gradle = (ANDROID / "app" / "build.gradle").read_text()
        self.assertIn("applicationId 'com.topherofit.thf.pulse'", gradle)
        self.assertIn("compileSdk 36", gradle)
        self.assertIn("targetSdk 36", gradle)
        version = int(re.search(r"versionCode\s+(\d+)", gradle).group(1))
        self.assertGreaterEqual(version, 51002)

    def test_health_permissions_are_exactly_the_data_used(self):
        manifest = ET.parse(ANDROID / "app" / "src" / "main" / "AndroidManifest.xml")
        health = {
            node.attrib[ANDROID_NS + "name"]
            for node in manifest.getroot().findall("uses-permission")
            if node.attrib[ANDROID_NS + "name"].startswith("android.permission.health.")
        }
        self.assertEqual(
            {
                "android.permission.health.READ_STEPS",
                "android.permission.health.READ_EXERCISE",
                "android.permission.health.WRITE_EXERCISE",
                "android.permission.health.READ_DISTANCE",
                "android.permission.health.READ_ACTIVE_CALORIES_BURNED",
            },
            health,
        )

    def test_health_flow_is_user_visible_and_fail_closed(self):
        html = (ANDROID / "app" / "src" / "main" / "assets" / "pulse" / "index.html").read_text()
        for marker in (
            'id="healthScreen"', 'id="healthConnectBtn"', 'id="healthSyncBtn"',
            'id="healthLastSync"', 'id="healthError"', "Samsung Health",
            "معرّف ثابت", "لا نطلب نبض القلب",
        ):
            self.assertIn(marker, html)
        self.assertNotIn("Stage16A", html)

    def test_native_health_uses_stable_ids_provenance_and_revoke_checks(self):
        source = "\n".join(
            p.read_text()
            for p in (ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse").glob("*.kt")
        )
        for marker in (
            "clientRecordId", "clientRecordVersion", "dataOrigin.packageName",
            "getGrantedPermissions", "onResume", "ActiveCaloriesBurnedRecord",
            "EXERCISE_TYPE_SOCCER", "EXERCISE_TYPE_SWIMMING_OPEN_WATER",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("HeartRateRecord", source)

    def test_backend_contract_is_authenticated_and_idempotent(self):
        contract = json.loads((ROOT / "fitness-v2" / "backend" / "openapi.json").read_text())
        self.assertEqual([{"BearerAuth": []}], contract["security"])
        sync = contract["paths"]["/v2/workouts:sync"]["post"]
        self.assertTrue(any(item["name"] == "Idempotency-Key" and item["required"] for item in sync["parameters"]))
        required = set(contract["components"]["schemas"]["WorkoutSession"]["required"])
        self.assertTrue({"clientRecordId", "clientRecordVersion", "source", "sets"} <= required)
        backend_source = (ROOT / "fitness-v2" / "backend" / "api.py").read_text()
        auth_source = (ROOT / "fitness-v2" / "backend" / "auth.py").read_text()
        for marker in (
            "require_https", "HTTP_IDEMPOTENCY_KEY", "revoked_sessions",
            "HmacAccessTokenVerifier", "THF_AUTH_KEYS_JSON",
        ):
            self.assertIn(marker, backend_source + auth_source)
        self.assertNotIn('keys={"development"', backend_source + auth_source)

    def test_android_local_state_recovers_from_corrupt_preferences(self):
        source = (ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse" / "MainActivity.kt").read_text()
        self.assertIn("private fun jsonArrayPreference", source)
        self.assertIn("prefs.edit { remove(key) }", source)
        self.assertNotIn('JSONArray(prefs.getString(PENDING_HEALTH', source)
        self.assertNotIn('JSONArray(prefs.getString(SUMMARIES', source)

    def test_android_backend_sync_is_https_queued_and_session_scoped(self):
        source = "\n".join(
            p.read_text()
            for p in (ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse").glob("*.kt")
        )
        for marker in (
            "HttpsURLConnection", "Idempotency-Key", '"THF_ANDROID"',
            '"com.topherofit.thf.pulse"', "pending_backend_workouts",
            "setBackendAccessToken", "backendAccessToken = null",
        ):
            self.assertIn(marker, source)
        self.assertIn("blockNetworkLoads = true", source)
        self.assertNotIn("putString(\"backend_access_token\"", source)

    def test_android_backup_rotation_and_health_rationale_are_release_safe(self):
        manifest_path = ANDROID / "app" / "src" / "main" / "AndroidManifest.xml"
        manifest = ET.parse(manifest_path)
        application = manifest.getroot().find("application")
        self.assertEqual("false", application.attrib[ANDROID_NS + "allowBackup"])
        self.assertEqual("@xml/backup_rules", application.attrib[ANDROID_NS + "fullBackupContent"])
        self.assertEqual("@xml/data_extraction_rules", application.attrib[ANDROID_NS + "dataExtractionRules"])
        main_activity = next(
            node
            for node in application.findall("activity")
            if node.attrib[ANDROID_NS + "name"] == ".MainActivity"
        )
        self.assertNotIn(ANDROID_NS + "screenOrientation", main_activity.attrib)

        for path in (
            ANDROID / "app" / "src" / "main" / "res" / "xml" / "backup_rules.xml",
            ANDROID / "app" / "src" / "main" / "res" / "xml" / "data_extraction_rules.xml",
            ANDROID / "app" / "src" / "main" / "res" / "values" / "strings.xml",
            ANDROID / "app" / "src" / "main" / "res" / "values-ar" / "strings.xml",
        ):
            ET.parse(path)

        rationale = (
            ANDROID
            / "app"
            / "src"
            / "main"
            / "java"
            / "com"
            / "topherofit"
            / "thf"
            / "pulse"
            / "HealthPermissionsRationaleActivity.kt"
        ).read_text()
        self.assertIn("R.string.health_permissions_rationale", rationale)


if __name__ == "__main__":
    unittest.main()
