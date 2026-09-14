# THF Games Physical Device Acceptance V4 — 2026-09-14

Status: REQUIRED / FAIL-CLOSED / NOT_FINAL

V4 supersedes the acceptance-validation portion of V3 for the six exact candidates in `THF_GAME_DEVICE_CANDIDATES_V1.json`. Objective collection still uses `capture_android_device_evidence_v3.py`; V4 adds cryptographic binding of every manual evidence reference to a real file in the evidence bundle.

## Preconditions

- Authorized physical Android phone only; emulator/QEMU/ranchu/goldfish evidence is invalid.
- Exact APK bytes and package from the current candidate registry.
- Registry bytes must remain unchanged during the evidence session.
- No resign/repack after candidate SHA registration.
- Create a dedicated evidence directory per product/session; do not reference files outside it.

## Objective capture

```bash
python ReleaseOps/mobile/capture_android_device_evidence_v3.py \
  --registry ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json \
  --product <product> \
  --apk /path/to/exact-candidate.apk \
  --out out/<product>/device-evidence-v3.json
```

The collector binds registry SHA + exact APK SHA/package, rejects emulator signatures, verifies install/cold launch, requires same-PID background/resume, and captures RAM/frame/thermal/display/window/logcat evidence. It intentionally leaves manual observations false.

## Manual evidence records

For every required manual observation, retain a concrete non-empty file under the evidence root (screen recording, captured diagnostic trace, screenshot sequence, or other reviewable evidence as appropriate). Each record must contain:

```json
{
  "pass": true,
  "observed_at_utc": "2026-09-14T03:00:00Z",
  "evidence_ref": "evidence/<product>/<capability>.mp4",
  "evidence_sha256": "<64 lowercase hex chars>"
}
```

Compute the digest from the retained file itself, for example:

```bash
sha256sum out/<product>/evidence/<product>/<capability>.mp4
```

`evidence_ref` must be a safe relative path inside the evidence root. Absolute paths and `..` traversal are rejected. Missing, empty, or post-capture modified evidence files are rejected.

## Required observations

Common to all six: touch, orientation/layout/safe-area, offline->network transition, online/network transition, core user journey, gameplay interaction, observed FPS/RAM/thermal duration, crash-free operation, plus explicit `online_state_not_faked=true` and `local_mode_genuinely_local=true`.

Product-specific:
- Terra: avatar/player load, movement+camera, world/NPC interaction.
- Rift: Terra-equivalent observations plus real combat.
- Spark: real learning-game progression.
- Rush: real sensor motion + repetition counting.
- Learn Games: real learning-game progression.
- Fitness Games: real sensor motion + repetition counting.

## V4 validation

After objective and manual evidence are complete:

```bash
python ReleaseOps/mobile/validate_game_device_evidence_v4.py \
  ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json \
  out/<product>/device-evidence-v3.json \
  out/<product>
```

V4 first applies all V3 semantic/device/exact-SHA requirements, then verifies every required `evidence_ref` exists inside the supplied evidence root, is non-empty, and hashes exactly to `evidence_sha256`.

A V4 PASS is still **not** FINAL/PLAY_READY. It establishes a cryptographically bound physical-device evidence bundle for later explicit release review/promotion only.

## Current boundary

Until V4 passes against each exact candidate on a real phone, all six remain `PHYSICAL_DEVICE_PENDING` / `NOT_FINAL`. Build/static/package/backend evidence cannot substitute for this physical acceptance gate.
