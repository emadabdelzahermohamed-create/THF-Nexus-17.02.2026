import hashlib
import tempfile
import unittest
import zipfile
from pathlib import Path

from ReleaseOps.FitnessStandalone.android_candidate_integrity import audit_candidate


META = {
    "github_run_id": 1,
    "github_job_id": 2,
    "artifact_id": 3,
    "artifact_name": "candidate",
    "source_commit_sha": "a" * 40,
    "package": "com.topherofit.thf.pulse",
    "track": "internal",
    "version_code": 50002,
    "recorded_at": "2026-09-26T17:30:00Z",
}


def varint(value: int) -> bytes:
    encoded = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        encoded.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(encoded)


def proto_bytes(field_number: int, value: bytes) -> bytes:
    return varint((field_number << 3) | 2) + varint(len(value)) + value


def xml_attribute(name: str, value: str, namespace: str = "") -> bytes:
    payload = b""
    if namespace:
        payload += proto_bytes(1, namespace.encode())
    payload += proto_bytes(2, name.encode())
    payload += proto_bytes(3, value.encode())
    return payload


def xml_element(name: str, attributes=(), children=()) -> bytes:
    payload = proto_bytes(3, name.encode())
    for key, value in attributes:
        payload += proto_bytes(4, xml_attribute(key, value))
    for child in children:
        payload += proto_bytes(5, proto_bytes(1, child))
    return payload


def manifest_proto(*, release_contracts: bool = True) -> bytes:
    permissions = [
        xml_element("uses-permission", (("name", "android.permission.INTERNET"),)),
        xml_element(
            "uses-permission", (("name", "android.permission.ACCESS_NETWORK_STATE"),)
        ),
    ]
    if release_contracts:
        permissions.append(
            xml_element(
                "uses-permission", (("name", "android.permission.health.READ_STEPS"),)
            )
        )
    launcher = xml_element(
        "intent-filter",
        (("autoVerify", "true"),) if release_contracts else (),
        (
            xml_element(
                "category", (("name", "android.intent.category.BROWSABLE"),)
            ),
            xml_element(
                "data",
                (
                    ("scheme", "https" if release_contracts else "topherofit"),
                    ("host", "topherofit.com"),
                ),
            ),
        ),
    )
    activity = xml_element(
        "activity",
        (("name", "com.topherofit.thf.pulse.MainActivity"), ("exported", "true")),
        (launcher,),
    )
    app_attributes = [
        ("allowBackup", "false"),
        ("supportsRtl", "true"),
        ("usesCleartextTraffic", "false"),
    ]
    if not release_contracts:
        app_attributes.append(("debuggable", "true"))
    application = xml_element("application", app_attributes, (activity,))
    manifest = xml_element(
        "manifest",
        (
            ("package", "com.topherofit.thf.pulse"),
            ("versionCode", "50002"),
            ("versionName", "5.0.1"),
            ("compileSdkVersion", "36"),
        ),
        (
            xml_element(
                "uses-sdk", (("minSdkVersion", "26"), ("targetSdkVersion", "36"))
            ),
            *permissions,
            application,
        ),
    )
    return proto_bytes(1, manifest)


def make_artifact(
    root: Path,
    *,
    with_stage16a: bool,
    with_signature: bool = True,
    release_contracts: bool = True,
) -> tuple[Path, str, str]:
    aab = root / "candidate.aab"
    with zipfile.ZipFile(aab, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr(
            "base/manifest/AndroidManifest.xml",
            manifest_proto(release_contracts=release_contracts),
        )
        bundle.writestr("base/dex/classes.dex", b"dex")
        bundle.writestr("base/assets/offline.html", b"offline")
        if with_stage16a:
            bundle.writestr(
                "base/assets/avatar/thf_mpfb_stage16a_ual12_animated.glb", b"glTF-stage16a"
            )
        if with_signature:
            bundle.writestr("META-INF/THF.SF", b"sf")
            bundle.writestr("META-INF/THF.RSA", b"rsa")
    aab_bytes = aab.read_bytes()
    artifact = root / "artifact.zip"
    with zipfile.ZipFile(artifact, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("candidate.aab", aab_bytes)
    return (
        artifact,
        hashlib.sha256(artifact.read_bytes()).hexdigest(),
        hashlib.sha256(aab_bytes).hexdigest(),
    )


class FitnessAndroidCandidateIntegrityTests(unittest.TestCase):
    def test_passes_signed_candidate_with_first_install_stage16a(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact, artifact_sha, aab_sha = make_artifact(Path(tmp), with_stage16a=True)
            report = audit_candidate(artifact, artifact_sha, aab_sha, META)
        self.assertEqual(report["result"], "PASS")
        self.assertEqual(report["issues"], [])
        self.assertFalse(report["play_ready"])

    def test_blocks_html_only_wrapper_even_when_signed(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact, artifact_sha, aab_sha = make_artifact(Path(tmp), with_stage16a=False)
            report = audit_candidate(artifact, artifact_sha, aab_sha, META)
        self.assertEqual(report["result"], "BLOCKED")
        self.assertIn("FIRST_INSTALL_STAGE16A_ASSET_MISSING", report["issues"])
        self.assertIn("OFFLINE_PAYLOAD_IS_FALLBACK_HTML_ONLY", report["issues"])

    def test_blocks_digest_drift_and_unsigned_bundle(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact, _, aab_sha = make_artifact(
                Path(tmp), with_stage16a=True, with_signature=False
            )
            report = audit_candidate(artifact, "0" * 64, aab_sha, META)
        self.assertEqual(report["result"], "BLOCKED")
        self.assertIn("ARTIFACT_SHA256_MISMATCH", report["issues"])
        self.assertIn("AAB_SIGNATURE_BLOCK_MISSING", report["issues"])

    def test_blocks_missing_dal_health_permissions_and_debuggable_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            artifact, artifact_sha, aab_sha = make_artifact(
                Path(tmp), with_stage16a=True, release_contracts=False
            )
            report = audit_candidate(artifact, artifact_sha, aab_sha, META)
        self.assertEqual(report["result"], "BLOCKED")
        self.assertIn("DIGITAL_ASSET_LINKS_INTENT_FILTER_MISSING", report["issues"])
        self.assertIn("HEALTH_CONNECT_PERMISSIONS_MISSING", report["issues"])
        self.assertIn("RELEASE_MARKED_DEBUGGABLE", report["issues"])


if __name__ == "__main__":
    unittest.main()
