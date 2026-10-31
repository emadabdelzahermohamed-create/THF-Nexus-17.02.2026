# TopHeroFit physical P0 execution plan — 2026-10-27, at/after 18:00 Cairo

## Purpose and scope

Prepare one safe physical QA pass for `com.topherofit.thf.pulse`. This file is a test plan only; it records no new device observation and claims no PASS.

Read first:
- [RECOVERY_20261023.md](../RECOVERY_20261023.md)
- [FREE_TIER_CONTINUITY_20261026.md](../FREE_TIER_CONTINUITY_20261026.md)
- [PR #119 — physical QA preflight](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/119)
- [PR #118 — snapshot evidence tooling](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/118)

## Release identity gate

The recovery file's 51014 / 51012 values are historical for this later checkpoint. The latest recorded phone observation in PR #119 is Play-installed `51018` (`5.0.0-v2-alpha18`), installer `com.android.vending`, observed 2026-10-27 10:17:49 +03:00. Do not assume that remains newest at test time.

Before physical interaction, obtain the latest independent Android Publisher Internal-track readback and use its exact versionCode as `--expected-version-code`. Record track, status, source SHA/build run and readback timestamp. If no independent readback is available, or the installed version/installer does not match the intended Play-delivered candidate, do not sideload or install; record the mismatch once and stop this device pass.

## One-shot safety preflight — no UI interaction yet

At or after 18:00 Africa/Cairo, run `fitness-v2/scripts/fitness_phone_p0_preflight.sh` once with a new output directory, exact expected version, and the authorized serial only if already known. The script is read-only. It must return `PREFLIGHT_READY` and every gate must pass:

- exactly one intended ADB device, responsive;
- exact package/version and Google Play installer;
- positive keyguard-unlocked signal, awake and interactive;
- `ActivityTrackingService` absent;
- no ongoing/tracking workout notification;
- TopHeroFit not currently resumed into a live workout;
- explicit owner-idle attestation available and truthful.

The `--owner-confirmed-idle` flag is an operator attestation, not a way to bypass uncertainty. Do not set it merely to make the preflight green. If owner-idle cannot be established independently, any gate fails, ADB is offline, multiple devices appear, or the result is ambiguous: **BLOCK, preserve evidence, and do not launch/tap/wake/unlock/connect/retry**. No force-stop, data clear, uninstall, sideload, permission change, or interruption of a pre-existing workout.

## Evidence convention

Use a unique, previously nonexistent output directory for every checkpoint. Use the existing read-only `fitness_phone_p0_snapshot.sh` and supported labels: `stationary-start`, `true-movement`, `navigation`, `background`, `screen-off`, `screen-on`, `reopened`, `process-death`, `explicit-stop`, `daily-steps`, `notification`, `notification-collapsed`, `notification-expanded`, `health-source`.

For each case preserve host and device timestamps, exact installed version and installer, serial/model, screenshot, notification/service/runtime dumps, relevant logcat, GPS accuracy and raw/accepted-point evidence where exposed, and SHA-256 manifest. Record exactly one of PASS / FAIL / BLOCKED with reason. A screenshot or mocked test is not physical sensor evidence.

## P0 order and acceptance

### P0-1 — Stationary start, before movement
For each available mode (walking, running, cycling), begin a controlled test session only after the safety gate passes. Capture a baseline immediately after start, remain physically still for at least 120 seconds, then capture again. Do not simulate GPS or steps.

PASS only if stationary time does not create false distance, steps, non-zero pace/speed, GPS route progress, or unsupported exercise-calorie growth. Record GPS accuracy, raw points and accepted/rejected points if visible in logs; document unavailable telemetry as unavailable, not PASS. End each test session only with the app's explicit Stop action.

### P0-2 — True movement and GPS integrity
Use actual safe outdoor movement and real device location evidence. Capture before/after and route evidence. Compare route shape, measured distance and pace/speed against device/location evidence. Record accuracy, timestamps, raw points and accepted points when observable. FAIL on obvious jumps/drift being accepted, implausible route geometry, or unsupported distance/pace/calorie/step growth. Do not fabricate movement or replay coordinates.

### P0-3 — Same-session lifecycle continuity
Start a controlled session and record its session identity, timer and metrics. Navigate through multiple in-app screens/tabs, Home/background, screen off/on, then reopen. Confirm the same session identity and continuous timer/metrics survive; daily totals/history must not reset. Capture `navigation`, `background`, `screen-off`, `screen-on`, and `reopened` snapshots separately. Stop only via explicit Stop.

### P0-4 — Explicit Stop semantics
Use the explicit in-app Stop control for the controlled test session. Confirm the timer and metric updates cease, the session is finalized once, and the persistent notification is dismissed/updated truthfully. Never use force-stop as a substitute for Stop.

### P0-5 — Daily versus session steps/history
Compare daily steps with session steps before, during and after controlled walking. Navigate away and back; verify daily average/history and today's total remain stable and distinct from the session counter. Do not manually alter step counts.

### P0-6 — Persistent notification
Capture collapsed and expanded states independently. Verify live metrics agree with the active session, elapsed time is truthful, tapping the notification resumes/opens the same session, and Stop performs the explicit stop action. Save each state to its own directory and compare screenshots/dumps.

### P0-7 — Health / wearable eligibility, only if real source data exists
If a compatible wearable or Health Connect source and real records are available, verify source-labelled heart-rate and swimming paths, permissions, data origin/provenance, partial-grant/no-data behavior and deduplication. If hardware or data is absent, mark BLOCKED / NOT AVAILABLE; never invent values or claim PASS.

## Remaining preserved scope after P0

- process-death recovery using a safe OS-observed process-death event only; do not force-stop or kill an active workout to manufacture the event;
- Health Connect baseline permissions and provenance;
- offline exercise motion/mapping and Arabic/English voice guidance;
- crash/ANR and package-scoped logcat review;
- account/session persistence where applicable.

If process death cannot be induced safely without killing/interrupting an active workout, mark that gate BLOCKED and retain the evidence; do not substitute `am force-stop` or data clearing.

## Anti-stall / final report

If the phone is offline or non-interactive, record that once and stop device attempts; continue only independent QA preparation. Do not repeat unchanged PASS gates. Final report must link the exact candidate/readback, preflight directory, per-case evidence directories, screenshots/logs, SHA-256 manifest, and a PASS/FAIL/BLOCKED table. Do not claim Phone PASS or Production PASS from host-only tests, build success, or Play publication alone.
