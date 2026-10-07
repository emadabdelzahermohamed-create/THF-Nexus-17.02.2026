import json
import importlib.util
from pathlib import Path
import re
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[2]
ANDROID = ROOT / "fitness-v2" / "android"
APPDEPLOY_PUBLIC = ROOT / "fitness-v2" / "appdeploy" / "public"
ANDROID_NS = "{http://schemas.android.com/apk/res/android}"


class FitnessV2SourceContractTest(unittest.TestCase):
    def test_android_gate_runs_for_release_pull_requests(self):
        workflow = (ROOT / ".github" / "workflows" / "fitness-v2-android-health.yml").read_text()
        trigger_block = workflow.split("permissions:", 1)[0]
        self.assertIn("pull_request:", trigger_block)
        self.assertGreaterEqual(
            trigger_block.count("branches: [release/fitness-v2-rebuild-20261002]"),
            2,
        )
        self.assertGreaterEqual(trigger_block.count("- 'fitness-v2/**'"), 2)

    def test_android_package_gate_derives_offline_payload_from_catalog(self):
        workflow = (ROOT / ".github" / "workflows" / "fitness-v2-android-health.yml").read_text()
        verifier_path = ROOT / "fitness-v2" / "scripts" / "verify_offline_payload.py"
        verifier_source = verifier_path.read_text()
        self.assertIn("verify_offline_payload.py", workflow)
        self.assertNotIn("-eq 160", workflow)
        for marker in (
            "catalog_matches_source",
            "missing_assets",
            "unexpected_assets",
            "stage16a",
        ):
            self.assertIn(marker, verifier_source)

        spec = importlib.util.spec_from_file_location("verify_offline_payload", verifier_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        catalog_path = ANDROID / "app" / "src" / "main" / "assets" / "pulse" / "data" / "exercises.js"
        catalog_bytes = catalog_path.read_bytes()
        expected = module.referenced_demo_assets(module.load_catalog(catalog_bytes))
        with tempfile.TemporaryDirectory() as temporary:
            apk_path = Path(temporary) / "candidate.apk"
            with zipfile.ZipFile(apk_path, "w") as apk:
                apk.writestr(module.CATALOG_ENTRY, catalog_bytes)
                for asset in expected:
                    apk.writestr(module.APK_MEDIA_PREFIX + asset, b"fixture")
            report = module.verify(apk_path, catalog_path)
        self.assertEqual(len(expected), report["packaged_demo_assets"])
        self.assertEqual(len(module.load_catalog(catalog_bytes)), report["exercise_count"])

    def test_android_identity_api_level_and_noncolliding_version(self):
        gradle = (ANDROID / "app" / "build.gradle").read_text()
        self.assertIn("applicationId 'com.topherofit.thf.pulse'", gradle)
        self.assertIn("compileSdk 36", gradle)
        self.assertIn("targetSdk 36", gradle)
        version = int(re.search(r"versionCode\s+(\d+)", gradle).group(1))
        self.assertGreaterEqual(version, 51003)

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
        sync = contract["paths"]["/api/v2/workouts/sync"]["post"]
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
        gradle = (ANDROID / "app" / "build.gradle").read_text()
        source = "\n".join(
            p.read_text()
            for p in (ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse").glob("*.kt")
        )
        for marker in (
            "HttpsURLConnection", "Idempotency-Key", '"THF_ANDROID"',
            '"com.topherofit.thf.pulse"', "pending_backend_workouts",
            "requestBackendSignIn", "backendAccessToken = null",
            "AccountAuthRepository", "AccountAuthContract",
        ):
            self.assertIn(marker, source)
        self.assertIn("blockNetworkLoads = true", source)
        self.assertNotIn("putString(\"backend_access_token\"", source)
        self.assertNotIn("setBackendAccessToken", source)
        self.assertIn(
            "https://api-v2.appdeploy.ai/app/thf-fitness-pulse-ul26f1/",
            gradle,
        )
        self.assertNotRegex(
            gradle,
            r"def baseUrl\s*=.*https://thf-fitness-pulse-ul26f1\.v2\.appdeploy\.ai",
        )

    def test_android_account_handoff_uses_external_browser_pkce_and_exact_callback(self):
        manifest = ET.parse(ANDROID / "app" / "src" / "main" / "AndroidManifest.xml")
        application = manifest.getroot().find("application")
        main_activity = next(
            node for node in application.findall("activity")
            if node.attrib[ANDROID_NS + "name"] == ".MainActivity"
        )
        self.assertEqual("singleTask", main_activity.attrib[ANDROID_NS + "launchMode"])
        manifest_text = (ANDROID / "app" / "src" / "main" / "AndroidManifest.xml").read_text()
        for marker in (
            'android:scheme="topherofit"', 'android:host="auth"', 'android:pathPrefix="/v2/complete"',
            'android:autoVerify="true"', 'android:host="thf-fitness-pulse-ul26f1.v2.appdeploy.ai"',
            'android:pathPrefix="/android/auth/v2/complete"',
        ):
            self.assertIn(marker, manifest_text)

        source = "\n".join(
            p.read_text()
            for p in (ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse").glob("*.kt")
        )
        for marker in (
            "Intent.ACTION_VIEW", "CATEGORY_BROWSABLE", "code_challenge_method=S256",
            "MessageDigest.getInstance(\"SHA-256\")", "FLOW_TTL_MILLIS",
            "/api/v2/auth/android/sessions", "remove(AUTH_PKCE_VERIFIER)",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("addJavascriptInterface", (ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse" / "AccountAuthRepository.kt").read_text())

    def test_appdeploy_account_bridge_is_pkce_bound_user_scoped_and_hash_only(self):
        routes = (ROOT / "fitness-v2" / "appdeploy" / "android_v2_routes.ts").read_text()
        bridge = (ROOT / "fitness-v2" / "appdeploy" / "native_auth_bridge.tsx").read_text()
        for marker in (
            "requireAuth()", "context.user!.userId", "codeChallenge",
            "timingSafeEqual", "tokenHash", "ticketHash", "SESSION_TTL_MS",
            "fitnessV2AndroidRoutes", "androidUser(context.event)",
        ):
            self.assertIn(marker, routes)
        for marker in (
            "auth.signIn", "api.post('/api/v2/auth/android/tickets'",
            "topherofit://auth/v2/complete", "code_challenge_method",
            "Continue to sign in", "AndroidAuthBridgeScreen",
        ):
            self.assertIn(marker, bridge)
        self.assertNotIn("accessToken:", routes)
        self.assertNotIn("refreshToken", routes + bridge)

    def test_appdeploy_v2_account_deletion_covers_dynamic_and_legacy_data(self):
        routes = (ROOT / "fitness-v2" / "appdeploy" / "android_v2_routes.ts").read_text()
        readme = (ROOT / "fitness-v2" / "appdeploy" / "README.md").read_text()
        workflow = (ROOT / ".github" / "workflows" / "fitness-v2-android-health.yml").read_text()
        typecheck = (ROOT / "fitness-v2" / "appdeploy" / "tsconfig.routes.json").read_text()
        for marker in (
            "export async function deleteFitnessV2UserData",
            "resourceTable(userId)",
            "deleteWorkoutHistory(userId)",
            "deleteTrackedResources(userId)",
            "deleteLegacySharedData(userId)",
            "LEGACY_TICKET_TABLE",
            "LEGACY_SESSION_TABLE",
            "LEGACY_COMPETITION_TABLE",
            "fitness_v2_deletion_",
            "nextToken",
        ):
            self.assertIn(marker, routes)
        self.assertIn("DELETE /api/account", readme)
        self.assertIn("deleteFitnessV2UserData", readme)
        self.assertIn("Typecheck AppDeploy V2 route overlay", workflow)
        self.assertIn("typescript@5.9.3", workflow)
        self.assertIn("android_v2_routes.ts", typecheck)
        self.assertNotIn("const competitionTable = 'fitness_v2_competition_submissions'", routes)

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

    def test_android_exposes_privacy_and_account_deletion_paths(self):
        html = (ANDROID / "app" / "src" / "main" / "assets" / "pulse" / "index.html").read_text()
        script = (ANDROID / "app" / "src" / "main" / "assets" / "pulse" / "app.js").read_text()
        activity = (
            ANDROID / "app" / "src" / "main" / "java" / "com" / "topherofit" / "thf" / "pulse" / "MainActivity.kt"
        ).read_text()
        for marker in ('id="privacyPolicyBtn"', 'id="accountDeletionBtn"'):
            self.assertIn(marker, html)
        for marker in ("openPrivacyPolicy", "openAccountDeletion", "privacy.html", "account-deletion.html"):
            self.assertIn(marker, script + activity)
        self.assertIn("Intent.CATEGORY_BROWSABLE", activity)
        self.assertIn("AccountAuthContract.persistentHttpsBase", activity)

        privacy = (APPDEPLOY_PUBLIC / "privacy.html").read_text()
        deletion = (APPDEPLOY_PUBLIC / "account-deletion.html").read_text()
        for marker in (
            "Health Connect summary values",
            "does not sell personal data",
            "does not include an advertising SDK",
            "external identity-provider account",
        ):
            self.assertIn(marker, privacy)
        for marker in (
            "Delete THF Fitness account data",
            "V2 workout history",
            "synchronization/idempotency records",
            "does not delete your Google, Apple, X, email-provider, or shared AppDeploy identity",
        ):
            self.assertIn(marker, deletion)

    def test_android_founding_hero_offer_is_play_billing_only_and_fail_closed(self):
        gradle = (ANDROID / "app" / "build.gradle").read_text()
        html = (ANDROID / "app" / "src" / "main" / "assets" / "pulse" / "index.html").read_text()
        script = (ANDROID / "app" / "src" / "main" / "assets" / "pulse" / "app.js").read_text()
        billing = (
            ANDROID
            / "app"
            / "src"
            / "main"
            / "java"
            / "com"
            / "topherofit"
            / "thf"
            / "pulse"
            / "FoundingHeroBilling.kt"
        ).read_text()

        self.assertIn("com.android.billingclient:billing-ktx:9.1.0", gradle)
        for marker in (
            'id="foundingHeroCard"',
            'id="foundingHeroPurchaseBtn"',
            'id="foundingHeroRestoreBtn"',
            "شارة تجميلية فقط",
            "Cosmetic badge only",
        ):
            self.assertIn(marker, html + script)
        for marker in (
            "thf_founding_hero_lifetime",
            "enableAutoServiceReconnection",
            "enableOneTimeProducts",
            "queryProductDetailsAsync",
            "queryPurchasesAsync",
            "acknowledgePurchase",
            "PurchaseState.PENDING",
            "signatureVerified",
        ):
            self.assertIn(marker, billing)
        self.assertNotRegex(
            html + script + billing,
            r"(?i)(token reward|investment return|guaranteed profit|pay.?to.?win)",
        )


if __name__ == "__main__":
    unittest.main()
