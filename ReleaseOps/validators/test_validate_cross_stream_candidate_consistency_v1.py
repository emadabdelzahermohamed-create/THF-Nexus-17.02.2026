#!/usr/bin/env python3
import json
from pathlib import Path


def _load():
    apps = json.loads(Path("ReleaseOps/apps_factory/THF_APPS_PHYSICAL_DEVICE_EVIDENCE_REGISTRY_V1.json").read_text("utf-8"))
    games = json.loads(Path("ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json").read_text("utf-8"))
    return apps, games


def test_current_registries_are_fail_closed_and_cross_stream_consistent():
    apps, games = _load()
    assert apps["truth_boundary"]["all_pending"] is True
    assert apps["truth_boundary"]["final_or_play_ready"] is False
    assert games["final_or_play_ready"] is False
    assert games["physical_device_status"] == "PENDING"

    app_by_pkg = {c["package"]: c for c in apps["candidates"]}
    game_by_pkg = {c["package"]: c for c in games["candidates"]}
    overlaps = set(app_by_pkg) & set(game_by_pkg)
    assert "com.topherofit.thf.spark" in overlaps
    assert "com.topherofit.thf.rush" in overlaps

    for package in overlaps:
        assert app_by_pkg[package]["apk_sha256"] == game_by_pkg[package]["apk_sha256"]
        if app_by_pkg[package].get("source_sha256") is not None:
            assert app_by_pkg[package]["source_sha256"] == game_by_pkg[package]["source_sha256"]

    superseded = {(c["package"], c["apk_sha256"]) for c in apps.get("superseded_candidates", [])}
    assert ("com.topherofit.thf.spark", "92bc7f913d560a185044af2df7b1955d3a0b29eca920034edf3cd9741bce0c23") in superseded
    assert ("com.topherofit.thf.rush", "304164035cc4b82d23e2b2e6bf48abca3c466c46f5668a203cf0b4cfca223e99") in superseded


def test_game_candidates_remain_api36_and_device_requirements_fail_closed():
    _, games = _load()
    rows = {c["app"]: c for c in games["candidates"]}
    assert rows
    assert all(c["target_sdk"] == 36 for c in rows.values())

    for app in ("terra", "rift"):
        assert rows[app]["sensor_landscape"] is True
        assert rows[app]["expand_aspect"] is True
        assert rows[app]["desktop_override_active"] is False
    assert rows["rift"]["requires_combat"] is True
    assert rows["rush"]["requires_sensor_motion"] is True
    assert rows["fitness_games"]["requires_sensor_motion"] is True


def test_shared_game_packages_keep_source_provenance_not_only_apk_identity():
    apps, games = _load()
    app_by_pkg = {c["package"]: c for c in apps["candidates"]}
    game_by_pkg = {c["package"]: c for c in games["candidates"]}
    for package in ("com.topherofit.thf.spark", "com.topherofit.thf.rush"):
        assert app_by_pkg[package]["source_sha256"]
        assert game_by_pkg[package]["source_sha256"]
        assert app_by_pkg[package]["source_sha256"] == game_by_pkg[package]["source_sha256"]
