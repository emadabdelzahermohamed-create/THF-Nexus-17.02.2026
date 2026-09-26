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
ANDROID_NAMESPACE = "http://schemas.android.com/apk/res/android"


def _read_varint(data: bytes, offset: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while offset < len(data):
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7
        if shift > 63:
            raise ValueError("protobuf varint is too long")
    raise ValueError("truncated protobuf varint")


def _proto_fields(data: bytes):
    """Yield protobuf fields needed by aapt2's XmlNode schema.

    Android App Bundles store their manifest as com.android.aapt.Resources.XmlNode.
    Keeping this tiny wire reader local avoids depending on an unpinned bundletool
    binary while still pairing attribute names with their exact values.
    """

    offset = 0
    while offset < len(data):
        key, offset = _read_varint(data, offset)
        field_number, wire_type = key >> 3, key & 0x07
        if field_number == 0:
            raise ValueError("invalid protobuf field number 0")
        if wire_type == 0:
            value, offset = _read_varint(data, offset)
        elif wire_type == 1:
            if offset + 8 > len(data):
                raise ValueError("truncated fixed64 protobuf field")
            value = data[offset : offset + 8]
            offset += 8
        elif wire_type == 2:
            length, offset = _read_varint(data, offset)
            end = offset + length
            if end > len(data):
                raise ValueError("truncated length-delimited protobuf field")
            value = data[offset:end]
            offset = end
        elif wire_type == 5:
            if offset + 4 > len(data):
                raise ValueError("truncated fixed32 protobuf field")
            value = data[offset : offset + 4]
            offset += 4
        else:
            raise ValueError(f"unsupported protobuf wire type {wire_type}")
        yield field_number, wire_type, value


def _utf8(value: object) -> str:
    if not isinstance(value, bytes):
        raise ValueError("expected length-delimited UTF-8 protobuf field")
    return value.decode("utf-8")


def _parse_xml_attribute(data: bytes) -> dict[str, str]:
    attribute = {"namespace_uri": "", "name": "", "value": ""}
    for field_number, wire_type, value in _proto_fields(data):
        if wire_type != 2:
            continue
        if field_number == 1:
            attribute["namespace_uri"] = _utf8(value)
        elif field_number == 2:
            attribute["name"] = _utf8(value)
        elif field_number == 3:
            attribute["value"] = _utf8(value)
    return attribute


def _parse_xml_node(data: bytes) -> dict[str, object] | None:
    for field_number, wire_type, value in _proto_fields(data):
        if field_number == 1 and wire_type == 2 and isinstance(value, bytes):
            return _parse_xml_element(value)
    return None


def _parse_xml_element(data: bytes) -> dict[str, object]:
    element: dict[str, object] = {
        "namespace_uri": "",
        "name": "",
        "attributes": [],
        "children": [],
    }
    for field_number, wire_type, value in _proto_fields(data):
        if wire_type != 2 or not isinstance(value, bytes):
            continue
        if field_number == 2:
            element["namespace_uri"] = _utf8(value)
        elif field_number == 3:
            element["name"] = _utf8(value)
        elif field_number == 4:
            element["attributes"].append(_parse_xml_attribute(value))
        elif field_number == 5:
            child = _parse_xml_node(value)
            if child is not None:
                element["children"].append(child)
    return element


def _attributes(element: dict[str, object]) -> dict[str, str]:
    return {
        str(attribute["name"]): str(attribute["value"])
        for attribute in element["attributes"]
        if attribute["name"]
    }


def _children(element: dict[str, object], name: str) -> list[dict[str, object]]:
    return [child for child in element["children"] if child["name"] == name]


def _manifest_audit(
    manifest_bytes: bytes, expected_package: str, expected_version_code: int
) -> tuple[dict[str, object], list[str]]:
    root = _parse_xml_node(manifest_bytes)
    if root is None or root["name"] != "manifest":
        raise ValueError("AAB manifest is not an aapt2 XmlNode manifest")

    root_attributes = _attributes(root)
    uses_sdk = next(iter(_children(root, "uses-sdk")), None)
    application = next(iter(_children(root, "application")), None)
    if uses_sdk is None or application is None:
        raise ValueError("AAB manifest is missing uses-sdk or application")
    sdk_attributes = _attributes(uses_sdk)
    application_attributes = _attributes(application)

    permissions = sorted(
        {
            _attributes(permission).get("name", "")
            for permission in _children(root, "uses-permission")
            if _attributes(permission).get("name")
        }
    )
    health_permissions = [
        permission
        for permission in permissions
        if permission.startswith("android.permission.health.")
    ]

    activities = _children(application, "activity") + _children(
        application, "activity-alias"
    )
    main_activity_exported = any(
        _attributes(activity).get("name", "").endswith(".MainActivity")
        and _attributes(activity).get("exported") == "true"
        for activity in activities
    )
    dal_hosts: set[str] = set()
    for activity in activities:
        for intent_filter in _children(activity, "intent-filter"):
            intent_attributes = _attributes(intent_filter)
            categories = {
                _attributes(category).get("name")
                for category in _children(intent_filter, "category")
            }
            for data in _children(intent_filter, "data"):
                data_attributes = _attributes(data)
                if (
                    intent_attributes.get("autoVerify") == "true"
                    and data_attributes.get("scheme") == "https"
                    and data_attributes.get("host")
                    and "android.intent.category.BROWSABLE" in categories
                ):
                    dal_hosts.add(data_attributes["host"])

    checks = {
        "package_matches": root_attributes.get("package") == expected_package,
        "version_code_matches": root_attributes.get("versionCode")
        == str(expected_version_code),
        "compile_sdk_36": root_attributes.get("compileSdkVersion") == "36",
        "target_sdk_36": sdk_attributes.get("targetSdkVersion") == "36",
        "release_not_debuggable": application_attributes.get("debuggable") != "true",
        "cleartext_disabled": application_attributes.get("usesCleartextTraffic") == "false",
        "rtl_enabled": application_attributes.get("supportsRtl") == "true",
        "backup_disabled": application_attributes.get("allowBackup") == "false",
        "main_activity_exported": main_activity_exported,
        "digital_asset_links_filter_present": bool(dal_hosts),
        "health_connect_permissions_present": bool(health_permissions),
    }
    issue_by_check = {
        "package_matches": "PACKAGE_ID_MISMATCH",
        "version_code_matches": "VERSION_CODE_MISMATCH",
        "compile_sdk_36": "COMPILE_SDK_NOT_36",
        "target_sdk_36": "TARGET_SDK_NOT_36",
        "release_not_debuggable": "RELEASE_MARKED_DEBUGGABLE",
        "cleartext_disabled": "CLEARTEXT_NOT_DISABLED",
        "rtl_enabled": "RTL_SUPPORT_NOT_ENABLED",
        "backup_disabled": "BACKUP_NOT_DISABLED",
        "main_activity_exported": "MAIN_ACTIVITY_EXPORT_CONTRACT_INVALID",
        "digital_asset_links_filter_present": "DIGITAL_ASSET_LINKS_INTENT_FILTER_MISSING",
        "health_connect_permissions_present": "HEALTH_CONNECT_PERMISSIONS_MISSING",
    }
    details = {
        "package": root_attributes.get("package"),
        "version_code": root_attributes.get("versionCode"),
        "version_name": root_attributes.get("versionName"),
        "compile_sdk": root_attributes.get("compileSdkVersion"),
        "min_sdk": sdk_attributes.get("minSdkVersion"),
        "target_sdk": sdk_attributes.get("targetSdkVersion"),
        "permissions": permissions,
        "health_connect_permissions": health_permissions,
        "digital_asset_links_hosts": sorted(dal_hosts),
        "application_attributes": {
            key: application_attributes.get(key)
            for key in (
                "allowBackup",
                "debuggable",
                "supportsRtl",
                "usesCleartextTraffic",
            )
        },
        "checks": checks,
    }
    return details, [issue_by_check[name] for name, passed in checks.items() if not passed]


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
        manifest_bytes = aab.read("base/manifest/AndroidManifest.xml")

    try:
        manifest, manifest_issues = _manifest_audit(
            manifest_bytes, str(metadata["package"]), int(metadata["version_code"])
        )
        issues.extend(manifest_issues)
    except (UnicodeDecodeError, ValueError) as exc:
        manifest = {"checks": {}, "parse_error": f"{type(exc).__name__}:{exc}"}
        issues.append("AAB_MANIFEST_PROTO_INVALID")

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
            "manifest": manifest,
        },
        "issues": sorted(issues),
        "recorded_at": metadata["recorded_at"],
        "next_action": (
            "Keep versionCode 50001 on Internal only. Motion lane must provide the canonical "
            "Stage16A first-install asset; Android lane must package it into a newly signed "
            "successor with versionCode >50001, add a verified HTTPS autoVerify Digital Asset "
            "Links intent filter and the minimum declared Health Connect permissions, rerun this "
            "integrity gate, then perform exact-candidate physical install/runtime QA before "
            "promotion."
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
