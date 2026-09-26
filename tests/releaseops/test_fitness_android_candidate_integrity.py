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


def make_artifact(root: Path, *, with_stage16a: bool, with_signature: bool = True) -> tuple[Path, str, str]:
    aab = root / "candidate.aab"
    with zipfile.ZipFile(aab, "w", zipfile.ZIP_DEFLATED) as bundle:
        bundle.writestr("base/manifest/AndroidManifest.xml", b"manifest")
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


if __name__ == "__main__":
    unittest.main()
