#!/usr/bin/env python3
from __future__ import annotations
import json, re, sys
from pathlib import Path

SHA_RE = re.compile(r"^[0-9a-f]{64}$")
APPS = Path("ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json")
GAMES = Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json")


def load(path: Path) -> dict:
    return json.loads(path.read_text("utf-8"))


def main() -> int:
    errors: list[str] = []
    apps = load(APPS)
    games = load(GAMES)

    if apps.get("truth_boundary", {}).get("final_or_play_ready") is not False:
        errors.append("apps registry must remain final_or_play_ready=false before physical-device acceptance")
    if games.get("final_or_play_ready") is not False:
        errors.append("games registry must remain final_or_play_ready=false before physical-device acceptance")
    if games.get("physical_device_status") != "PENDING":
        errors.append("games physical_device_status must remain PENDING until exact-device evidence exists")

    by_package: dict[str, list[dict]] = {}
    for c in apps.get("candidates", []):
        pkg = c.get("package")
        sha = c.get("apk_sha256")
        if not pkg or not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            errors.append(f"invalid apps candidate identity/SHA: {c.get('name')}")
            continue
        if c.get("status") != "PENDING_PHYSICAL_PHONE":
            errors.append(f"apps candidate {c.get('name')} unexpectedly promoted: {c.get('status')}")
        by_package.setdefault(pkg, []).append({"stream": "apps", "name": c.get("name"), "apk_sha256": sha})

    for c in games.get("candidates", []):
        pkg = c.get("package")
        sha = c.get("apk_sha256")
        if c.get("target_sdk") != 36:
            errors.append(f"game candidate {c.get('app')} targetSdk is not 36")
        if not pkg or not isinstance(sha, str) or not SHA_RE.fullmatch(sha):
            errors.append(f"invalid games candidate identity/SHA: {c.get('app')}")
            continue
        by_package.setdefault(pkg, []).append({"stream": "games", "name": c.get("app"), "apk_sha256": sha})

    conflicts = []
    for pkg, entries in sorted(by_package.items()):
        hashes = sorted({e["apk_sha256"] for e in entries})
        if len(hashes) > 1:
            conflicts.append({"package": pkg, "entries": entries})

    result = {
        "schema": "thf.cross-stream-candidate-consistency.v1",
        "status": "BLOCKED" if errors or conflicts else "PASS",
        "final_or_play_ready": False,
        "apps_candidates": len(apps.get("candidates", [])),
        "games_candidates": len(games.get("candidates", [])),
        "conflicts": conflicts,
        "errors": errors,
        "policy": "same Android package must have one authoritative exact APK SHA before release promotion; physical-device evidence remains SHA-bound",
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    # Candidate conflicts are a release blocker by design, not a tooling crash.
    return 2 if errors or conflicts else 0


if __name__ == "__main__":
    sys.exit(main())
