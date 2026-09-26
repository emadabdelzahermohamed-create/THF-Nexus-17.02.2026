import tempfile
import unittest
from pathlib import Path

from ReleaseOps.FitnessStandalone.android_source_packaging_contract import (
    STAGE16A_NAME,
    audit_source,
    sha256_file,
)


PACKAGE = "com.topherofit.thf.pulse"
HOST = "thf-fitness-pulse-ul26f1.v2.appdeploy.ai"


def write(path: Path, content: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(content, bytes):
        path.write_bytes(content)
    else:
        path.write_text(content, encoding="utf-8")


def make_source(root: Path, *, complete: bool) -> str:
    avatar = root / "static/assets/avatar" / STAGE16A_NAME
    write(avatar, b"stage16a-canonical")
    write(
        root / "android/app/build.gradle",
        "\n".join(
            [
                "android {",
                "  namespace 'com.topherofit.thf.pulse'",
                "  compileSdk 36",
                "  defaultConfig {",
                "    applicationId 'com.topherofit.thf.pulse'",
                "    targetSdk 36",
                f"    versionCode {50002 if complete else 50001}",
                "  }",
                "}",
                "dependencies { implementation 'androidx.health.connect:connect-client:1.1.0' }" if complete else "",
            ]
        ),
    )
    permission = (
        '<uses-permission android:name="android.permission.health.READ_STEPS"/>'
        if complete
        else ""
    )
    dal = (
        f'''<intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW"/>
        <category android:name="android.intent.category.DEFAULT"/>
        <category android:name="android.intent.category.BROWSABLE"/>
        <data android:scheme="https" android:host="{HOST}"/>
      </intent-filter>'''
        if complete
        else ""
    )
    write(
        root / "android/app/src/main/AndroidManifest.xml",
        f'''<manifest xmlns:android="http://schemas.android.com/apk/res/android">
  {permission}
  <application><activity android:name=".MainActivity">{dal}</activity></application>
</manifest>''',
    )
    main = (
        'class MainActivity { HealthConnectClient client; String offline="file:///android_asset/offline.html"; }'
        if complete
        else "class MainActivity { void showOffline() {} }"
    )
    write(
        root / "android/app/src/main/java/com/topherofit/thf/pulse/MainActivity.java",
        main,
    )
    html = (
        '<canvas id="photoCanvas"></canvas><script type="module" src="offline-runtime.mjs"></script>'
        if complete
        else "<p>The secure service is not available yet.</p>"
    )
    write(root / "android/app/src/main/assets/offline.html", html)
    if complete:
        write(root / "android/app/src/main/assets/offline-runtime.mjs", "// renderer")
        write(root / "android/app/src/main/assets/avatar" / STAGE16A_NAME, b"stage16a-canonical")
    return sha256_file(avatar)


class FitnessAndroidSourcePackagingContractTests(unittest.TestCase):
    def audit(self, root: Path, avatar_sha: str):
        return audit_source(
            root,
            "a" * 64,
            avatar_sha,
            PACKAGE,
            50002,
            HOST,
            "2026-09-27T00:00:00Z",
        )

    def test_complete_successor_source_passes_packaging_contract(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            avatar_sha = make_source(root, complete=True)
            report = self.audit(root, avatar_sha)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["issues"], [])

    def test_current_wrapper_source_blocks_with_exact_reasons(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            avatar_sha = make_source(root, complete=False)
            report = self.audit(root, avatar_sha)
        self.assertEqual(report["result"], "BLOCKED")
        for issue in (
            "SUCCESSOR_VERSION_CODE_NOT_RESERVED",
            "FIRST_INSTALL_STAGE16A_NOT_PACKAGED",
            "OFFLINE_ENTRYPOINT_PLACEHOLDER",
            "OFFLINE_RUNTIME_ASSETS_MISSING",
            "OFFLINE_ENTRYPOINT_NOT_REACHABLE",
            "DAL_HTTPS_AUTOVERIFY_FILTER_MISSING",
            "HEALTH_CONNECT_PERMISSIONS_MISSING",
            "HEALTH_CONNECT_IMPLEMENTATION_MISSING",
        ):
            self.assertIn(issue, report["issues"])
        self.assertTrue(report["checks"]["canonical_stage16a_hash_matches"])

    def test_canonical_avatar_hash_drift_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_source(root, complete=True)
            report = self.audit(root, "0" * 64)
        self.assertIn("CANONICAL_STAGE16A_HASH_MISMATCH", report["issues"])
        self.assertEqual(report["result"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
