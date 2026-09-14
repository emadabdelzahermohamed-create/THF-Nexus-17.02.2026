#!/usr/bin/env python3
"""Fail-closed validator for the exact THF Rift RC37 Phone V1 Actions artifact.

This validates packaged bytes, not source/build presence. It deliberately keeps the
candidate NOT_FINAL until physical-device evidence is attached for the same APK SHA.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import pathlib
import re
import zipfile

EXPECTED_ARTIFACT_SHA256 = "7f447d35e4cd6e06f64fd7efbebbd8ac4c6e6cf92d00af4842ffab18faba043d"
EXPECTED_APK_SHA256 = "8d023174dc30cb7899c21b66e6d7deaca8e16ddd0371f337f589a812c22a8f15"
EXPECTED_SOURCE_SHA256 = "3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914"
EXPECTED_APK_NAME = "THF-RIFT-4.7.1-RC37-PHONE-V1.apk"
EXPECTED_PACKAGE = "com.topherofit.thf.rift.phoneqa"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_kv(text: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        if k in out:
            raise SystemExit(f"duplicate evidence key: {k}")
        out[k] = v
    return out


def safe_members(z: zipfile.ZipFile) -> list[str]:
    names = z.namelist()
    for name in names:
        p = pathlib.PurePosixPath(name)
        if p.is_absolute() or ".." in p.parts:
            raise SystemExit(f"unsafe zip member: {name}")
    return names


def require_eq(data: dict[str, str], key: str, expected: str) -> None:
    got = data.get(key)
    if got != expected:
        raise SystemExit(f"{key}: expected {expected!r}, got {got!r}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("artifact_zip", type=pathlib.Path)
    args = ap.parse_args()
    artifact = args.artifact_zip.resolve()
    if not artifact.is_file():
        raise SystemExit("artifact ZIP missing")

    artifact_sha = sha256_file(artifact)
    if artifact_sha != EXPECTED_ARTIFACT_SHA256:
        raise SystemExit(f"artifact SHA mismatch: {artifact_sha}")

    with zipfile.ZipFile(artifact) as outer:
        names = safe_members(outer)
        required_outer = {
            EXPECTED_APK_NAME,
            "EVIDENCE.txt",
            "TRUTH.txt",
            "badging-phone.txt",
            "apksigner.txt",
            "import.log",
            "boot.log",
            "export.log",
            "local-training.json",
            "mobile.json",
            "network.txt",
        }
        missing = sorted(required_outer.difference(names))
        if missing:
            raise SystemExit(f"artifact missing required files: {missing}")

        evidence = parse_kv(outer.read("EVIDENCE.txt").decode("utf-8"))
        truth = parse_kv(outer.read("TRUTH.txt").decode("utf-8"))
        badging = outer.read("badging-phone.txt").decode("utf-8", errors="replace")
        signer = outer.read("apksigner.txt").decode("utf-8", errors="replace")
        apk = outer.read(EXPECTED_APK_NAME)

        require_eq(evidence, "THF_RIFT_RC37_PHONE_V1", "BUILT")
        require_eq(evidence, "canonical_source_sha256", EXPECTED_SOURCE_SHA256)
        require_eq(evidence, "canonical_archive_unchanged", "true")
        require_eq(evidence, "candidate_package", EXPECTED_PACKAGE)
        require_eq(evidence, "target_sdk", "36")
        require_eq(evidence, "engine", "Godot-4.7.2")
        require_eq(evidence, "sensor_landscape_setting", "PASS")
        require_eq(evidence, "expandable_aspect", "PASS")
        require_eq(evidence, "desktop_window_override", "NONE")
        require_eq(evidence, "local_training_mode", "GENUINE_LOCAL_STATE")
        require_eq(evidence, "local_training_online_session_faked", "FALSE")
        require_eq(evidence, "local_training_start_backend_calls", "0")
        require_eq(evidence, "online_act_authority", "PRESERVED_WEBSOCKET_OR_HTTP_TICK")
        require_eq(evidence, "ranked_social_economy_world_local_mutation", "DISABLED")
        require_eq(evidence, "placeholder_endpoint_markers", "0")
        require_eq(evidence, "physical_device_status", "PENDING")
        require_eq(evidence, "final_or_play_ready", "FALSE")
        require_eq(evidence, "production_signing", "false")
        require_eq(evidence, "production_cutover", "false")
        require_eq(evidence, "apk_sha256", EXPECTED_APK_SHA256)

        require_eq(truth, "status", "PASS")
        require_eq(truth, "apk_sha256", EXPECTED_APK_SHA256)
        require_eq(truth, "package", EXPECTED_PACKAGE)
        require_eq(truth, "target_sdk", "36")
        require_eq(truth, "payload", "PASS")
        require_eq(truth, "qa_signing_only", "true")
        require_eq(truth, "production_signing", "false")
        require_eq(truth, "device_status", "PENDING")
        require_eq(truth, "final_status", "NOT_FINAL")

        apk_sha = sha256_bytes(apk)
        if apk_sha != EXPECTED_APK_SHA256:
            raise SystemExit(f"nested APK SHA mismatch: {apk_sha}")
        if str(len(apk)) != evidence.get("apk_size_bytes"):
            raise SystemExit("nested APK size does not match evidence")
        if f"package: name='{EXPECTED_PACKAGE}'" not in badging:
            raise SystemExit("badging package mismatch")
        if "targetSdkVersion:'36'" not in badging or "native-code: 'arm64-v8a'" not in badging:
            raise SystemExit("badging targetSdk/native-code mismatch")
        if "Verifies" not in signer or "Number of signers: 1" not in signer:
            raise SystemExit("APK signature verification evidence missing")

        for log_name in ("import.log", "boot.log", "export.log"):
            text = outer.read(log_name).decode("utf-8", errors="replace")
            if re.search(r"SCRIPT ERROR|Parse Error|Parser Error|Failed to load script|Invalid call|Invalid get index|Invalid set index", text, re.I):
                raise SystemExit(f"Godot fault marker in {log_name}")

    with zipfile.ZipFile(io.BytesIO(apk)) as inner:
        entries = safe_members(inner)
        entry_set = set(entries)
        if "assets/project.binary" not in entry_set:
            raise SystemExit("missing packaged Godot project.binary")
        if "assets/native/arena/ArenaMain.gdc" not in entry_set:
            raise SystemExit("missing compiled ArenaMain gameplay script")
        if "assets/native/scenes/arena_main.tscn.remap" not in entry_set:
            raise SystemExit("missing Arena main scene remap")
        if "lib/arm64-v8a/libgodot_android.so" not in entry_set:
            raise SystemExit("missing arm64 Godot runtime")
        if not any(x.startswith("assets/.godot/exported/") and x.endswith("-arena_main.scn") for x in entries):
            raise SystemExit("missing exported Rift arena scene")
        if not any("thf_mpfb_stage16a_ual12_animated.glb-" in x and x.endswith(".scn") for x in entries):
            raise SystemExit("missing imported MPFB/UAL avatar payload")
        for weapon in ("Pistol.glb-", "Rifle.glb-", "Shotgun.glb-"):
            if not any(weapon in x and x.endswith(".scn") for x in entries):
                raise SystemExit(f"missing imported combat payload: {weapon}")
        if len([x for x in entries if x.startswith("assets/")]) < 300:
            raise SystemExit("implausibly small Godot game payload; possible template/wrapper")
        if any(x.startswith(("lib/x86/", "lib/x86_64/")) for x in entries):
            raise SystemExit("unexpected desktop/emulator ABI in phone candidate")

    print("THF_RIFT_RC37_PHONE_V1_EXACT_ARTIFACT=PASS")
    print(f"artifact_sha256={artifact_sha}")
    print(f"apk_sha256={EXPECTED_APK_SHA256}")
    print("game_specific_payload=PASS")
    print("mpfb_ual_payload=PASS")
    print("combat_payload=PASS")
    print("physical_device_status=PENDING")
    print("final_or_play_ready=FALSE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
