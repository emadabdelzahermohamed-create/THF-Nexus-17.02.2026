# THF Apps — Physical Device Acceptance V11

Status: **NON-PROMOTIONAL GATE / PHYSICAL_DEVICE_PENDING**.

## Material change

Apps V11 now requires SHA-256-bound foreground-process provenance for every foreground-sensitive check activated by the authoritative registry. The provenance must bind the same session, package, exact APK candidate SHA, authoritative source SHA, device fingerprint, canonical evidence SHA and check name.

The capture must prove `THF_FOREGROUND_PACKAGE` equals the authoritative package, use `THF_PROCESS_CAPTURE_METHOD=ADB_DUMPSYS_ACTIVITY_PIDOF`, contain a positive numeric foreground PID, show the same resumed PID, and assert both `THF_ACTIVITY_RESUMED=TRUE` and `THF_PROCESS_ALIVE_AFTER=TRUE`.

Canonical evidence ownership is preserved: semantic checks bind to their semantic observation, touch/responsive/orientation/background-resume bind to the lifecycle transcript, and offline-network binds to the network transcript. Process-provenance files must be separate and SHA-256-bound.

## CI evidence

Final successful workflow: `THF App Physical Device Evidence Tooling V11`, run `34845214934`, head `70f386d9345ee83a536c612f1f7661bfc1a72b1f`.

The workflow compiled V2 through V11, ran the complete regression chain, verified the production registry contains the complete V11 foreground policy set, verified all ten app candidates remain `PENDING_PHYSICAL_PHONE`, and verified `FINAL_OR_PLAY_READY=FALSE`.

Earlier V11 runs in this same repair sequence failed only because the regression fixture assumed all checks used one evidence owner and then collided with an inherited `_refresh` test helper. Those tooling/test defects were repaired without weakening the validator or modifying candidate binaries.

## Release truth

No APK/source candidate bytes changed in this pass, so rebuilding identical candidates is neither necessary nor evidence of additional readiness.

No physical-device install/launch/touch/layout/orientation/background-resume/offline-network/core-journey/crash-free acceptance was fabricated. No signed production AAB, Play approval, production HTTPS/WSS cutover, or production deployment is claimed.

Games V15 remains independently fail-closed and non-promotional. THF and WAVE remain isolated. WAVE canonical release work remains blocked on authorized access to the canonical workspace; SSH/OS Login must not be weakened and an older WAVE source must not be substituted.

## Remaining non-delegable release requirements

A real Android device must execute the exact authoritative candidate sessions. Production signing/Play App Signing/Internal Track requires the authorized signing/Play owner. Legal/store declarations that require owner acceptance remain owner actions. WAVE canonical workspace access requires an authorized OS/admin identity or a service-account-owned release workspace cryptographically bound to the canonical source.

Body SHA-256 (content above this line): `8e5dfe98f5fd8bc3159c7807da36e2a4d6ab41a643009c72358303b357941bc1`
