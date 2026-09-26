#!/usr/bin/env python3
"""Fail-closed integrity audit for the exact Top Hero Fit Android candidate.

This validator intentionally does not build, sign, upload, or mutate a Play edit.
It binds the audit to a GitHub Actions artifact digest and checks whether the
contained production AAB carries the first-install Stage16A payload required by
the Fitness standalone release contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path


STAGE16A_PATTERN = re.compile(r"stage16a.*\.glb$", re.IGNORECASE)
LEGACY_AVATAR_PATTERN = re.compile(
    r"(?:thf_humanoid_v[1-6]|stage15j_ual1_animated)\.glb$", re.IGNORECASE
)
SIGNATURE_PATTERN = re.compile(r"^META-INF/[^/]+\.(?:RSA|DSA|EC)$", re.IGNORECASE)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _select_single_aab(artifact: zipfile.ZipFile) -> str:
    candidates = sorted(name for name in artifact.namelist() if name.lower().endswith(".aab"))
    if len(candidates) != 1:
        raise ValueError(f"expected exactly one AAB in artifact, found {len(candidates)}")
    return candidates[0]


def audit_candidate(
    artifact_zip: Path,
    expected_artifact_sha256: str,
    expected_aab_sha256: str,
    metadata: dict[str, object],
) -> dict[str, object]:
    artifact_sha256 = sha256_file(artifact_zip)
    issues: list[str] = []
    if artifact_sha256 != expected_artifact_sha256:
        issues.append("ARTIFACT_SHA256_MISMATCH")

    with zipfile.ZipFile(artifact_zip) as artifact:
        aab_name = _select_single_aab(artifact)
        aab_bytes = artifact.read(aab_name)

    aab_sha256 = hashlib.sha256(aab_bytes).hexdigest()
    if aab_sha256 != expected_aab_sha256:
        issues.append("AAB_SHA256_MISMATCH")

    from io import BytesIO

    with zipfile.ZipFile(BytesIO(aab_bytes)) as aab:
        infos = [entry for entry in aab.infolist() if not entry.is_dir()]
        members = sorted(entry.filename for entry in infos)
        uncompressed_bytes = sum(entry.file_size for entry in infos)

    stage16a_members = [name for name in members if STAGE16A_PATTERN.search(name)]
    legacy_avatar_members = [name for name in members if LEGACY_AVATAR_PATTERN.search(name)]
    signature_members = [name for name in members if SIGNATURE_PATTERN.search(name)]
    asset_members = [name for name in members if name.startswith("base/assets/")]
    native_lib_members = [name for name in members if name.startswith("base/lib/")]
    arm64_members = [name for name in native_lib_members if "/arm64-v8a/" in name]

    if not signature_members:
        issues.append("AAB_SIGNATURE_BLOCK_MISSING")
    if not stage16a_members:
        issues.append("FIRST_INSTALL_STAGE16A_ASSET_MISSING")
    if legacy_avatar_members:
        issues.append("LEGACY_AVATAR_ASSET_PRESENT")
    if asset_members == ["base/assets/offline.html"]:
        issues.append("OFFLINE_PAYLOAD_IS_FALLBACK_HTML_ONLY")

    result = "PASS" if not issues else "BLOCKED"
    return {
        "schema": "thf-fitness-android-candidate-integrity-v1",
        "lane": "android",
        "scope": "release_integrity_only",
        "result": result,
        "final": False,
        "phone_pass": False,
        "play_ready": False,
        "artifact": {
            "github_run_id": metadata["github_run_id"],
            "github_job_id": metadata["github_job_id"],
            "artifact_id": metadata["artifact_id"],
            "artifact_name": metadata["artifact_name"],
            "artifact_sha256": artifact_sha256,
            "artifact_sha256_expected": expected_artifact_sha256,
            "source_commit_sha": metadata["source_commit_sha"],
        },
        "android": {
            "package": metadata["package"],
            "track": metadata["track"],
            "version_code": metadata["version_code"],
            "aab_name": aab_name,
            "aab_sha256": aab_sha256,
            "aab_sha256_expected": expected_aab_sha256,
            "aab_compressed_bytes": len(aab_bytes),
            "aab_uncompressed_bytes": uncompressed_bytes,
            "file_count": len(members),
            "asset_count": len(asset_members),
            "stage16a_members": stage16a_members,
            "legacy_avatar_members": legacy_avatar_members,
            "signature_members": signature_members,
            "native_lib_count": len(native_lib_members),
            "arm64_native_lib_count": len(arm64_members),
        },
        "issues": sorted(issues),
        "recorded_at": metadata["recorded_at"],
        "next_action": (
            "Keep versionCode 50001 on Internal only. Motion lane must provide the canonical "
            "Stage16A first-install asset; Android lane must package it into a newly signed "
            "successor with versionCode >50001, rerun this integrity gate, then perform exact-"
            "candidate physical install/runtime QA before promotion."
        ),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-zip", type=Path, required=True)
    parser.add_argument("--artifact-sha256", required=True)
    parser.add_argument("--aab-sha256", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--expect", choices=("PASS", "BLOCKED"), required=True)
    parser.add_argument("--github-run-id", type=int, required=True)
    parser.add_argument("--github-job-id", type=int, required=True)
    parser.add_argument("--artifact-id", type=int, required=True)
    parser.add_argument("--source-commit-sha", required=True)
    parser.add_argument("--package", default="com.topherofit.thf.pulse")
    parser.add_argument("--track", default="internal")
    parser.add_argument("--version-code", type=int, default=50001)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    metadata = {
        "github_run_id": args.github_run_id,
        "github_job_id": args.github_job_id,
        "artifact_id": args.artifact_id,
        "artifact_name": "thf-fitness-v5-rc2-signed-release",
        "source_commit_sha": args.source_commit_sha,
        "package": args.package,
        "track": args.track,
        "version_code": args.version_code,
        "recorded_at": args.recorded_at,
    }
    try:
        report = audit_candidate(
            args.artifact_zip,
            args.artifact_sha256.lower(),
            args.aab_sha256.lower(),
            metadata,
        )
    except (OSError, ValueError, zipfile.BadZipFile) as exc:
        report = {
            "schema": "thf-fitness-android-candidate-integrity-v1",
            "lane": "android",
            "scope": "release_integrity_only",
            "result": "BLOCKED",
            "final": False,
            "phone_pass": False,
            "play_ready": False,
            "issues": [f"AUDIT_ERROR:{type(exc).__name__}:{exc}"],
            "recorded_at": args.recorded_at,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == args.expect else 2


if __name__ == "__main__":
    sys.exit(main())
