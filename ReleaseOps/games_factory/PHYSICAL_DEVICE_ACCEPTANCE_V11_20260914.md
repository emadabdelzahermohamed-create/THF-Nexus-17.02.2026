# THF Games Physical Device Acceptance V11 — 2026-09-14

## Purpose
V11 does not declare any game FINAL/PLAY_READY. It defines the additional exact-phone evidence required to prove that offline/local gameplay is real local behavior and that returning online restores transport without silently fabricating ranked/social/economy/world state.

## Prerequisites
- Use the exact APK SHA listed in `THF_GAME_DEVICE_CANDIDATES_V1.json`.
- Use one real Android phone, not an emulator.
- Complete the existing installed-byte, performance, crash/logcat, touch/orientation/safe-area and same-PID lifecycle evidence chain (V7–V10).
- Keep one `session_id` for the entire acceptance session.

## V11 offline/network observation
The evidence bundle must contain `offline_network_observation` with:
- the exact candidate package;
- the same physical-device `session_id`;
- method `adb-shell-connectivity-transition-v1`;
- an observation interval entirely inside the declared phone session;
- `offline_reached=true`;
- `local_mode_stayed_local=true`;
- `no_online_state_faked=true`;
- `online_restored=true`;
- `process_same_pid=true`;
- a non-empty safe-path transcript file and its exact SHA-256.

The transcript must contain the exact package and session identities and exactly one ordered sequence:
1. `THF_STAGE=OFFLINE_CONFIRMED`
2. `THF_STAGE=LOCAL_GAMEPLAY_OBSERVED`
3. `THF_STAGE=ONLINE_RESTORED`

It must also contain exactly one affirmative offline/local/restored marker, exactly one `THF_ONLINE_STATE_FAKED=FALSE`, and matching numeric `THF_NETWORK_PID_BEFORE` / `THF_NETWORK_PID_AFTER` values.

## Product expectations while offline
- Terra: local explore/training may remain local; no local world mutation may masquerade as authoritative shared-world state.
- Rift: local training/combat may remain local; ranked results/rewards must not be fabricated locally.
- Spark / Learn Games: local learning progression may operate locally only where designed; online/shared state must not be forged.
- Rush / Fitness Games: sensor/repetition local modes may operate locally; online competition/reward state must not be forged.

## Restoration expectation
After network restoration the same process must remain alive for this observation. Any authoritative online state must be obtained/reconciled through the backend rather than inferred from a local offline claim.

## Fail-closed rule
Missing, reordered, duplicated, tampered, cross-session, wrong-package, wrong-method, changed-PID or fake-online-state evidence fails V11. V11 never promotes FINAL/PLAY_READY by itself.
