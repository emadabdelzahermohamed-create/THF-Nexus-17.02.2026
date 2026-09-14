#!/usr/bin/env python3
import json
from pathlib import Path


def test_current_registries_are_fail_closed_and_expose_same_package_conflict():
    apps = json.loads(Path("ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json").read_text("utf-8"))
    games = json.loads(Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json").read_text("utf-8"))
    assert apps["truth_boundary"]["final_or_play_ready"] is False
    assert games["final_or_play_ready"] is False
    assert games["physical_device_status"] == "PENDING"

    app_by_pkg = {c["package"]: c["apk_sha256"] for c in apps["candidates"]}
    game_by_pkg = {c["package"]: c["apk_sha256"] for c in games["candidates"]}
    overlaps = set(app_by_pkg) & set(game_by_pkg)
    conflicts = {p for p in overlaps if app_by_pkg[p] != game_by_pkg[p]}

    # These are intentionally asserted until the release authority reconciles the
    # duplicate package streams. Removing this assertion requires a single exact
    # candidate SHA per package, not weakening the gate.
    assert "com.topherofit.thf.spark" in conflicts
    assert "com.topherofit.thf.rush" in conflicts


def test_game_candidates_remain_api36():
    games = json.loads(Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json").read_text("utf-8"))
    assert games["candidates"]
    assert all(c["target_sdk"] == 36 for c in games["candidates"])
