# Fitness Phone QA Preflight Design

## Intent

Protect the owner's Samsung phone and live workout data by making every physical Fitness QA run prove that one authorized device is connected, interactive, unlocked, and not running `ActivityTrackingService` before any mutating QA command is considered.

## Goals

- Perform exactly one `adb devices -l` inventory call and never reconnect or pair.
- Report a stable machine-readable `qa_state` and useful read-only identity details.
- Fail closed for no device, multiple devices, locked/non-interactive state, missing package, or active tracking.
- Permit a later human-controlled QA step only as `READY_FOR_MANUAL_QA`.
- Prove behavior with a fake ADB executable; tests must also prove no mutating command is issued.

## Non-goals and anti-goals

- No install, launch, force-stop, notification interaction, permission change, wake/unlock, input event, screenshot, or data deletion.
- No stale IP/port, `adb connect`, wireless pairing, retry loop, or automatic continuation into QA.
- No Phone PASS or candidate-install claim.

## Constraints

- Package is fixed to `com.topherofit.thf.pulse`.
- The current exact uninstalled candidate remains source `cb425fef23b8541499acb02cecd8b86312b0eb34`, run `40163572486`, artifact `12586864799`, version code `51012`.
- The script must run with Bash and standard Android platform tools only.
- Output must be safe to paste into a QA checkpoint without exposing user data.

## Approaches

1. **Add safety checks to the existing full QA harness.** Rejected because that harness contains install, force-stop, launch, input, and recording actions; a parser defect could cross directly into mutations.
2. **Create a standalone read-only preflight.** Selected because it keeps the safety boundary auditable and requires a separate deliberate action before the existing harness can run.
3. **Use a host-side Python tool.** Rejected because Bash is already the repository convention for ADB QA and avoids adding a runtime dependency on the remote Termux host.

## Interface and state model

`fitness_phone_preflight.sh [--serial SERIAL]` calls the configured `${ADB_BIN:-adb}`. It emits `qa_state=<STATE>` plus serial/package identity when available and exits `0` only for `READY_FOR_MANUAL_QA`.

States: `ADB_OFFLINE`, `MULTIPLE_DEVICES`, `REQUESTED_DEVICE_UNAVAILABLE`, `DEVICE_NOT_INTERACTIVE`, `DEVICE_LOCKED`, `PACKAGE_NOT_INSTALLED`, `ACTIVE_TRACKING_SESSION`, and `READY_FOR_MANUAL_QA`.

## Acceptance

Fake-ADB tests prove one inventory call, correct classification, expected installed version/installer reporting, active-session refusal, and absence of commands containing `connect`, `pair`, `install`, `uninstall`, `force-stop`, `monkey`, `input`, `am start`, `pm clear`, or notification interaction.
