#!/usr/bin/env python3
"""Fail-closed static contract for THF local game overlays.

This does NOT establish device readiness. It only proves that the disposable local
practice overlays are in-memory/local and contain no online mutation transport,
ranked/social/economy simulation, or persistent fake-authoritative state.
"""
from __future__ import annotations
import argparse, json, pathlib, re, sys

FORBIDDEN_TRANSPORT = (
    "HttpURLConnection", "URLConnection", "OkHttp", "Retrofit", "WebSocket",
    "java.net.", "android.net.", "http://", "https://", "/api/",
)
FORBIDDEN_PERSISTENCE = (
    "SharedPreferences", "SQLiteDatabase", "RoomDatabase", "FileOutputStream",
    "openFileOutput", "ContentResolver.insert",
)


def audit(path: pathlib.Path, family: str) -> dict:
    text = path.read_text(encoding="utf-8")
    low = text.lower()
    checks = {}
    checks["offline_authority_marker"] = "OFFLINE_AUTHORITY=LOCAL_ONLY_NO_RANKED_SOCIAL_ECONOMY_MUTATION" in text
    checks["readiness_promotion_disabled"] = "READINESS_PROMOTION=NO" in text
    checks["no_network_transport_in_overlay_generator"] = not any(x.lower() in low for x in FORBIDDEN_TRANSPORT)
    checks["no_persistent_fake_authority_state"] = not any(x.lower() in low for x in FORBIDDEN_PERSISTENCE)
    checks["local_game_view_present"] = "GameView" in text or "LocalGameView" in text
    checks["frame_loop_present"] = "Choreographer" in text and "postFrameCallback" in text
    checks["touch_input_present"] = "onTouchEvent" in text
    checks["explicit_no_fake_online_copy"] = (
        "never fabricated" in low or "never simulated" in low or
        "no ranked/social/economy" in low or "ranked/social/economy state is never" in low
    )
    if family == "spark_rush":
        checks["spark_learning_progression_local"] = all(x in text for x in ("score", "streak", "level", "nextQuestion"))
        checks["rush_sensor_progression_local"] = all(x in text for x in ("SensorManager", "SensorEventListener", "reps"))
    elif family == "learn_fitness":
        checks["learn_mastery_progression_local"] = all(x in text for x in ("mastery", "score", "level", "nextQuestion"))
        checks["fitness_sensor_progression_local"] = all(x in text for x in ("SensorManager", "SensorEventListener", "repCount", "setCount"))
    else:
        raise ValueError(f"unsupported family: {family}")
    return {
        "schema": "thf-game-offline-local-truth-v1",
        "path": str(path),
        "family": family,
        "checks": checks,
        "passed": all(checks.values()),
        "truth_boundary": "STATIC_LOCAL_OVERLAY_CONTRACT_ONLY_NOT_DEVICE_OR_PLAY_READY",
        "final_or_play_ready": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("path", type=pathlib.Path)
    p.add_argument("--family", required=True, choices=["spark_rush", "learn_fitness"])
    p.add_argument("--json-out", type=pathlib.Path)
    a = p.parse_args()
    r = audit(a.path, a.family)
    rendered = json.dumps(r, indent=2, sort_keys=True) + "\n"
    if a.json_out:
        a.json_out.parent.mkdir(parents=True, exist_ok=True)
        a.json_out.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if r["passed"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
