#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
APPS = Path("ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json")
GAMES = Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json")


def load(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def _valid_sha(value: object) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def main() -> int:
    errors: list[str] = []
    apps = load(APPS)
    games = load(GAMES)

    if apps.get("truth_boundary", {}).get("final_or_play_ready") is not False:
        errors.append("apps registry must remain final_or_play_ready=false before physical-device acceptance")
    if apps.get("truth_boundary", {}).get("all_pending") is not True:
        errors.append("apps registry all_pending must remain true before physical-device acceptance")
    if games.get("final_or_play_ready") is not False:
        errors.append("games registry must remain final_or_play_ready=false before physical-device acceptance")
    if games.get("physical_device_status") != "PENDING":
        errors.append("games physical_device_status must remain PENDING until exact-device evidence exists")

    by_package: dict[str, list[dict]] = {}
    for c in apps.get("candidates", []):
        pkg = c.get("package")
        sha = c.get("apk_sha256")
        source_sha = c.get("source_sha256")
        if not pkg or not _valid_sha(sha):
            errors.append(f"invalid apps candidate identity/SHA: {c.get('name')}")
            continue
        if source_sha is not None and not _valid_sha(source_sha):
            errors.append(f"invalid apps source SHA: {c.get('name')}")
        if c.get("status") != "PENDING_PHYSICAL_PHONE":
            errors.append(f"apps candidate {c.get('name')} unexpectedly promoted: {c.get('status')}")
        by_package.setdefault(pkg, []).append({
            "stream": "apps",
            "name": c.get("name"),
            "apk_sha256": sha,
            "source_sha256": source_sha,
        })

    for c in games.get("candidates", []):
        pkg = c.get("package")
        sha = c.get("apk_sha256")
        source_sha = c.get("source_sha256")
        if c.get("target_sdk") != 36:
            errors.append(f"game candidate {c.get('app')} targetSdk is not 36")
        if not pkg or not _valid_sha(sha):
            errors.append(f"invalid games candidate identity/SHA: {c.get('app')}")
            continue
        if not _valid_sha(source_sha):
            errors.append(f"invalid games source SHA: {c.get('app')}")
        if c.get("app") in {"terra", "rift"}:
            if c.get("sensor_landscape") is not True:
                errors.append(f"game candidate {c.get('app')} lost sensor-landscape")
            if c.get("expand_aspect") is not True:
                errors.append(f"game candidate {c.get('app')} lost expand aspect")
            if c.get("desktop_override_active") is not False:
                errors.append(f"game candidate {c.get('app')} has active desktop override")
        if c.get("app") == "rift" and c.get("requires_combat") is not True:
            errors.append("Rift candidate lost combat evidence requirement")
        if c.get("app") in {"rush", "fitness_games"} and c.get("requires_sensor_motion") is not True:
            errors.append(f"game candidate {c.get('app')} lost sensor-motion requirement")
        by_package.setdefault(pkg, []).append({
            "stream": "games",
            "name": c.get("app"),
            "apk_sha256": sha,
            "source_sha256": source_sha,
        })

    conflicts = []
    for pkg, entries in sorted(by_package.items()):
        apk_hashes = sorted({e["apk_sha256"] for e in entries})
        source_hashes = sorted({e["source_sha256"] for e in entries if e.get("source_sha256") is not None})
        reasons = []
        if len(apk_hashes) > 1:
            reasons.append("apk_sha256")
        # If two streams both claim source provenance for the same package, they
        # must name the same exact source bytes, not merely happen to emit the same APK.
        if len(entries) > 1 and len(source_hashes) > 1:
            reasons.append("source_sha256")
        if reasons:
            conflicts.append({"package": pkg, "reasons": reasons, "entries": entries})

    result = {
        "schema": "thf.cross-stream-candidate-consistency.v1",
        "status": "BLOCKED" if errors or conflicts else "PASS",
        "final_or_play_ready": False,
        "apps_candidates": len(apps.get("candidates", [])),
        "games_candidates": len(games.get("candidates", [])),
        "conflicts": conflicts,
        "errors": errors,
        "policy": "same Android package must have one authoritative exact APK SHA and one authoritative source SHA across release streams; game-specific device requirements remain fail-closed",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if errors or conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
