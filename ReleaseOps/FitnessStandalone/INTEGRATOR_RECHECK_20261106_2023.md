# TopHeroFit integrator recheck — 2026-11-06 20:23 Cairo

Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`
Canonical branch: `agent/codex/fitness-recovery/20261023`
Canonical source head before this evidence-only checkpoint: `ab29ddd333d39581ee6ed7a31a7fccd1ed7343c8`
Android app-source SHA: `5e5374e74f8cbce0eff54c0b5dc37ef860bfe4dc`

## Merged and verified

### GPS + Health provenance — PR #267
- Merge commit: `be251efd890def10781b4b0aaa02c9e058ee3cb6`.
- Tested app-source SHA: `5e5374e74f8cbce0eff54c0b5dc37ef860bfe4dc`.
- Exact-source Android CI: [42262865136](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42262865136), success; product 60, source 33, backend 15, Android unit 151; lint/APK/AAB build succeeded.
- Artifact 13525932102 ZIP SHA-256: `ceff03d2ba048982f911cac575a4e796533e83a0ca0b6fca3eb5fb004185aa7a`; QA APK SHA-256: `88327195ed61dd4f244bad9f395a946a58d4894fddfe3110b87c247ba1fa79a2`; unsigned validation AAB SHA-256: `ee16ae4921e133ec373196fddf0743d8940c8e4ef1005c3f3de27711268c3b3f`.
- Downloaded artifact and recomputed all three digests. The AAB contains no META-INF signature entries and the app Gradle file has no release signing config. It is not a signed release artifact.
- Exact PR-head guard 42266789292 succeeded with Android packaging skipped; size-policy run 42266795888 succeeded. Merge tree equals tested PR head f04fcb4de3744d3f161ce5ac130101ae6aecb699.
- GPS path filtering is conservative; persistent plausible stationary drift remains possible. Physical GPS P0 is not run.

### Server-recorded competitions — PR #269
- Merge commit/current canonical HEAD: `ab29ddd333d39581ee6ed7a31a7fccd1ed7343c8`.
- Exact tested PR head: `b46a92ab6e9797eeaf2631a4d1e10e60d81e677c`; merge tree identical.
- Exact-head backend CI [42267621742](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42267621742) succeeded: compileall and 27 backend unit tests; Android packaging skipped.
- Strength volume only, server-derived from stored non-warmup workout sets. Scores are `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED`; every response sets `rewardEligible=false`.
- Admin creation remains disabled without owner-managed `THF_COMPETITION_ADMIN_KEY`; no events seeded, no deployment or payout path verified.
- Follow-up branch 41defcf is one docs/test commit ahead and one behind canonical, with no associated PR workflow run; not integrated.

## Live Play readback
- Run 41686496926; latest artifact 13527497941 created 2026-11-06T18:07:44Z; probe job 128064256919 succeeded.
- Artifact ZIP SHA-256: `5c486a1e0d91ef1b310b1515f4eb92a1bde0ecb2b299f9f8a70de6aea9b182c1`; embedded JSON SHA-256: `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`.
- Internal 51019 completed; alpha 51007 draft; Production not listed/verified; upload and commit attempts false.
- Existing signed 51019 AAB SHA-256: `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`. No new signed AAB or Play write.

## Current blockers
- Google Maps preflight 41684077962 (2026-11-03): APIs enabled, key inventory permission denied, no key visible, no billing account linked. Native SDK remains blocked; no paid infrastructure.
- Authorized Desktop Commander `localhost` is offline, last seen about 103 hours ago. Last phone observation 2026-11-01T21:24:32Z showed an active/ambiguous tracking session; current state unknown. No ADB/session action. Physical P0 blocked.
- Open priority handoffs: #266 heart-rate identity (11/11 local, no Android CI); #263 GPS anomaly (11/11 local, unwired/no Android CI); #261 swimming eligibility (6/6 local, unwired/no Android CI); #225 daily-step ledger core (no all-day observer/dashboard); #93 Health services; #188/#98 permission/privacy gates. #215 remains draft for Maps SDK/key work; its GPS source is superseded.
- No explicit lease registry found; shared resources are not assumed free.

## Release decision
VersionCode 51020 remains unallocated. The current-source validation AAB is unsigned and not uploaded. Allocate a unique code greater than 51019 only after owner API/key prerequisites, exact-head Android CI and physical P0 pass. Production only after policy/privacy and physical gates. No paid infrastructure.
