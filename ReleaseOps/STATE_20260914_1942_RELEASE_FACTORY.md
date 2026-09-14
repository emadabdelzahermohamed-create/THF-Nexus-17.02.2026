# THF + WAVE Release Factory Checkpoint — 2026-09-14 19:42 EET

Checkpoint body SHA-256: `7987617ec46e8725808b025b50f7b485c7c58b71bb6bc0824b2ca0a5fe82b684`

SHA scope: exact UTF-8 bytes after the `--- BODY ---` marker through the final period, with no trailing newline.

--- BODY ---
Observed release head during this batch:
- Vault/Signal canonical authority checkpoint: 4537c1bb43d13bc2fc36d80c3ba5127750de48f0.
- Later concurrent TokenOps head observed: 4ecbe0e609c45843ac384acd72a81078d0f85142.

Repairs and checkpoints made in this batch:
- Merged PR #23 fail-closed Vault/Signal canonical native source authority at b97cdec134c5c12e5a597882408af0b47b230f16 after its long branch hit Google WIF google.subject >127-byte rejection. The same workflow on main authenticated through WIF without relaxing IAM.
- Vault/Signal workflow run 34869083968 attempt 2 completed SUCCESS after a transient OS Login public-key propagation failure on attempt 1. Authoritative candidate details are recorded by ReleaseOps commit 4537c1bb43d13bc2fc36d80c3ba5127750de48f0.
- Fixed isolated Godot 4.7.2 EditorSettings resource syntax in ReleaseOps/scripts/godot_candidate_tree_apk_v1.sh at commit 6fcf63a0e06bf09e479786a55de5e67dc537a2dd.
- Hardened Rift workflow checkout credentials, added concurrency, and made the shared Godot helper a triggering dependency at commit 004d8631c841d4646b40f1cdd8cc27ef4ca6a7bb.

Rift RC37 Phone V1 evidence:
- Workflow run: 34869811923 = SUCCESS.
- Canonical source SHA-256: 3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914.
- Canonical archive unchanged: true.
- QA package: com.topherofit.thf.rift.phoneqa.
- targetSdk: 36.
- Engine: Godot 4.7.2.
- Arena source SHA-256: 6406f4d1aeed0d9d6cebd000ea916fdd3af66f539feff025b04ee1c85840fd04.
- Project SHA-256: 531dbab39184ba122a53f6df8a25a1029773662f6c7ec7c73f20a9d24fcb458e.
- APK SHA-256: 8d023174dc30cb7899c21b66e6d7deaca8e16ddd0371f337f589a812c22a8f15.
- APK size: 196716096 bytes.
- Artifact ID: 10359190457.
- Artifact ZIP SHA-256: 7f447d35e4cd6e06f64fd7efbebbd8ac4c6e6cf92d00af4842ffab18faba043d.
- Artifact size: 198734324 bytes.
- Sensor landscape setting: PASS.
- Expandable aspect: PASS.
- Desktop window override: NONE.
- Minimum recorded touch target Y: 62.
- MPFB avatar path is embedded in candidate.
- Local training mode: GENUINE_LOCAL_STATE.
- Local online session fabrication: FALSE.
- Local training start backend calls: 0.
- Local movement: TARGET_POSITION_LOCAL_ONLY.
- Local combat: CAMERA_AIM_CONE_TARGET_HP_AMMO_HITS_KILLS.
- Online action authority remains PRESERVED_WEBSOCKET_OR_HTTP_TICK.
- Ranked/social/economy/world local mutation remains DISABLED.
- Placeholder endpoint markers: 0.
- physical_device_status=PENDING.
- final_or_play_ready=FALSE.
- production_signing=false.
- production_cutover=false.

Rift package-size inspection:
- Candidate exceeds 100 MiB and is not acceptable as the requested compact delivery artifact.
- APK inspection shows the largest single payload is lib/arm64-v8a/libgodot_android.so at 76181608 bytes; substantial imported avatar/texture assets make up much of the remainder.
- This is recorded as an optimization/Play-delivery blocker, not hidden by declaring the QA APK final.

Release governance:
- GitHub branch API reported main protected=false and branch protection enforcement disabled during this batch. Owner/admin branch-ruleset protection plus required release checks remains required.
- No branch-protection bypass or administrative mutation was attempted.

WAVE isolation:
- WAVE was not mutated in this batch.
- Latest explicit WAVE RC14 blocker remains CANONICAL_ROOT_OS_LOGIN_REQUIRED: WIF/IAP/VM reachability work, but canonical /root/workspace/wave-mawja requires narrow OS Admin Login or, preferably, a service-account-owned release workspace cryptographically bound to canonical root.
- SSH/OS Login was not weakened and no older WAVE source was substituted.

Mobile Real-Function Release Policy remains fail-closed:
- No physical-device install/launch/touch/layout/orientation/background-resume/offline-network/core-journey/crash-free evidence was fabricated.
- Games still require exact-candidate avatar/player load, movement/camera/gameplay and FPS/RAM/thermal evidence on a physical phone.
- No production-signed AAB, Play approval, stable production HTTPS/WSS, Cloudflare production cutover, or production deployment is claimed.
- Overall release truth remains NOT_FINAL / NO-GO.