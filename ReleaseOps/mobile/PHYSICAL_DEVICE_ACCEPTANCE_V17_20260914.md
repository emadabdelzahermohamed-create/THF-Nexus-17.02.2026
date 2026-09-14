# THF Games — Physical Device Acceptance V17

Status: fail-closed; non-promotional. V17 does not make any candidate FINAL/PLAY_READY.

## Purpose
V16 proves that each semantic gameplay observation is tied to the resumed foreground package/PID, the same physical-device fingerprint, exact installed candidate APK SHA, current registry SHA, and exact observation timestamp. V17 additionally prevents same-phone cross-reboot evidence mixing.

## Android boot-session rule
For every required gameplay capability process-provenance file, capture the Android/Linux boot UUID using exactly:

`adb -s <serial> shell cat /proc/sys/kernel/random/boot_id`

The proof must contain exactly one canonical UUID and these markers:

- `THF_ANDROID_BOOT_ID=<canonical UUID>`
- `THF_BOOT_ID_CAPTURE_METHOD=ADB_CAT_PROC_BOOT_ID`
- `THF_BOOT_ID_CAPTURE_COMMAND=cat /proc/sys/kernel/random/boot_id`
- `THF_BOOT_ID_CAPTURE_EXIT_CODE=0`

All required capability process proofs for one acceptance bundle must carry the same boot UUID. A device reboot therefore invalidates attempts to combine earlier and later capability process evidence into one accepted phone session; recapture the complete required gameplay-capability process set after reboot.

## Product-specific capability preservation
V17 adds no substitutes for earlier gates. Terra still needs real avatar/player load, movement, camera and world/NPC interaction. Rift needs those plus combat state change. Spark/Learn Games need real learning progression. Rush/Fitness Games need real sensor motion and increasing repetition count. V7–V16 install identity, orientation/touch, background/resume, offline/local/online, crash, performance, semantic gameplay and foreground-process constraints remain required.

## Release truth
- `FINAL_OR_PLAY_READY` must remain `FALSE` until the full exact-candidate physical-phone acceptance chain is present.
- A CI pass of V17 tooling is not a phone acceptance pass.
- Source/static/build-only, wrapper, template-engine, UI-only and placeholder evidence remains invalid.
- Ranked/social/economy/world mutation remains backend-authoritative; local evidence must not fake online state.
