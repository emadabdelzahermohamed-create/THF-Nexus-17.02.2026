# Top Hero Fit — GPS, session and Health provenance checkpoint

Date: 2026-11-06 (Africa/Cairo; evidence through 2026-11-06T17:40:13Z)
Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical branch: `agent/codex/fitness-recovery/20261023`
Canonical base observed: `6f230a46d071af3dcd7fb79ef30c13b882620bc5`
Candidate branch: `agent/codex/gps-path-inflation-guard-20261106-r1`
PR: [#267](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/267)
App-source SHA: `5e5374e74f8cbce0eff54c0b5dc37ef860bfe4dc`
PR head before this evidence refresh: `0f7f6063a5526114803f785e55cc198f7b090f36` (workflow-only sync/comment after the tested app-source SHA).

## GPS measurement correction

The candidate combines the accepted-fix GPS path accumulator and Health provenance handoff on the current canonical base.

- Keeps a stable movement anchor while displacement remains inside the reported-accuracy deadband.
- A one-fix displacement excursion is not credited unless it persists on the next accepted fix; a spike that returns inside the deadband is discarded and re-anchored.
- Credited path is bounded by `min(pendingPathDistance, netDisplacement × 1.4)`, preventing oscillating accepted fixes from multiplying small drift into an inflated route.
- Uses the worst observed accuracy radius for the pending path and normalizes longitude across the date line.
- Retains provider/source consistency, accepted-fix distance accounting, pause/callback guards, and accumulator lifecycle resets.

This is conservative measurement filtering, not GPS calibration, spoof-proofing, or physical accuracy proof. Persistent plausible stationary drift can still pass if it remains outside the uncertainty deadband long enough. Physical stationary-drift and real-route tests remain mandatory.

## Exact-source Android CI and artifact evidence

[Candidate workflow run 42262865136](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42262865136) completed successfully on the exact app-source SHA `5e5374e74f8cbce0eff54c0b5dc37ef860bfe4dc`.

- Product tests: 60 passed.
- Source-contract tests: 33 passed.
- Backend tests: 15 passed.
- Android unit tests: 151 passed, 0 failures.
- `:app:lintDebug`, `:app:assembleDebug`, and `:app:bundleRelease`: successful.
- Artifact ID: `13525932102`; ZIP SHA-256 independently recomputed after download: `ceff03d2ba048982f911cac575a4e796533e83a0ca0b6fca3eb5fb004185aa7a`.
- QA APK SHA-256: `88327195ed61dd4f244bad9f395a946a58d4894fddfe3110b87c247ba1fa79a2`.
- Unsigned validation AAB SHA-256: `ee16ae4921e133ec373196fddf0743d8940c8e4ef1005c3f3de27711268c3b3f`.
- Candidate identity: `com.topherofit.thf.pulse.qa`, validation-only versionCode 51019. The AAB is unsigned; no signing or Play upload occurred.

The current PR head at the time of this report had one workflow-only comment commit after the tested app-source SHA. Its guard run [42263966129](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42263966129) passed: `changed-app` succeeded and Android packaging was skipped. No unchanged AAB was rebuilt.

## Health Connect provenance and anti-cheat boundary

The same tested app-source SHA:
- Allow-lists the reviewed Health Connect writer packages `com.google.android.apps.fitness`, `com.sec.android.app.shealth`, and `com.samsung.android.wear.shealth`.
- Requires compatible Health Connect device metadata: phone, watch, fitness band, chest strap, or ring.
- Keeps manual, self-authored, unknown-provider, missing-identity, and incompatible-device evidence out of the trusted reward tier.
- Passes the actual provider package and device type from the Health Connect reader into the evidence policy.

The allowlist identifies the writing app; it is not cryptographic wearable attestation. No Health permission or manifest expansion is included. Health Connect grant/revoke/no-data/error and real wearable physical tests, plus Play Health declaration/privacy reconciliation, remain open.

## Session persistence and truthful metrics

The canonical branch already includes the source-only GPS/session restore integration from PR #264 (merged commit `92462d59a76061b6a445b5e119ec28ca544893af`; exact Android CI run `41681713383` on source SHA `5ce141340282319723a218deafbd1f24eee2b04a`). The current #267 candidate builds on that source. Persistent background/session behavior is still not physically accepted; notifications and restored state must be checked on-device.

The existing daily-step ledger PR #225 remains a core-only handoff: it has prior exact-head validation, but no all-day sensor observer or dashboard wiring. Do not present its core as live daily tracking.

## Google Maps owner gate

Latest recorded preflight remains run `41684077962` (2026-11-03):
- Maps Android Backend and API Keys APIs enabled.
- Release-builder key-inventory permission denied.
- No restricted Maps key visible to the builder.
- No billing account linked.

Native Google Maps SDK rendering and native traffic/transit remain blocked by owner API/key prerequisites. No billing, payment method, key, or paid infrastructure was changed. Continue the attributed free OSM street, OpenTopoMap terrain, EOX 2016 satellite/hybrid layers, and honest Google directions handoff. EOX imagery is 2016, not current.

## Physical P0 and release boundary

Authorized Desktop Commander `localhost` is OFFLINE (last seen 103 hours ago at the 2026-11-06 recheck). The last phone observation remains 2026-11-01T21:24:32Z: Play-installed 51019, foreground tracking service, and an active/ambiguous session. Current phone/session state is unknown. No ADB, install, launch, Stop, session action, or activity-data read was attempted. Physical P0 is BLOCKED_NOT_RUN.

VersionCode 51020 remains unallocated. No new signed AAB exists, no Play listing/track changed, and Production is not verified. Allocate only after owner API/key prerequisites, exact-head Android CI, and physical P0 pass; Production only after policy/privacy and physical gates pass.
