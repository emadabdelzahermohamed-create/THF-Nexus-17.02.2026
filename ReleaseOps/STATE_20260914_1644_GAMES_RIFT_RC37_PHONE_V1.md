# THF Games Factory — Rift RC37 Phone V1 checkpoint

Date: 2026-09-14
Scope: THF Rift / Nexus Arena phone candidate. Existing PASS gates for unchanged Terra/Spark/Rush/Learn/Fitness candidates were not repeated.

## Authoritative source and candidate

- Canonical source archive SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- Canonical source archive mutated: **false**
- Build workflow run: `34869811923`
- Build job: `104062624099`
- Build result: **SUCCESS**
- Actions artifact ID: `10359190457`
- Actions artifact SHA-256: `7f447d35e4cd6e06f64fd7efbebbd8ac4c6e6cf92d00af4842ffab18faba043d`
- APK: `THF-RIFT-4.7.1-RC37-PHONE-V1.apk`
- APK SHA-256: `8d023174dc30cb7899c21b66e6d7deaca8e16ddd0371f337f589a812c22a8f15`
- APK byte size: `196716096`
- QA package: `com.topherofit.thf.rift.phoneqa`
- Engine: Godot 4.7.2
- targetSdk: 36
- ABI: arm64-v8a
- QA signing only: true
- Production signing: false

## Gameplay and authority changes proven in candidate build

- Genuine local-training state is separate from the online `session` dictionary.
- Starting local training clears online session state and does not call the online session/connect path.
- Local movement drives candidate-local `target_position` from keyboard or touch input.
- Local combat has ammo, target HP, hit count and kill count state; fire/reload/aim/crouch stay local while local training is active.
- Existing online `_act()` path remains WebSocket/HTTP request based and backend-authoritative.
- Ranked/social/economy/world mutation is not performed by local training.
- Terra/Rift mobile constraints in this candidate: sensor-landscape PASS, expandable aspect PASS, desktop window override NONE, touch target minimum Y 62.

## Exact packaged-payload verification

A separate fail-closed exact-artifact gate was added after the build instead of rebuilding an already-PASS source SHA.

- Validator: `ReleaseOps/scripts/validate_rift_rc37_phone_v1_artifact.py`
- CI: `.github/workflows/thf-rift-rc37-phone-v1-exact-artifact-gate.yml`
- Exact-artifact gate run: `34870305440`
- Exact-artifact gate job: `104064280227`
- Result: **SUCCESS**

The gate downloads artifact `10359190457`, requires the exact artifact and APK SHAs above, and rejects substitution. It verifies package/API36/arm64/signature evidence and parser/import/headless logs, then inspects the nested APK bytes for game-specific payload rather than accepting an engine/template APK. Required packaged evidence includes:

- `assets/project.binary`
- compiled `assets/native/arena/ArenaMain.gdc`
- exported Rift arena scene
- MPFB/UAL Stage16A imported avatar scene
- Pistol, Rifle and Shotgun imported combat assets
- arm64 `libgodot_android.so`
- at least 300 packaged `assets/` entries
- no x86/x86_64 ABI in this phone candidate

Observed packaged asset count during independent inspection: **450** entries under `assets/`.

Godot fault scan across import/boot/export evidence found no `SCRIPT ERROR`, parser error, failed-script-load, invalid-call, invalid-get-index or invalid-set-index markers.

## Release truth

- Physical-device status: **PENDING**
- FINAL/PLAY_READY: **FALSE**
- Production cutover: false
- This checkpoint does not promote a source/static/build-only result into a final game.

Before promotion, the exact installed APK bytes must be verified on a physical Android phone under the established V17 boot/session evidence chain. Required evidence remains install/cold launch, touch, orientation/safe-area, same-process background/resume, offline/local/online truth, crash-free logcat, FPS/RAM/thermal, real avatar load, movement, camera and gameplay, plus a real combat state transition for Rift.

No Play publish, production signing, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite, or WAVE_MAWJA mutation was performed in this batch.
