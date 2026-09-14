# THF Physical Device Acceptance V7 — 2026-09-14

Status: **REQUIRED / NOT_FINAL / PHYSICAL_DEVICE_PENDING**

This protocol applies to the exact registered Android game candidates in `THF_GAME_DEVICE_CANDIDATES_V1.json`. It does not replace package, payload, server-authority, anti-cheat, source-lock, Godot, API36, or asset-provenance gates already proven for the same SHA.

## Non-negotiable identity chain

A phone acceptance session must bind all evidence to one physical phone session and one exact candidate:

1. Read `THF_GAME_DEVICE_CANDIDATES_V1.json` and hash the registry bytes.
2. Verify the candidate APK SHA-256 before installation.
3. Run the V3 objective collector on exactly one authorized physical Android phone; emulators/QEMU/ranchu/goldfish are rejected.
4. Keep all manual gameplay, authority, objective and performance observations inside the same declared session interval and session ID.
5. After installation, run `capture_installed_apk_identity_v1.py` while the same phone/session is connected. It resolves `pm path <package>`, requires exactly one `/data/app/.../base.apk`, reads those installed bytes through ADB, hashes them, and requires equality with the registered exact candidate SHA-256.
6. Preserve and SHA-bind every manual, authority, objective and performance evidence file.
7. Validate the completed bundle with `validate_game_device_evidence_v7.py`.

A pre-install APK hash is not sufficient: the package bytes actually installed on the phone must be proven identical to the candidate under test.

## Required common observations

The exact candidate must have evidence for installation, cold launch, touch interaction, orientation/safe-area behavior, same-PID HOME/background/resume, offline/network transition behavior, core gameplay, crash-free execution, online-authority behavior, genuine local/offline behavior, FPS observation, RAM observation and thermal observation.

No arbitrary FPS/RAM/thermal threshold is invented by the evidence tooling. The measurements are captured for release judgment and regression comparison.

## Product-specific observations

- **Terra / Nexus World:** real player/avatar load, locomotion, camera, touch HUD, world/NPC interaction and sensor-landscape/expand behavior.
- **Rift / Nexus Arena:** Terra-class observations plus real combat interaction.
- **Spark:** real learning-game interaction and progression.
- **Rush:** real sensor motion and repetition counting.
- **Learn Games:** real learning-game interaction and progression.
- **Fitness Games:** real sensor motion and repetition counting.

## Authority truth

Online ranked/social/economy/world mutation must remain backend-authoritative. A local/offline mode may function locally, but must not fabricate online/ranked/social/economy state. Evidence for both authority behavior and local-mode truth must be captured in the same phone session and hash-bound to files.

## Commands

Example flow from the repository root after the exact candidate APK and a physical phone are available:

```bash
python3 ReleaseOps/mobile/capture_android_device_evidence_v3.py \
  --registry ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json \
  --product terra \
  --apk /path/to/exact-candidate.apk \
  --out /path/to/evidence/evidence.json

# Complete the required manual/authority/performance evidence inside the same session.

PYTHONPATH=ReleaseOps/mobile python3 ReleaseOps/mobile/capture_installed_apk_identity_v1.py \
  --evidence /path/to/evidence/evidence.json \
  --evidence-root /path/to/evidence

PYTHONPATH=ReleaseOps/mobile python3 ReleaseOps/mobile/validate_game_device_evidence_v7.py \
  ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json \
  /path/to/evidence/evidence.json \
  /path/to/evidence
```

Replace `terra` with the registered product key for each candidate.

## Release truth

A V7 evidence validation PASS is necessary but does not independently declare FINAL/PLAY_READY. Promotion requires the complete release decision over the exact candidate and all required evidence. Until a real physical phone produces that evidence, all six candidates remain `PHYSICAL_DEVICE_PENDING` and `final_or_play_ready=false`.
