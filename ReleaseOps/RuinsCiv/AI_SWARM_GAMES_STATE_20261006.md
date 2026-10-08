# RuinsCiv — AI Swarm Games State

## Canonical execution baseline
- Base branch: `automation/ruinsciv-android-qa-20260922`
- Exact tested source SHA: `4d009d73ce3031266e5658b8c924178c804c1f1b`
- Reconciliation merge SHA: `f45fe77aa77c5ce1bfc1f47e72a0f5db4baaa792`
- Engine/package contract retained: Godot 4.7.2, Android API 36, arm64-v8a, QA package `com.topherofit.ruins.civ.phoneqa`.
- Source recovery / Android packaging provenance already passed for this exact SHA and MUST NOT be rerun merely because runtime failed.

## 2026-10-07 physical Android evidence — release rejection
The exact QA candidate was installed and opened on a physical Android phone. This converts the previously pending runtime/visual gate into an evidence-backed FAIL while preserving the already-proven packaging PASS.

Observed evidence supplied from the phone:
- install/boot: PASS;
- registration/login: FAIL / non-functional;
- local exploration: renders an effectively empty terrain/sky scene rather than the required populated RuinsCiv social world;
- player locomotion: FAIL — camera responds but the character does not provide usable player movement;
- camera UX: FAIL — no acceptable explicit mobile camera/control scheme;
- avatar/rig: FAIL — visible head/rig instability and unacceptable human visual quality;
- world/content visibility: FAIL — social world, community presence, farm, fishing and mission loops are not presented as a retention-ready experience.

The candidate is therefore **REJECTED FOR RELEASE**. Do not upload it to Play and do not treat build/package success as gameplay success.

## Current gates
| Gate | State | Evidence / boundary |
|---|---|---|
| Source recovery / provenance | PASS (retain) | exact SHA `4d009d73...`; do not redo |
| Android API36 / arm64 QA packaging | PASS (retain) | exact SHA `4d009d73...`; QA-only signing boundary |
| Physical install / boot | PASS | physical phone evidence 2026-10-07 |
| Auth usable journey | FAIL | registration/login non-functional |
| Player locomotion / mobile controls | FAIL | character movement unavailable in observed runtime |
| Camera UX | FAIL | camera-only interaction is not acceptable gameplay control |
| Avatar / rig visual | FAIL | unstable/low-quality human presentation |
| World / retention loop | FAIL | empty world; required social/farm/fishing/mission experience not surfaced |
| Production / Play | BLOCKED | rejected runtime; no production signing/release claim |

## Product boundary
RuinsCiv remains the social-world + farm + fishing + missions/community product. Do not import EndCiv combat/LAN requirements as a substitute for repairing RuinsCiv. Do not solve this gate with placeholder geometry, prototype button-only farms, or a speculative second game.

## P0 next task
Trace the recovered RC34-or-better `project.godot` and `native/world/WorldMain.gd` composition to determine why packaged world/avatar assets are not instantiated into the tested runtime and why player locomotion/auth surfaces are unusable. Make the smallest evidence-backed RuinsCiv-only correction on an agent branch, then build one new API36/arm64 QA candidate and require physical A/B evidence.

## Dedup / spend guard
Task key: `RUINSCIV-PHYSICAL-RUNTIME-FAIL+4d009d73ce3031266e5658b8c924178c804c1f1b`.
This task is complete as evidence capture. Never repeat it for the same SHA. No billing, purchase, production signing, Play upload, or release/main merge is authorized by this checkpoint.
