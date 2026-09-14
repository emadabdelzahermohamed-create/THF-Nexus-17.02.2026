#!/usr/bin/env python3
import json
from pathlib import Path


def test_current_registries_are_fail_closed_and_cross_stream_consistent():
    apps = json.loads(Path("ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json").read_text("utf-8"))
    games = json.loads(Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json").read_text("utf-8"))
    assert apps["truth_boundary"]["final_or_play_ready"] is False
    assert games["final_or_play_ready"] is False
    assert games["physical_device_status"] == "PENDING"

    app_by_pkg = {c["package"]: c["apk_sha256"] for c in apps["candidates"]}
    game_by_pkg = {c["package"]: c["apk_sha256"] for c in games["candidates"]}
    overlaps = set(app_by_pkg) & set(game_by_pkg)
    conflicts = {p for p in overlaps if app_by_pkg[p] != game_by_pkg[p]}

    # Cross-stream authority was reconciled only after Spark/Rush APPS_RC4 +
    # real-game-overlay candidates proved package identity, targetSdk 36 and
    # packaged real-game payload. The exact APK SHA must now be identical in
    # both registries while FINAL/PLAY_READY remains false pending phone evidence.
    assert "com.topherofit.thf.spark" in overlaps
    assert "com.topherofit.thf.rush" in overlaps
    assert conflicts == set()

    superseded = {(c["package"], c["apk_sha256"]) for c in apps.get("superseded_candidates", [])}
    assert ("com.topherofit.thf.spark", "92bc7f913d560a185044af2df7b1955d3a0b29eca920034edf3cd9741bce0c23") in superseded
    assert ("com.topherofit.thf.rush", "304164035cc4b82d23e2b2e6bf48abca3c466c46f5668a203cf0b4cfca223e99") in superseded


def test_game_candidates_remain_api36():
    games = json.loads(Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json").read_text("utf-8"))
    assert games["candidates"]
    assert all(c["target_sdk"] == 36 for c in games["candidates"])
