# THF Apps — Physical Device Acceptance V12 Checkpoint

Date: 2026-09-14
Scope: THF Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault app UX, Signal, Command, THF Pass/shared identity release-control only.
Explicitly excluded: dedicated native game streams and token finance.

## Authoritative truth at this checkpoint

- Production candidate APK/source bytes are unchanged in this batch.
- Same-SHA package/API-36/build gates already proven for those candidates were not repeated.
- The authoritative physical-device registry still contains exactly 10 candidates.
- All 10 candidates remain `PENDING_PHYSICAL_PHONE`.
- `PHYSICAL_DEVICE_PASS=FALSE`.
- `FINAL_OR_PLAY_READY=FALSE`.
- No physical-device evidence was synthesized or inferred from CI.
- No production signing, Play rollout, public deployment, game-stream implementation, or token-finance implementation was performed.

## V12 release-control hardening

V12 layers V11 and prevents cross-reboot/stale-process evidence replay for foreground-sensitive acceptance checks.

Required chain:

1. A distinct SHA-256-bound ADB capture of `/proc/sys/kernel/random/boot_id`.
2. Exact session ID and physical-device fingerprint binding.
3. Capture method exactly `ADB_CAT_PROC_SYS_KERNEL_RANDOM_BOOT_ID` with exit code 0.
4. Exactly one bounded raw stdout payload containing a canonical Android boot UUID.
5. The validator independently SHA-256 hashes the raw canonical UUID and compares it to the declared `boot_id_sha256`.
6. Every registry-active V11 foreground process-provenance record must contain exactly the same boot-ID SHA.
7. Boot evidence cannot alias foreground process evidence.
8. V12 cannot self-promote `FINAL_OR_PLAY_READY`.

This preserves the V11 protections for exact session/package/APK candidate SHA/source SHA/device fingerprint/check/bound evidence SHA, foreground package, positive PID, resumed PID, resumed activity, live process, and capture method.

## Regression coverage added

V12 blocks at minimum:

- missing boot evidence;
- raw boot UUID substitution;
- declared boot hash substitution;
- noncanonical boot UUID text;
- wrong boot capture method;
- failed ADB boot capture;
- process evidence originating from a different boot session;
- duplicate boot-ID markers in process provenance;
- boot/process evidence-file aliasing.

The first PR run exposed a test-fixture scoping bug: the fixture assumed every production foreground check existed in the reduced regression registry. The validator and test harness were corrected to use the registry-active V11 foreground-check set. No release requirement was removed or relaxed.

## GitHub evidence

- PR: #16 `apps: bind physical-device evidence to Android boot session (V12)`.
- PR head after fixes: `7eba1290060c846e6650ff6363c17319e6a790ba`.
- Successful PR V12 run: `34850700010`.
- Merge commit: `1e7c4c6db291d1bcdf6a5875b8726838b138b966`.
- Successful post-merge V12 run: `34850764438`.
- Post-merge V12 job result: compile V2-V12 PASS; complete V2-V12 regressions PASS; V12 release-truth verification PASS.

## Remaining user/external gates

These remain intentionally unpromoted and must be supplied/proven independently before FINAL/PLAY_READY:

- exact-candidate physical Android phone install/launch/touch/layout/orientation/background-resume/offline-network/core-user-journey/crash-free evidence;
- accessibility, Data Saver, RTL and 20-language physical-phone evidence;
- notification permission/channel/receive/tap/deeplink evidence where applicable;
- stable externally reachable trusted-TLS THF Pass/backend health/auth/session/federation proof for network-required flows;
- real FCM/APNs provider credentials behind the approved secret/KMS boundary;
- production signing/Play Console/legal/public-rollout gates where user/account action is required.

Offline claims remain limited to genuinely local behavior; this checkpoint does not authorize fake economy, social, ranked, or server-authoritative state.

## Rollback

If V12 tooling must be rolled back, revert merge commit `1e7c4c6db291d1bcdf6a5875b8726838b138b966`. V11 remains the previous physical-device evidence policy. Candidate APK/source bytes are unaffected by this tooling rollback.
