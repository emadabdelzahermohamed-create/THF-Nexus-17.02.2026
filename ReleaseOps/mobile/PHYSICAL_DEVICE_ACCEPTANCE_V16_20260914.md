# THF Games — Physical Device Acceptance V16

Status: **NON-PROMOTIONAL GATE**. Passing V16 does not by itself make any THF game FINAL or PLAY_READY.

## New V16 requirement
V15 proves that semantic gameplay evidence was observed while the expected game package/PID was foreground and resumed. V16 additionally prevents replay or substitution of that process proof across phones, APK candidates, registry revisions, or observation times.

For every required gameplay capability, the SHA-256-bound foreground process provenance file must now also contain and exactly match:

- `THF_DEVICE_FINGERPRINT_SHA256` — the physical phone fingerprint recorded in the evidence bundle.
- `THF_EXACT_APK_SHA256` — the exact candidate APK SHA already proven as installed bytes.
- `THF_REGISTRY_SHA256` — the exact current game candidate registry bytes used for validation.
- `THF_OBSERVED_AT_UTC` — exactly the same UTC timestamp as that capability's manual observation and inside the declared single-device session.
- `THF_ACTIVITY_DUMPSYS_EXIT_CODE=0` and `THF_PIDOF_EXIT_CODE=0` — successful raw process-state capture commands.

All V7–V15 requirements remain mandatory, including exact installed APK identity, single physical-device session, SHA-bound objective/performance/crash/network/gameplay evidence, semantic gameplay markers, foreground/resumed package and PID identity, no fake online state, and genuinely local offline modes.

## Product-specific gameplay remains mandatory
Terra/Nexus World requires real avatar/player load, movement, camera movement and world/NPC interaction. Rift/Nexus Arena requires the same plus a combat action with combat-state change. Spark/Learn Games require increasing learning progression. Rush/Fitness Games require real sensor events and increasing repetition counts. Terra/Rift remain sensor-landscape/expand phone candidates with touch-safe HUD and no desktop-window override.

## Release truth
Until the entire exact-candidate physical-phone chain passes on a real Android phone, release truth remains `FINAL_OR_PLAY_READY=FALSE` and `PHYSICAL_DEVICE_PENDING`. Source/static/build-only evidence, wrappers, template APKs, stale process captures, or evidence from a different device/candidate/registry cannot promote a game.
