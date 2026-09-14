#!/usr/bin/env python3
"""Fail-closed semantic verifier for THF Pulse phone QA candidates.

Uses stdlib only. It verifies that the APK contains a skinned/animated MPFB/UAL
human and that the shipped Motion Coach runtime actually drives semantic bones
on a render loop. This is package/runtime evidence only; it never substitutes
for physical-phone visible-motion validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

REQUIRED = {
    "assets/pulse/index.html",
    "assets/pulse/avatar.glb",
    "assets/pulse/three.min.js",
    "assets/pulse/GLTFLoader.js",
    "assets/pulse/photoreal.js",
    "assets/pulse/health-contracts.json",
}
EXPECTED_METRICS = {
    "activity",
    "workout",
    "steps",
    "distance",
    "calories",
    "heart_rate",
    "sleep",
    "body_composition",
}


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def parse_glb_json(data: bytes) -> dict:
    if len(data) < 20:
        raise ValueError("GLB too small")
    magic, version, declared_len = struct.unpack_from("<4sII", data, 0)
    if magic != b"glTF" or version != 2 or declared_len != len(data):
        raise ValueError("invalid GLB v2 header/length")
    pos = 12
    while pos + 8 <= len(data):
        chunk_len, chunk_type = struct.unpack_from("<II", data, pos)
        pos += 8
        end = pos + chunk_len
        if end > len(data):
            raise ValueError("GLB chunk exceeds file length")
        chunk = data[pos:end]
        pos = end
        if chunk_type == 0x4E4F534A:
            return json.loads(chunk.decode("utf-8").rstrip("\x00 \t\r\n"))
    raise ValueError("GLB JSON chunk missing")


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def verify(apk: Path) -> dict:
    apk_bytes = apk.read_bytes()
    evidence: dict[str, object] = {
        "schema": 1,
        "apk": apk.name,
        "apk_sha256": sha256(apk_bytes),
        "package_semantic_gate": "FAIL_CLOSED",
        "physical_phone_visible_motion": "PENDING_REQUIRED",
    }

    with zipfile.ZipFile(apk) as zf:
        bad = zf.testzip()
        require(bad is None, f"ZIP CRC failure: {bad}")
        names = set(zf.namelist())
        missing = sorted(REQUIRED - names)
        require(not missing, f"required runtime assets missing: {missing}")

        avatar = zf.read("assets/pulse/avatar.glb")
        gltf = parse_glb_json(avatar)
        skins = gltf.get("skins") or []
        nodes = gltf.get("nodes") or []
        meshes = gltf.get("meshes") or []
        animations = gltf.get("animations") or []
        animation_names = [str(a.get("name") or "") for a in animations]
        skin_joint_counts = [len(s.get("joints") or []) for s in skins]
        skinned_mesh_nodes = [n for n in nodes if "mesh" in n and "skin" in n]

        require(skins, "avatar has no skin")
        require(max(skin_joint_counts, default=0) >= 60, "avatar skeleton is not human-scale")
        require(len(meshes) >= 1 and len(skinned_mesh_nodes) >= 1, "avatar has no skin-bound mesh")
        require(len(animations) >= 10, "avatar animation library unexpectedly small")
        names_lower = {n.lower() for n in animation_names}
        require({"idle", "walk", "run"}.issubset(names_lower), "baseline locomotion clips missing")
        require(any(n.startswith("UAL1_") or n.startswith("UAL2_") for n in animation_names), "UAL animation provenance missing")

        runtime = zf.read("assets/pulse/photoreal.js").decode("utf-8")
        index = zf.read("assets/pulse/index.html").decode("utf-8")
        contract = json.loads(zf.read("assets/pulse/health-contracts.json"))

        runtime_needles = [
            "loader.loadAsync(cfg.assetUrl)",
            "if(o.isBone)bones.push(o)",
            "case 'squat'",
            "case 'run'",
            "case 'dynamic_warmup'",
            "function pose(t)",
            "requestAnimationFrame(frame)",
            "PulseNative?.poseEvent",
        ]
        missing_runtime = [x for x in runtime_needles if x not in runtime]
        require(not missing_runtime, f"Motion Coach runtime hooks missing: {missing_runtime}")

        index_needles = [
            'id="photoCanvas"',
            "assetUrl:'avatar.glb'",
            'src="three.min.js"',
            'src="GLTFLoader.js"',
            'src="photoreal.js"',
            "data-ar=",
            "data-en=",
        ]
        missing_index = [x for x in index_needles if x not in index]
        require(not missing_index, f"Motion Coach page wiring missing: {missing_index}")
        require("Workout Console" not in index, "legacy text-only Workout Console is active in Motion Coach page")

        metrics = set((contract.get("metrics") or {}).keys())
        require(metrics == EXPECTED_METRICS, f"health metric contract mismatch: {sorted(metrics)}")
        providers = contract.get("providers") or {}
        require(bool((providers.get("health_connect") or {}).get("permission_bridge")), "Health Connect permission bridge missing")
        require("samsung_health" in providers, "Samsung Health adapter boundary missing")
        rewards = contract.get("rewards") or {}
        require(rewards.get("provider_data_alone_authorizes_reward") is False, "provider data must not authorize rewards alone")
        require(rewards.get("pose_hook_alone_authorizes_reward") is False, "pose hook must not authorize rewards alone")

        evidence.update(
            {
                "zip_crc": "PASS",
                "avatar_sha256": sha256(avatar),
                "avatar_nodes": len(nodes),
                "avatar_meshes": len(meshes),
                "avatar_skins": len(skins),
                "avatar_max_joint_count": max(skin_joint_counts, default=0),
                "avatar_skinned_mesh_nodes": len(skinned_mesh_nodes),
                "avatar_animation_count": len(animations),
                "avatar_ual_animation_count": sum(n.startswith(("UAL1_", "UAL2_")) for n in animation_names),
                "baseline_clips": [n for n in animation_names if n.lower() in {"idle", "walk", "run"}],
                "motion_runtime_semantic_bone_driver": "PASS",
                "motion_runtime_render_loop": "PASS",
                "motion_runtime_pose_event_hook": "PASS",
                "legacy_text_workout_console_active": False,
                "health_metrics": sorted(metrics),
                "health_connect_permission_bridge": "PASS",
                "samsung_health_adapter_boundary": "PASS",
                "reward_proof_fail_closed": "PASS",
                "package_semantic_gate": "PASS_PHONE_VALIDATION_STILL_REQUIRED",
            }
        )
    return evidence


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("apk", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    try:
        result = verify(args.apk)
    except Exception as exc:
        print(f"THF_PULSE_MOTION_SEMANTIC_GATE=FAIL_CLOSED\nreason={type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        args.out.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
