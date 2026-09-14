#!/usr/bin/env python3
"""Fail-closed validator for THF physical-phone game acceptance evidence.

This validator never infers gameplay PASS from build/static/ADB-only evidence. It binds
one evidence document to the current candidate registry bytes, exact APK SHA/package,
a non-emulated physical Android device, objective runtime observations, and explicit
per-capability observation records with evidence references.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

SHA = re.compile(r"^[0-9a-f]{64}$")
SCHEMA = "thf-android-device-evidence-v3"
COMMON_MANUAL = (
    "touch",
    "orientation_layout",
    "offline_network_transition",
    "online_network_transition",
    "core_user_journey",
    "gameplay_interaction",
)
PRODUCT_MANUAL = {
    "terra": ("avatar_or_player_load", "movement_camera", "world_npc_interaction"),
    "rift": ("avatar_or_player_load", "movement_camera", "world_npc_interaction", "combat"),
    "spark": ("learning_progression",),
    "rush": ("sensor_motion", "repetition_counting"),
    "learn_games": ("learning_progression",),
    "fitness_games": ("sensor_motion", "repetition_counting"),
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> tuple[dict, str]:
    raw = path.read_bytes()
    return json.loads(raw), sha256_bytes(raw)


def candidate_for(registry: dict, product: str) -> dict | None:
    for row in registry.get("candidates", []):
        if isinstance(row, dict) and row.get("app") == product:
            return row
    return None


def _manual_pass(errors: list[str], observations: dict, key: str) -> None:
    row = observations.get(key)
    if not isinstance(row, dict):
        errors.append(f"manual_observations.{key}: missing record")
        return
    if row.get("pass") is not True:
        errors.append(f"manual_observations.{key}: pass must be true")
    ref = row.get("evidence_ref")
    if not isinstance(ref, str) or len(ref.strip()) < 3:
        errors.append(f"manual_observations.{key}: evidence_ref required")
    observed_at = row.get("observed_at_utc")
    if not isinstance(observed_at, str) or "T" not in observed_at or not observed_at.endswith("Z"):
        errors.append(f"manual_observations.{key}: observed_at_utc must be UTC ISO-like timestamp")


def validate(registry: dict, registry_sha: str, evidence: dict) -> list[str]:
    errors: list[str] = []
    if evidence.get("schema") != SCHEMA:
        errors.append("evidence schema mismatch")
    product = evidence.get("product")
    if product not in PRODUCT_MANUAL:
        errors.append("unknown product")
        return errors
    candidate = candidate_for(registry, product)
    if candidate is None:
        errors.append("product missing from current registry")
        return errors

    if evidence.get("registry_sha256") != registry_sha:
        errors.append("registry SHA mismatch: evidence is not bound to current registry bytes")
    if evidence.get("package") != candidate.get("package"):
        errors.append("package mismatch against current registry")
    if evidence.get("exact_candidate_sha256") != candidate.get("apk_sha256"):
        errors.append("APK SHA mismatch against current registry")
    if not SHA.fullmatch(str(evidence.get("exact_candidate_sha256", ""))):
        errors.append("invalid exact candidate SHA")

    device = evidence.get("device")
    if not isinstance(device, dict):
        errors.append("device record missing")
    else:
        if device.get("physical_device") is not True:
            errors.append("physical_device must be true; emulator evidence is forbidden")
        if device.get("emulator_detected") is not False:
            errors.append("emulator_detected must be false")
        fp = str(device.get("fingerprint_sha256", ""))
        if not SHA.fullmatch(fp):
            errors.append("device fingerprint_sha256 missing/invalid")
        if not str(device.get("model", "")).strip():
            errors.append("device model missing")
        if not str(device.get("sdk", "")).strip():
            errors.append("device sdk missing")

    objective = evidence.get("objective")
    if not isinstance(objective, dict):
        errors.append("objective evidence missing")
    else:
        for key in ("install_pass", "cold_launch_pass", "background_resume_pass", "crash_free_smoke_pass"):
            if objective.get(key) is not True:
                errors.append(f"objective.{key} must be true")
        pss = objective.get("total_pss_kb")
        if not isinstance(pss, int) or pss <= 0:
            errors.append("objective.total_pss_kb must be observed positive integer")
        frames = objective.get("framestats_rows")
        if not isinstance(frames, int) or frames <= 0:
            errors.append("objective.framestats_rows must be > 0")
        if objective.get("thermal_snapshot_present") is not True:
            errors.append("objective thermal snapshot required")
        if objective.get("fatal_runtime_markers") not in ([], None):
            errors.append("fatal runtime markers present")

    perf = evidence.get("performance_observation")
    if not isinstance(perf, dict):
        errors.append("performance_observation missing")
    else:
        # We require observed values, but impose no arbitrary FPS/RAM/thermal threshold.
        if not isinstance(perf.get("fps_observed"), (int, float)) or perf.get("fps_observed", 0) <= 0:
            errors.append("performance fps_observed must be recorded")
        if not isinstance(perf.get("ram_mb_observed"), (int, float)) or perf.get("ram_mb_observed", 0) <= 0:
            errors.append("performance ram_mb_observed must be recorded")
        if perf.get("thermal_status_observed") in (None, ""):
            errors.append("performance thermal_status_observed must be recorded")
        if not isinstance(perf.get("observation_seconds"), (int, float)) or perf.get("observation_seconds", 0) <= 0:
            errors.append("performance observation_seconds must be recorded")

    observations = evidence.get("manual_observations")
    if not isinstance(observations, dict):
        errors.append("manual_observations missing")
        observations = {}
    for key in COMMON_MANUAL + PRODUCT_MANUAL[product]:
        _manual_pass(errors, observations, key)

    if product == "rift" and "combat" not in PRODUCT_MANUAL[product]:
        errors.append("internal policy error: Rift combat requirement missing")
    if product in {"rush", "fitness_games"} and "sensor_motion" not in PRODUCT_MANUAL[product]:
        errors.append("internal policy error: sensor-motion requirement missing")

    if evidence.get("online_state_not_faked") is not True:
        errors.append("online_state_not_faked must be explicitly proven true")
    if evidence.get("local_mode_genuinely_local") is not True:
        errors.append("local_mode_genuinely_local must be explicitly proven true")
    if evidence.get("final_or_play_ready") is not False:
        errors.append("evidence input may not self-declare FINAL/PLAY_READY")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("registry", type=Path)
    ap.add_argument("evidence", type=Path)
    args = ap.parse_args()
    registry, registry_sha = load_json(args.registry)
    evidence, _ = load_json(args.evidence)
    errors = validate(registry, registry_sha, evidence)
    if errors:
        for err in errors:
            print("ERROR: " + err, file=sys.stderr)
        print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE=FAIL")
        print("FINAL_OR_PLAY_READY=FALSE")
        return 1
    print("THF_GAME_PHYSICAL_DEVICE_EVIDENCE=PASS")
    print(f"PRODUCT={evidence['product']}")
    print(f"EXACT_APK_SHA256={evidence['exact_candidate_sha256']}")
    print("FINAL_OR_PLAY_READY=FALSE")
    print("NOTE=Device evidence passed this validator; release promotion remains a separate explicit gate.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
