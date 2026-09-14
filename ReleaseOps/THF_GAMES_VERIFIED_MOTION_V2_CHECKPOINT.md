# THF Games — Verified Motion V2 Checkpoint

Status: **NOT FINAL / PHYSICAL DEVICE PENDING**

## Authoritative lineage used

- THF Terra / Nexus World: latest confirmed Library source line remains RC34. Do not promote historical template/shell APKs that lack exported Godot payload.
- THF Rift / Nexus Arena: authoritative source is **4.7.5-rc41**, source ZIP SHA-256 `29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d`, versionCode `42075`, API 36. RC37/RC38 APK candidates are superseded for latest-source release work. Fresh Godot 4.7.2 / Android test AAB for exact RC41 remains blocked until the exact RC41 artifact bytes are staged to the builder.
- THF Learn Games / Spark: latest currently confirmed phone candidate registry remains RC4. Existing candidate evidence is retained; this batch does not rebuild unchanged bytes.
- THF Motion Games / Rush: latest currently confirmed phone candidate registry remains RC4. Existing candidate evidence is retained; this batch changes the candidate overlay contract only and does **not** claim a new APK SHA.

## New verified-motion boundary

`ReleaseOps/scripts/thf_spark_rush_verified_motion_overlay_v2.py` replaces the old touch-driven Rush repetition behavior for future disposable candidate trees.

For **THF Motion Games** local practice:

- touch/manual activity values cannot increment repetitions;
- repetition progression consumes trusted `DeviceMotionEvent` sensor events only;
- motion vectors must be finite 3-axis values;
- repetition detection uses high/low hysteresis plus a cooldown rather than a single arbitrary sample;
- local practice writes no ranked, social, economy, reward, or server fitness-evidence state;
- any online reward/economy result remains backend-authoritative and is explicitly not implemented by this local overlay;
- the overlay does not claim cryptographic/server-verifiable Health Connect evidence;
- package ID remains `com.topherofit.thf.rush`;
- approved user-facing name is `THF Motion Games`.

For **THF Learn Games** the same overlay family preserves the real local learning loop, package ID `com.topherofit.thf.spark`, and approved user-facing name `THF Learn Games`.

Regression contract:

- `ReleaseOps/scripts/test_spark_rush_verified_motion_overlay_v2.py`
- `.github/workflows/thf-rush-verified-motion-v2.yml`

The regression rejects any touch handler that increments Rush repetitions, missing trusted-event checks, missing finite sensor vectors, missing hysteresis/cooldown, manual activity acceptance, local reward/economy writes, or any promotion to FINAL before physical-device evidence.

## Truth boundary

This checkpoint is an engineering/source-contract checkpoint, not a new installable release. A future exact Rush candidate must apply V2 to the newest authoritative source tree, then pass API 36 package/signature/installability inspection and the existing physical-device evidence chain.

Physical-device acceptance remains mandatory before `FINAL` or `PLAY_READY`: exact installed candidate SHA; install/cold launch; touch/orientation/safe-area; background/resume; offline/local/online truth; crash-free logcat; real game progression; and FPS/RAM/thermal observation. For Motion Games specifically, sensor events and increasing repetitions must be observed on the physical phone.

No production signing, Play publication, Cloudflare production cutover, token/economy mutation, canonical archive overwrite, or WAVE_MAWJA change is part of this checkpoint.
