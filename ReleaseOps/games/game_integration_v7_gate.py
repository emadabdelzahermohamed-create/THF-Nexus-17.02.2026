from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUTH = ROOT / "ReleaseOps/games/LATEST_GAME_AUTHORITY_V1.json"
INTEGRATION = ROOT / "ReleaseOps/integration_factory/ANDROID_SHARED_INTEGRATION_V7.json"

EXPECTED = {
    "terra": ("THF World", "com.topherofit.thf.terra"),
    "rift": ("THF Arena", "com.topherofit.thf.rift"),
    "spark": ("THF Learn Games", "com.topherofit.thf.spark"),
    "rush": ("THF Motion Games", "com.topherofit.thf.rush"),
}


def fail(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def main() -> None:
    authority = json.loads(AUTH.read_text(encoding="utf-8"))
    integration = json.loads(INTEGRATION.read_text(encoding="utf-8"))
    games = authority["games"]

    if authority.get("final_or_play_ready") is not False:
        fail("game authority must remain NOT_FINAL before physical-device evidence")

    for key, (name, package_id) in EXPECTED.items():
        game = games.get(key) or fail(f"missing authority game: {key}")
        if game.get("user_facing_name") != name:
            fail(f"{key}: user-facing name drift")
        if game.get("canonical_package_id") != package_id:
            fail(f"{key}: package-id drift")
        if game.get("target_sdk") != 36 or game.get("arm64_required") is not True:
            fail(f"{key}: API36/arm64 contract drift")
        if game.get("physical_device_status") != "PENDING":
            fail(f"{key}: physical-device truth drift")

    rift = games["rift"]
    if rift.get("authoritative_version") != "4.7.5-rc41" or rift.get("eligible_candidate_apk_sha256") is not None:
        fail("Rift must stay exact RC41 with no older APK promoted")

    rush = games["rush"]
    if rush.get("verified_motion_required") is not True:
        fail("Rush verified-motion requirement missing")
    if rush.get("reward_bearing_health_evidence_required") is not True:
        fail("Rush reward-bearing health evidence requirement missing")

    text = json.dumps(integration, sort_keys=True).lower()
    required_terms = ("health_connect", "manual_activity", "fabricat", "physical_device", "final_or_play_ready")
    for term in required_terms:
        if term not in text:
            fail(f"V7 integration truth missing {term}")

    # Motion rewards must never become authoritative from client/manual input.
    if '"manual_activity_is_verified_evidence": true' in text:
        fail("manual activity incorrectly promoted to verified evidence")
    if '"final_or_play_ready": true' in text or '"physical_device_pass": true' in text:
        fail("integration truth incorrectly claims device/final pass")

    print("PASS: THF games authority is compatible with V7 identity/health boundaries")
    print("PASS: Rift RC41 stale-candidate rejection preserved")
    print("PASS: Rush verified-motion/reward evidence boundary preserved")
    print("PASS: NOT_FINAL / physical-device pending truth preserved")


if __name__ == "__main__":
    main()
