#!/usr/bin/env python3
"""Fail-closed Android packaging audit for the immutable Fitness source ZIP.

The audit proves what exists in the canonical source without rewriting Product
or Motion files. It intentionally emits only paths, hashes, and aggregate
checks; source bodies are not copied into the evidence artifact.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path


ANDROID_NS = "http://schemas.android.com/apk/res/android"
ANDROID_ATTR = f"{{{ANDROID_NS}}}"
STAGE16A_NAME = "thf_mpfb_stage16a_ual12_animated.glb"
LEGACY_AVATAR_RE = re.compile(
    r"(?:thf_humanoid_v[1-6]|stage15j_ual1_animated)\.glb$", re.I
)
PLACEHOLDER_RE = re.compile(
    r"(?:service\s+is\s+not\s+available|not\s+available\s+yet|coming\s+soon|placeholder)",
    re.I,
)
HEALTH_CODE_MARKERS = (
    "HealthConnectClient",
    "androidx.health.connect",
    "HealthPermission",
    "ExerciseSessionRecord",
    "StepsRecord",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _gradle_value(text: str, name: str) -> str | None:
    match = re.search(rf"\b{re.escape(name)}\s*(?:=\s*)?['\"]?([^'\"\s}}]+)", text)
    return match.group(1) if match else None


def _manifest_contract(manifest_path: Path, expected_host: str) -> dict[str, object]:
    if not manifest_path.is_file():
        return {
            "health_permissions": [],
            "dal_hosts": [],
            "dal_filter_present": False,
        }
    root = ET.parse(manifest_path).getroot()
    health_permissions = sorted(
        permission.get(ANDROID_ATTR + "name", "")
        for permission in root.findall("uses-permission")
        if permission.get(ANDROID_ATTR + "name", "").startswith(
            "android.permission.health."
        )
    )
    dal_hosts: set[str] = set()
    for intent_filter in root.findall("./application/activity/intent-filter"):
        if intent_filter.get(ANDROID_ATTR + "autoVerify") != "true":
            continue
        categories = {
            category.get(ANDROID_ATTR + "name", "")
            for category in intent_filter.findall("category")
        }
        actions = {
            action.get(ANDROID_ATTR + "name", "")
            for action in intent_filter.findall("action")
        }
        if "android.intent.action.VIEW" not in actions:
            continue
        if "android.intent.category.BROWSABLE" not in categories:
            continue
        for data in intent_filter.findall("data"):
            if data.get(ANDROID_ATTR + "scheme") == "https":
                host = data.get(ANDROID_ATTR + "host", "")
                if host:
                    dal_hosts.add(host)
    return {
        "health_permissions": health_permissions,
        "dal_hosts": sorted(dal_hosts),
        "dal_filter_present": expected_host in dal_hosts,
    }


def audit_source(
    source_root: Path,
    source_sha256: str,
    expected_avatar_sha256: str,
    expected_package: str,
    minimum_version_code: int,
    expected_dal_host: str,
    recorded_at: str,
) -> dict[str, object]:
    android_root = source_root / "android" / "app"
    gradle_path = android_root / "build.gradle"
    manifest_path = android_root / "src" / "main" / "AndroidManifest.xml"
    main_source_root = android_root / "src" / "main"
    assets_root = main_source_root / "assets"
    canonical_avatar = (
        source_root
        / "static"
        / "assets"
        / "avatar"
        / STAGE16A_NAME
    )

    gradle_text = _read_text(gradle_path)
    manifest = _manifest_contract(manifest_path, expected_dal_host)
    version_code_text = _gradle_value(gradle_text, "versionCode")
    version_code = int(version_code_text) if version_code_text and version_code_text.isdigit() else None
    package = _gradle_value(gradle_text, "applicationId")
    compile_sdk = _gradle_value(gradle_text, "compileSdk")
    target_sdk = _gradle_value(gradle_text, "targetSdk")

    android_assets = sorted(
        path.relative_to(assets_root).as_posix()
        for path in assets_root.rglob("*")
        if path.is_file()
    ) if assets_root.is_dir() else []
    stage16a_assets = [name for name in android_assets if name.lower().endswith("stage16a_ual12_animated.glb")]
    legacy_assets = [name for name in android_assets if LEGACY_AVATAR_RE.search(name)]
    offline_html_path = assets_root / "offline.html"
    offline_html = _read_text(offline_html_path)
    offline_runtime_assets = [
        name
        for name in android_assets
        if name.lower().endswith((".js", ".mjs", ".wasm"))
    ]

    source_files = sorted(
        path
        for path in main_source_root.rglob("*")
        if path.is_file() and path.suffix.lower() in {".java", ".kt"}
    ) if main_source_root.is_dir() else []
    source_text = "\n".join(_read_text(path) for path in source_files)
    health_implementation_markers = sorted(
        marker for marker in HEALTH_CODE_MARKERS if marker in source_text or marker in gradle_text
    )
    offline_entrypoint_reachable = any(
        marker in source_text
        for marker in (
            "file:///android_asset/offline.html",
            "https://appassets.androidplatform.net/assets/offline.html",
            "WebViewAssetLoader",
        )
    )

    canonical_avatar_sha256 = sha256_file(canonical_avatar) if canonical_avatar.is_file() else None
    packaged_stage16a_hashes = {
        name: sha256_file(assets_root / name) for name in stage16a_assets
    }
    checks = {
        "canonical_stage16a_present": canonical_avatar.is_file(),
        "canonical_stage16a_hash_matches": canonical_avatar_sha256 == expected_avatar_sha256,
        "package_matches": package == expected_package,
        "compile_sdk_36": compile_sdk == "36",
        "target_sdk_36": target_sdk == "36",
        "successor_version_code_reserved": version_code is not None
        and version_code >= minimum_version_code,
        "stage16a_packaged_in_android_source": bool(stage16a_assets)
        and expected_avatar_sha256 in packaged_stage16a_hashes.values(),
        "legacy_avatar_absent": not legacy_assets,
        "offline_entrypoint_non_placeholder": bool(offline_html)
        and not PLACEHOLDER_RE.search(offline_html),
        "offline_runtime_assets_packaged": bool(offline_runtime_assets),
        "offline_entrypoint_reachable": offline_entrypoint_reachable,
        "dal_https_autoverify_filter_present": bool(manifest["dal_filter_present"]),
        "health_connect_permissions_present": bool(manifest["health_permissions"]),
        "health_connect_implementation_present": bool(health_implementation_markers),
    }
    issue_by_check = {
        "canonical_stage16a_present": "CANONICAL_STAGE16A_SOURCE_MISSING",
        "canonical_stage16a_hash_matches": "CANONICAL_STAGE16A_HASH_MISMATCH",
        "package_matches": "PACKAGE_ID_MISMATCH",
        "compile_sdk_36": "COMPILE_SDK_NOT_36",
        "target_sdk_36": "TARGET_SDK_NOT_36",
        "successor_version_code_reserved": "SUCCESSOR_VERSION_CODE_NOT_RESERVED",
        "stage16a_packaged_in_android_source": "FIRST_INSTALL_STAGE16A_NOT_PACKAGED",
        "legacy_avatar_absent": "LEGACY_AVATAR_ASSET_PRESENT",
        "offline_entrypoint_non_placeholder": "OFFLINE_ENTRYPOINT_PLACEHOLDER",
        "offline_runtime_assets_packaged": "OFFLINE_RUNTIME_ASSETS_MISSING",
        "offline_entrypoint_reachable": "OFFLINE_ENTRYPOINT_NOT_REACHABLE",
        "dal_https_autoverify_filter_present": "DAL_HTTPS_AUTOVERIFY_FILTER_MISSING",
        "health_connect_permissions_present": "HEALTH_CONNECT_PERMISSIONS_MISSING",
        "health_connect_implementation_present": "HEALTH_CONNECT_IMPLEMENTATION_MISSING",
    }
    issues = sorted(issue_by_check[name] for name, passed in checks.items() if not passed)
    return {
        "schema": "thf-fitness-android-source-packaging-contract-v1",
        "lane": "android",
        "scope": "immutable_source_read_only_audit",
        "result": "PASS" if not issues else "BLOCKED",
        "final": False,
        "phone_pass": False,
        "play_ready": False,
        "source_sha256": source_sha256,
        "expected_avatar_sha256": expected_avatar_sha256,
        "canonical_avatar": {
            "path": canonical_avatar.relative_to(source_root).as_posix(),
            "sha256": canonical_avatar_sha256,
        },
        "android": {
            "package": package,
            "compile_sdk": compile_sdk,
            "target_sdk": target_sdk,
            "version_code": version_code,
            "asset_count": len(android_assets),
            "stage16a_assets": stage16a_assets,
            "stage16a_asset_sha256": packaged_stage16a_hashes,
            "legacy_avatar_assets": legacy_assets,
            "offline_runtime_assets": offline_runtime_assets,
            "dal_hosts": manifest["dal_hosts"],
            "health_permissions": manifest["health_permissions"],
            "health_implementation_markers": health_implementation_markers,
        },
        "checks": checks,
        "issues": issues,
        "recorded_at": recorded_at,
        "next_action": (
            "Create a successor canonical Android package source with versionCode >= "
            f"{minimum_version_code}; copy the already verified Stage16A asset into first-install "
            "Android assets with an offline renderer and reachable entrypoint, add the HTTPS "
            "autoVerify DAL filter, and implement only the Health Connect permissions actually used. "
            "Then build/sign once, rerun exact-candidate integrity, and keep physical QA fail-closed."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--source-sha256", required=True)
    parser.add_argument("--expected-avatar-sha256", required=True)
    parser.add_argument("--expected-package", default="com.topherofit.thf.pulse")
    parser.add_argument("--minimum-version-code", type=int, default=50002)
    parser.add_argument(
        "--expected-dal-host", default="thf-fitness-pulse-ul26f1.v2.appdeploy.ai"
    )
    parser.add_argument("--recorded-at", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--expect", choices=("PASS", "BLOCKED"), required=True)
    args = parser.parse_args()

    try:
        report = audit_source(
            args.source_root,
            args.source_sha256,
            args.expected_avatar_sha256.lower(),
            args.expected_package,
            args.minimum_version_code,
            args.expected_dal_host,
            args.recorded_at,
        )
    except (ET.ParseError, OSError, TypeError, ValueError) as exc:
        report = {
            "schema": "thf-fitness-android-source-packaging-contract-v1",
            "lane": "android",
            "scope": "immutable_source_read_only_audit",
            "result": "BLOCKED",
            "final": False,
            "phone_pass": False,
            "play_ready": False,
            "source_sha256": args.source_sha256,
            "issues": [f"SOURCE_AUDIT_ERROR:{type(exc).__name__}:{exc}"],
            "recorded_at": args.recorded_at,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["result"] == args.expect else 2


if __name__ == "__main__":
    raise SystemExit(main())
