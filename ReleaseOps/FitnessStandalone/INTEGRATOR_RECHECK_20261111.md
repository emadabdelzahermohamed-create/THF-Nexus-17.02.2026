# TopHeroFit integrator recheck — 2026-11-11 19:46 Africa/Cairo

Scope: **TopHeroFit only**. Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`. Canonical branch: `agent/codex/fitness-recovery/20261023`.

## Executive state

- Last app-source commit on the canonical branch at the start of this recheck: `3b65efa94709e3a60cc62113e19c92639e2a76b9`.
- GPS handoff PR [#284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284) remains **Draft / open / unmerged**.
- Current PR head: `be95a73bce584043eaffe17df1c1a99a81251488`.
- Exact current PR-head Android CI: [42978310512](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42978310512), success.
- Physical P0 remains **BLOCKED / NOT RUN** because Desktop Commander device `localhost` is offline (last seen 31 hours before this check).
- Latest successful Play state readback remains [42405709027, attempt 4](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), observed 2026-11-10 18:31:07 UTC. No newer successful publication-state probe exists.
- Internal 51019 is completed; Alpha 51007 is draft; Production is not verified. No Play write occurred in this recheck.
- Next versionCode 51020 remains **unallocated**. No signing, upload, promotion, or Production action occurred.

## 1. GPS / Maps — PR #284

### Current exact-head evidence

PR #284 current head is `be95a73bce584043eaffe17df1c1a99a81251488`. The app/test implementation commit is `fdbdd0588222ba366e56767e3b21de66c3f0d829`; the later `be95a73...` commit only synchronizes the recovery document. Run 42978310512 tested the exact current PR head.

- Product tests: **60/60**
- Source-contract tests: **40/40**
- Backend tests: **29/29**
- Android Gradle unit tests: **228/228**, 0 failures, 0 ignored
- Android API 36 setup, `:app:testDebugUnitTest`, `:app:lintDebug`, `:app:assembleDebug`, `:app:bundleRelease`: PASS
- Artifact ID: `13836587093`
- Artifact ZIP SHA-256: `5c601d070f86f01729138eb90d84cf039b64499a73ad90f71541036c226fff5d`
- QA APK SHA-256: `cd6655f3e58bfa4d9d4c8b2d42a1f30b2a77d5fef0f8eacac6e8c5d8f8a7f7a1`
- Validation AAB SHA-256: `be085f9f86bb147a88430983944d249254ff9a8cf3e7ad22d03e10e2f1c43239`
- AAB verification: **unsigned**. This is validation output, not a Play artifact.
- The AAB bytes match the earlier source-head run 42976730277; no new signing or upload is justified.

The user-requested checkpoint run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) was successful on the then-head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`, not the current PR head:

- Android unit tests: 223/223, 0 failures, 0 ignored
- Artifact ID `13707718861`, ZIP SHA-256 `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`
- APK SHA-256 `08a573... (historical artifact; see artifact report)`
- AAB SHA-256 `08d2c80... (historical artifact; unsigned)`

The earlier [42694199295](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694199295) failed one source-contract test because its uploaded `MainActivity.kt` ended before `motionSnapshot`. The current PR-head file was read in two chunks (999 + 147 lines): **1,146 lines total**, and `motionSnapshot` is present in the second chunk. The truncation failure is superseded by the later passing runs.

### Implementation scope

PR #284 contains the Fused-to-framework fallback watchdog (8-second initial and 12-second stale-fix thresholds), permission-aware single-provider selection (GPS with fine permission, network with coarse-only permission), Fused shutdown after fallback registration, callback/generation guards against late tasks, truthful GPS accuracy/pause state, explicit Android Location Settings handoff when device-wide location is off, unique TopHeroFit User-Agent, and OSM-derived raster caching.

Current map choice remains Leaflet in WebView with OpenStreetMap streets, OpenTopoMap terrain, and EOX Sentinel-2 imagery. The current stack does **not** require Google Maps SDK, billing, or a Maps key. No archived Google Maps Rx code or paid Maps dependency was added.

### Rebase and merge boundary

The current canonical branch head is `3b65efa94709e3a60cc62113e19c92639e2a76b9`. A fresh compare against PR #284 reports **15 commits ahead / 11 behind**, merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`. GitHub reports mergeable=true, but the PR body still contains stale base/behind counts. It remains Draft.

Do not merge yet:
- `app.js` overlaps PR #282, PR #216, and several exercise UX/demo handoffs.
- `MainActivity.kt` overlaps the active file-ownership claim in PR #93.
- PR #93 also changes source-contract coverage and has no exact-head Android CI.
- Physical P0 has not run.

## 2. Canonical Health record deduplication

Canonical app-source commit `3b65efa94709e3a60cc62113e19c92639e2a76b9` adds source-scoped latest-version Health record aggregation. The same five changed file blobs were compared against tested handoff head `71a2863e51465ad587df8230269c1af4cbdf55d9` and match:

- `HealthConnectRepository.kt`: `618836257a2650acb746954fd9bb0566827759f4`
- `HealthRecordDeduplicationPolicy.kt`: `f9ee3968a26cc9e12e705a8e45e61f9421e8a7de`
- `HealthRecordEvidencePolicy.kt`: `eda76e6eb2cbb6ffebb8a812209cca8322de3237`
- `HealthConnectProvenanceTest.kt`: `d90f428a5a0c6a2f6bf767deea0e8160f2171e3f`
- `HealthRecordDeduplicationPolicyTest.kt`: `216e459e7186e3993b45a309fe2c97bd553f46fa`

The tree-equivalent handoff head had exact-head CI [43028123167](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43028123167): product 60/60, source-contract 34/34, backend 29/29, Android 232/232, lint/assemble/bundle PASS. Artifact ID `13860436298`; ZIP SHA-256 `d39b8dbf445b631d15486c817bbd0a2d67a73c186197eaeb7cb2a350b81204a7`; AAB SHA-256 `d6e61704062f2dcc50fa8a79e0c407c47b9bef8bde8c099d26e0bf8f381d6d3e`; AAB is unsigned.

Important limitation: canonical push run [43029368869](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43029368869) completed at workflow level but its `deterministic-build` job was skipped because the workflow explicitly excludes pushes to the canonical recovery branch. The tested handoff tree matches the five canonical Health file blobs, but there is **no Android build run on commit SHA 3b65 itself**. Do not describe 3b65 as exact-commit CI PASS. No Health handoff was merged during this recheck.

## 3. Current PRs and ownership holds

| PR | Current status | Integrator decision |
|---|---|---|
| #284 | Draft; exact current-head CI pass; physical P0 missing | Keep Draft |
| #93 | Draft; active `MainActivity.kt` ownership claim; no exact-head Android CI | Treat claimed files as held |
| #282 | Draft; Health null-vs-zero UI; exact CI is on old base; overlaps `app.js` | Hold for combined-head CI |
| #216 | Open; workout resume protection; no exact-head Android CI; overlaps `app.js` | Hold |
| #248 | Draft; display-only route smoother; local stub tests only, no Android Gradle CI | Do not integrate |
| #188 | Draft; Health permission-scope guard; exact CI and Play declaration review pending | Hold |

Other open exercise/demo handoffs also share `app.js` (including #224, #247, #249, #250, #251, #253, #254, #256, #258, #259, #260, #244, #252, #255 and #257). Do not infer disjointness from a PR's small diff.

No formal lease registry file was found. PR #93's explicit MainActivity ownership statement is treated as a file-level hold. Shared files are not assumed free.

## 4. Device and physical P0

Desktop Commander reports `localhost` **Offline**, last seen about 31 hours before this check. Last known device identity: Samsung SM-A217F / Android 12. Historical app fine/coarse permissions were granted; the last recorded device-wide `location_mode=0` was from 2026-11-09. This setting was not changed.

No ADB install, launch, session stop, settings change, or live-session inspection was attempted. Preserve the unknown phone/session state.

Physical P0 remains NOT RUN: stationary drift, measured outdoor route, coarse-only network fallback, first-fix latency, jump/multipath rejection, pause/resume/finish, screen-off/background notification, process-death recovery, and daily-vs-session step separation.

## 5. Health, anti-cheat, and competitions

- Health Connect dedup now selects the newest source-scoped record version and keeps evidence/trust aligned with metric aggregation. Missing permission must remain unavailable; a permitted read with no records may be true zero.
- Health provenance and wearable/sport metadata are not cryptographic device attestation. No physical watch proof or real swimming session was validated.
- PR #285's swimming provenance gate is merged, but eligibility remains constrained to source/device evidence and does not establish cryptographic trust.
- Competition backend code is server-recorded only. The admin key is not configured, no event is seeded, independent deployment is not verified, and all scores remain `SERVER_RECORDED_NOT_PHYSICALLY_VERIFIED` with `rewardEligible=false`. No reward or payout claim is permitted.

## 6. Route backup/sync contract recheck — design only

Current WebView completion code `persistFinishedActivity()` writes route points into `pulse.v2.activities` localStorage (bounded local history); it does not upload GPS. The one-second map refresh is local presentation only.

The current Python backend OpenAPI exposes workout sync/history/progress and competition routes, but no activity-route endpoint. Its bearer-token verifier uses the existing account token issuer/audience/key ring; the server derives the account from the verified token. The AppDeploy adapter `android_v2_routes.ts` likewise has a strict workout allowlist and resource kinds limited to ticket/session/idempotency/workout-index; no route table or route endpoint exists, and the account-deletion helper does not yet delete route resources.

Existing design: [ROUTE_SYNC_DESIGN_20261110.md](ROUTE_SYNC_DESIGN_20261110.md). It remains **DESIGN ONLY**: account-level summary opt-in, separate precise-route opt-in, per-session opt-in, finished-session-only uploads, no active location stream, explicit retention/deletion/revocation, and no precise-location upload by default. No route sync code or cloud GPS upload was added.

## 7. Play and release chain

Latest successful read-only Play readback: run 42405709027, attempt 4, observed 2026-11-10 18:31:07 UTC. Artifact ID `13791872061`; ZIP SHA-256 `bffbb6484802331c90f7b49ba029ab373f63cc2f13d94d10b980907008e775ee`; embedded JSON SHA-256 `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`. Both were recomputed/verified in this recheck.

Readback: Internal 51019 completed; Alpha 51007 draft; Production not listed/not verified. Upload and commit attempts were false. No newer successful probe exists.

The canonical release record associates Internal 51019 with source `76053bd9127c38d8065eb7ac250bdeb34ab67854` and signed AAB SHA-256 `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`. The original build artifact is no longer retrievable for fresh recomputation; the independent Play readback still confirms the track/version state. New GPS/Health validation AABs are unsigned and are not Play artifacts.

VersionCode 51020 remains unallocated. No new signed AAB, upload, commit, or Production action occurred. Production remains NOT VERIFIED. Owner-controlled release API/signing prerequisites, exact final-source CI, physical P0, policy/privacy and listing-truthfulness gates remain mandatory. Maps SDK billing/key is not a prerequisite for the selected OSM stack.

## Next safe actions

1. Keep #284 Draft. Reconcile the shared `app.js` and `MainActivity.kt` handoffs before any rebase/merge.
2. When the device reconnects, inspect the current session state first; do not stop or replace an unknown active session. Then run physical GPS/background P0.
3. Keep route backup design-only until consent, backend endpoint, account deletion, retention and cross-account tests are implemented and validated.
4. Keep Health/wearable and competition rewards ineligible until physical provenance, owner keys, deployment, privacy and anti-cheat gates pass.
5. Do not allocate 51020, sign, upload or promote until all owner/API/key, exact-head, physical and policy gates pass.
