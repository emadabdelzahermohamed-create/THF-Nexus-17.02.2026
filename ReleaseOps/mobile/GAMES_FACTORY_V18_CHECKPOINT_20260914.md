# THF Games Factory — V18 checkpoint — 2026-09-14

## Scope reviewed
THF Terra/Nexus World, THF Rift/Nexus Arena, THF Spark, THF Rush, THF Learn Games/Fitness Games, shared avatar/animation systems, and physical-device release truth.

## Start-of-batch authority inspection
The previous authoritative Games physical-device baseline remains V17 (`GAMES_FACTORY_V17_CHECKPOINT_20260914.md`): all six products are NOT_FINAL / PHYSICAL_DEVICE_PENDING and V17 evidence is bound to one exact installed APK/device/Android boot session.

Since V17, authoritative game work introduced a newer Terra RC34 compact phone QA line. The latest pre-batch Terra phone overlay was V3. It used Godot 4.7.2, targetSdk 36, arm64-v8a, MPFB/UAL avatar payload and phone-safe project settings, but its explicit offline mode only spawned the local avatar. Read-only source inspection proved that both `_send_keyboard_input()` and `_update_mobile_input()` returned whenever the websocket was disconnected, so V3 did not provide genuine offline exploration/gameplay.

Rift, Spark, Rush, Learn Games and Fitness Games had no newer game-payload SHA in this batch that invalidated their already-proven gates. Those gates were not rerun merely for repetition.

## V18 engineering completed — Terra RC34 Phone V4
The compact-phone builder was upgraded from visual-only V3 to V4 genuine local exploration.

### Local gameplay wiring
V4 adds an explicit `offline_explore_mode`. Entering the mode:
- clears `THFSessionStore`;
- clears the API token;
- does not establish an authenticated online session;
- marks websocket state disconnected;
- spawns the real local MPFB avatar;
- uses the existing keyboard and touch input cadence;
- routes `_send_step()` to `_apply_offline_step()` only while offline mode is active;
- updates local `target_position` inside the compact QA world bounds;
- therefore drives the already-existing local interpolation, locomotion/UAL animation, grounding/IK and camera path;
- does not synthesize ranked/social/economy/world-authoritative state.

The online branch remains websocket/server-authoritative. V4 does not turn local movement into an online mutation and does not report fake online state.

### Phone constraints and fail-closed build checks
The V4 builder now fails closed unless the staged project has:
- Godot handheld orientation value `4` (sensor-landscape);
- `window/stretch/aspect="expand"`;
- desktop window width/height overrides both `0`;
- right-side touch camera drag support;
- 62x62 minimum movement touch buttons;
- local movement wiring and server-authority branch markers.

The Android export remains targetSdk 36, arm64-v8a and package `com.topherofit.thf.terra.phoneqa`. The `.phoneqa` identity is deliberate: this artifact is QA-only and is not being substituted for a production package.

## Exact V4 build evidence
GitHub Actions run `34861284297`, job `104034509280`, completed SUCCESS on commit `798b6391b5545d949bd72ac2ce70a3ed13bd119b`.

Artifact facts:
- artifact: `THF-TERRA-4.6.8-RC34-PHONE-V4`
- artifact ID: `10355450211`
- uploaded artifact ZIP SHA-256: `8b30603c2bb3f7d5f166d03d298eb7807350c900d5104061d9a9361a1cbdcd02`
- APK: `THF-TERRA-4.6.8-RC34-PHONE-V4.apk`
- APK SHA-256: `e0ac997e1cdb0145b765884d8a59a70403821d1d1e19fbf6a05adcc4640cfbec`
- APK size: `49,657,730` bytes (`under_100MiB=PASS`)
- version: `4.6.8-rc34-phonev4`
- package: `com.topherofit.thf.terra.phoneqa`
- targetSdk: `36`
- engine: `Godot-4.7.2`
- architecture: `arm64-v8a`
- patched world source SHA-256: `19043caa07aa1470f586708b551bbe86249f0f612480657d8891458361e78372`
- project SHA-256: `ce3b4e4e2c08febcdb3d25591ee3163319af828d9c91e4691d3c2c47d02ff182`
- MPFB/UAL avatar asset SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f`
- recorded runtime avatar claim: 137 joints / 195 clips
- backend status: `EPHEMERAL_ENDPOINT_NOT_ACCEPTED_AS_FINAL`
- physical device status: `PENDING`
- final/play ready: `FALSE`

## Parser/import/headless and authority cleanliness
A second independent, non-rebuild gate was added so the exact V4 output is inspected rather than rebuilding an already-proven SHA.

GitHub Actions run `34861680334`, job `104035232270`, completed SUCCESS. It verified:
- V4 exact builder output exists;
- import/export logs contain no `SCRIPT ERROR`, parse/parser error, failed script load, or invalid-call signature;
- local movement helper and both keyboard/touch offline branches are present in the staged source;
- websocket sending still exists only as the online branch;
- phone orientation/aspect/no-desktop-override requirements remain present;
- `THF_TERRA_V4_HEADLESS_CLEAN=PASS`;
- `THF_TERRA_V4_LOCAL_MOVEMENT_WIRED=PASS`;
- `THF_TERRA_V4_SERVER_AUTHORITY_PRESERVED=PASS`;
- `FINAL_OR_PLAY_READY=FALSE`.

## Release truth and blockers
Terra V4 is a materially stronger physical-phone QA candidate, not a production or Play-ready artifact. It has not been promoted into the production candidate registry because its package is explicitly QA-only and its configured public backend is still ephemeral/unacceptable as a final endpoint.

No physical Android device was connected to the available execution environment during this batch. Therefore no install/launch/touch/orientation/background-resume/offline-network/core-gameplay/crash-free/FPS/RAM/thermal claim was manufactured.

Before Terra can be FINAL/PLAY_READY, the exact production-package candidate must still satisfy the V17-or-newer physical-device evidence chain in one coherent device/boot session, including real avatar load, player movement, camera, world/NPC interaction, touch/safe-area/orientation, same-process resume, offline/local/online truth, crash-free logs and performance/thermal observations. Rift still additionally needs real combat state change; Spark/Learn need real learning progression; Rush/Fitness need real sensor events and increasing repetition counts.

No production signing, Play publishing, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite, no-pay-to-win relaxation, or WAVE_MAWJA modification was performed in this batch.
