#!/usr/bin/env python3
import argparse, json, pathlib, re, sys

SCHEMA = "thf-game-device-candidates-v1"
SHA = re.compile(r"^[0-9a-f]{64}$")
EXPECTED = {"terra", "rift", "spark", "rush", "learn_games", "fitness_games"}


def validate(doc: dict) -> list[str]:
    errors: list[str] = []
    if doc.get("schema") != SCHEMA:
        errors.append("schema mismatch")
    if doc.get("final_or_play_ready") is not False:
        errors.append("final_or_play_ready must be false")
    if doc.get("physical_device_status") != "PENDING":
        errors.append("physical_device_status must be PENDING")
    rows = doc.get("candidates")
    if not isinstance(rows, list):
        return errors + ["candidates must be a list"]
    apps = [r.get("app") for r in rows if isinstance(r, dict)]
    if set(apps) != EXPECTED or len(apps) != len(EXPECTED):
        errors.append("candidate set must contain exactly the six game apps once")
    if len(set(apps)) != len(apps):
        errors.append("duplicate app")
    packages, apks = set(), set()
    for i, r in enumerate(rows):
        if not isinstance(r, dict):
            errors.append(f"candidate[{i}] malformed"); continue
        app = r.get("app")
        for key in ("source_sha256", "apk_sha256", "artifact_digest"):
            if not SHA.fullmatch(str(r.get(key, ""))):
                errors.append(f"{app}: invalid {key}")
        pkg = r.get("package")
        if not isinstance(pkg, str) or "." not in pkg or any(c.isspace() for c in pkg):
            errors.append(f"{app}: invalid package")
        elif pkg in packages:
            errors.append(f"{app}: duplicate package")
        packages.add(pkg)
        apk = r.get("apk_sha256")
        if apk in apks:
            errors.append(f"{app}: duplicate apk sha")
        apks.add(apk)
        if r.get("target_sdk") != 36:
            errors.append(f"{app}: target_sdk must be 36")
        if not isinstance(r.get("workflow_run"), int) or r["workflow_run"] <= 0:
            errors.append(f"{app}: invalid workflow_run")
        if not isinstance(r.get("artifact_id"), int) or r["artifact_id"] <= 0:
            errors.append(f"{app}: invalid artifact_id")
        if r.get("desktop_override_active") is not False:
            errors.append(f"{app}: desktop override must be inactive")
        if app in {"terra", "rift"}:
            if r.get("sensor_landscape") is not True:
                errors.append(f"{app}: sensor_landscape required")
            if r.get("expand_aspect") is not True:
                errors.append(f"{app}: expand_aspect required")
        if app == "rift" and r.get("requires_combat") is not True:
            errors.append("rift: combat evidence must be required")
        if app != "rift" and r.get("requires_combat") is not False:
            errors.append(f"{app}: unexpected combat requirement")
        if app in {"rush", "fitness_games"}:
            if r.get("requires_sensor_motion") is not True:
                errors.append(f"{app}: sensor-motion evidence must be required")
        elif r.get("requires_sensor_motion") is not False:
            errors.append(f"{app}: unexpected sensor-motion requirement")
    rejected = doc.get("rejected_historical_candidates")
    if not isinstance(rejected, list) or not rejected:
        errors.append("rejected_historical_candidates missing")
    else:
        for p in rejected:
            if not isinstance(p, str) or not re.fullmatch(r"[0-9a-f]{8,64}", p):
                errors.append("invalid rejected historical candidate prefix")
            if any(isinstance(a, str) and a.startswith(p) for a in apks):
                errors.append("current candidate appears in rejected historical set")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("registry", type=pathlib.Path)
    args = ap.parse_args()
    doc = json.loads(args.registry.read_text())
    errors = validate(doc)
    if errors:
        for e in errors: print("ERROR: " + e, file=sys.stderr)
        return 1
    print("THF_GAME_DEVICE_CANDIDATE_REGISTRY=PASS")
    print("PHYSICAL_DEVICE_STATUS=PENDING")
    print("FINAL_OR_PLAY_READY=FALSE")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
