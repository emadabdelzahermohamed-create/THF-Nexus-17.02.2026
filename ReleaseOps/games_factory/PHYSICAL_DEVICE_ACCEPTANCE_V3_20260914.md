# THF Games Physical Device Acceptance V3 — 2026-09-14

Status: REQUIRED / FAIL-CLOSED / NOT_FINAL

This protocol applies to the six exact Android game/game-like candidates in `THF_GAME_DEVICE_CANDIDATES_V1.json`. It does not replace package/payload/API36/source gates and may not be executed against an emulator, repacked APK, historical APK, or a candidate whose bytes no longer match the registry.

## 1. Preconditions

- Use one authorized physical Android phone visible in `adb devices`.
- Use the exact APK bytes from the registry artifact.
- Do not resign/repack the APK after its SHA was registered.
- Keep the current registry file unchanged during a device evidence session.
- Screen-record or otherwise retain concrete evidence for every manual observation that will later be marked PASS.

## 2. Objective capture

Example for Terra (substitute product/APK path for the other candidates):

```bash
python ReleaseOps/mobile/capture_android_device_evidence_v3.py \
  --registry ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json \
  --product terra \
  --apk /path/to/exact-terra.apk \
  --out out/terra-device-evidence-v3.json
```

The collector derives the package and expected APK SHA from the registry, hashes the registry bytes into the evidence, rejects QEMU/emulator signatures, installs the APK, performs a cold launch, sends the app to HOME, and only records background/resume PASS if the same process PID survives and returns to foreground. It captures RAM, frame-stat rows, thermal/display/window/package snapshots and crash markers.

The collector deliberately leaves gameplay/touch/network/manual observations FALSE. Do not edit them to true without running the corresponding test on that exact APK/device session and recording an evidence reference.

## 3. Common manual observations for every candidate

Record PASS + UTC observation time + concrete `evidence_ref` for:

- touch controls / hit targets / safe-area usability;
- orientation and layout behavior;
- offline -> network transition;
- online/network transition;
- complete core user journey;
- real gameplay interaction;
- performance observation: actual FPS, RAM, thermal status and observation duration.

Also explicitly prove:

- `online_state_not_faked=true`: ranked/social/economy/world-mutation state is not fabricated locally;
- `local_mode_genuinely_local=true`: offline/local practice or exploration remains genuinely local and does not claim remote success.

## 4. Product-specific observations

- **Terra / Nexus World:** real avatar/player load, movement + camera, world/NPC interaction.
- **Rift / Nexus Arena:** Terra-equivalent player/movement/camera/world evidence plus actual combat interaction.
- **Spark:** learning-game progression through real interactive gameplay.
- **Rush:** real physical sensor-motion detection and repetition counting.
- **Learn Games:** learning-game progression through real interactive gameplay.
- **Fitness Games:** real physical sensor-motion detection and repetition counting.

## 5. Validation

After objective + manual evidence is complete:

```bash
python ReleaseOps/mobile/validate_game_device_evidence_v3.py \
  ReleaseOps/games_factory/THF_GAME_DEVICE_CANDIDATES_V1.json \
  out/<product>-device-evidence-v3.json
```

PASS here means the evidence document is complete and bound to the current registry + exact candidate. It still does **not** self-promote the app to FINAL/PLAY_READY. Release promotion remains a separate explicit gate after evidence review.

## 6. Invalid evidence conditions

Evidence is rejected if any of the following is true:

- registry SHA differs from the current registry bytes;
- APK SHA/package differs from the current product candidate;
- device is emulator/QEMU/ranchu/goldfish/generic emulator class;
- install/cold-launch/same-PID resume/crash-free objective gates fail;
- RAM/frame/thermal observations are absent;
- a required manual observation is missing, false, lacks UTC observation time, or lacks an evidence reference;
- Rift combat evidence is absent;
- Rush/Fitness sensor-motion or repetition evidence is absent;
- online state is faked locally or local mode is not genuinely local;
- the evidence file attempts to declare itself FINAL/PLAY_READY.

## 7. Current boundary

Until this protocol is completed for each exact candidate on a physical phone, all six candidates remain `PHYSICAL_DEVICE_PENDING` and `NOT_FINAL`.
