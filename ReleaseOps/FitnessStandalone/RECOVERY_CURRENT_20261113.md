# TopHeroFit recovery checkpoint — 2026-11-13

Scope: **TopHeroFit only**. Source of truth: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.

## Canonical starting point and latest source

- Canonical branch: `agent/codex/fitness-recovery/20261023`.
- Canonical application merge commit: `778f159402902549983142c83151a09745f624cc` (PR #293).
- Latest documentation/checkpoint commit: `82c29ba9d49b2e3e46d35c74f60a37359b1e3db9` before this ownership-safe checkpoint.
- Prior recovery: [RECOVERY_CURRENT_20261112.md](RECOVERY_CURRENT_20261112.md).
- Latest GPS candidate report: [GPS_MAP_QUALITY_20261113.md](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/blob/agent/codex/gps-fallback-resilience-20261113-r2/ReleaseOps/FitnessStandalone/GPS_MAP_QUALITY_20261113.md). This is GPS-owner evidence on PR #292, not a canonical physical-device pass.

## Health provenance — merged

- PR [#293](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/293) merged at `778f159402902549983142c83151a09745f624cc`.
- Tested exact head: `d69e969404f728f8666eedbf4d3c9ad08104b60e`.
- Exact-head Android CI [43438628557](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43438628557): SUCCESS.
- Product 67/67, source-contract 34/34, backend 29/29; Android unit tests, lint, assembleDebug and bundleRelease passed.
- QA APK SHA-256: `e6287984b4b869ac689fd49958cd7b9f7f63dbe094c20fccc3e25b940102dc47`.
- Unsigned validation AAB SHA-256: `de4e22f442b8d9ebe8cf0a3deb2ecc94f2ff62ba943485ca8fa121639de0cab2`.
- Artifact ZIP SHA-256: `4aed8a0bbf9c57b3f4e2a5069c13b75776c4bba158a8975696ad6986e3b3d44d`, artifact ID `14044676485`.

Canonical provenance files:
- `HealthConnectRepository.kt`: `dd65d53a70a8287014666d3759b0f4bab98aa152`.
- `HealthRecordProvenancePresentationPolicy.kt`: `ceba7bd93637c4acd83d7f0dd6d68cf666aa9e6d`.
- `HealthRecordProvenancePresentationPolicyTest.kt`: `f595c43f5073c7da39de8011a1f6ed499836b91c`.

The public `HealthSnapshot.recordProvenance` projection contains source package, stable record type, recording method, device class, integrity class, reward decision and constrained reason. Raw provider/client IDs and manufacturer/model are omitted. Its deterministic pseudonymous key is for UI/list reconciliation only, not anonymization, hardware attestation or authorization. Unknown types remain reward-ineligible; presentation cannot upgrade repository evidence.

## Health permission and integration gates

Canonical manifest blob: `0969cdb2f18775f23e0870bf754612a04376895f`. Exactly five Health permissions remain:
- `READ_STEPS`
- `READ_EXERCISE`
- `WRITE_EXERCISE`
- `READ_DISTANCE`
- `READ_ACTIVE_CALORIES_BURNED`

`READ_HEART_RATE` remains absent.

PR [#93](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/93) still owns Health service/manifest/rationale and MainActivity/WebView bridge files. Its manifest blob `a3b24f09e6b0c8a67b0fee3e7578317cfe979092` declares 19 scopes, including 14 deferred scopes. It remains Draft, diverged and unmergeable; merged PR #188's exact-five allowlist rejects it. No extra scope is authorized. PR #93 must rebase, keep five scopes and consume #293's summary without raw IDs.

The phone↔Health walking/running/cycling reconciliation policy remains unconnected to `HealthConnectRepository.readRecent()`. Same-source records deduplicate; nearby independent same-source sessions remain separate; swimming never time-deduplicates without stable identity.

## GPS and anti-cheat — separate owner

- PR [#292](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/292), branch `agent/codex/gps-fallback-resilience-20261113-r2`.
- Current branch HEAD: `de304b6f4baa44dc80b3245493d7275fe39f00fe`.
- Tested application/test SHA: `cb97dc0b66299825e6a02dd91ec53e369667bb74`.
- Exact-source Android CI [43382459916](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43382459916): SUCCESS; Product 67/67, source-contract 34/34, backend 29/29, Android 250/250; lint, assembleDebug and bundleRelease passed.
- Candidate provides bounded provider fallback/backoff, coarse-only NETWORK selection, generation-scoped callbacks and truthful accuracy. It is not merged. Its source and tests remain GPS-owner files; this lane did not edit them.
- Physical stationary-drift, measured-route, screen-off/background, notification, process-death and live-session P0 remain BLOCKED_NOT_RUN. Authorized device is offline; current session state unknown. Do not install, launch, stop or alter the phone until safely idle.
- Canonical anomaly policy/tests exist, but live accepted GPS fixes are not yet passed through the policy. GPS owner must supply actual raw Android Location provider, elapsedRealtimeNanos, coordinates, horizontal accuracy and OS mock flag before distance/pace/competition credit. No display-smoothed evidence.

## Exercise content, programs and offline motion

- Canonical catalog: 112 exercises; 84 Arabic/English step-count mismatches.
- PR #160 reduces count mismatches to zero but is 53 ahead / 180 behind and has two semantic mapping defects: Step-up with Knee Raise uses squat cues; Medicine Ball Scoop Throw uses hinge/deadlift cues. No exact-head CI.
- Canonical programs: 26 programs / 94 sessions / 470 references.
- PR #213 is 190 ahead / 180 behind, spans 49 files and has no exact-head CI. It removes timed RIR but leaves six 30-second Superman program holds mismatched to a repetition-based catalog entry.
- Offline media inventory: five videos, two reviewed 16-frame sequences, 105 two-frame reference-only exercises. Merged #289 protects mappings, local asset hashes and license attribution; no new clips were added.

## Release and physical gates

Play Health declaration/privacy/Data Safety reconciliation, physical Health grant/revoke/no-data/error checks, actual wearable/swimming verification and GPS physical P0 remain hard gates. No Play upload, release version allocation, signing, workflow change, billing or paid service occurred.

## Next safe order

1. Rebase PR #93 onto canonical, restore the five-scope permission allowlist, and integrate the merged per-record provenance contract through its owned bridge.
2. Connect phone-session evidence to walking/running/cycling reconciliation without editing GPS acquisition.
3. Port bilingual catalog and timed-program corrections onto canonical with semantic tests and exact-head CI.
4. Expand genuinely licensed full-motion clips with exact exercise-ID mapping.
5. Preserve physical Health/wearable/GPS and Play privacy gates until actual evidence exists.
