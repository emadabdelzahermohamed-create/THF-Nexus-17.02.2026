# TopHeroFit — current recovery checkpoint (2026-11-11)

**Repository authority:** `emadabdelzahermohamed-create/THF-Nexus-17.02.2026` only.  
**Canonical branch:** `agent/codex/fitness-recovery/20261023`.  
**Last app-source commit at checkpoint start:** `3b65efa94709e3a60cc62113e19c92639e2a76b9`.  
**Current release decision:** HOLD. No version allocation, signing, Play upload, or Production action.

## Resume from these exact states

- GPS handoff: [PR #284](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/pull/284), current head `be95a73bce584043eaffe17df1c1a99a81251488`, Draft.
- Exact current PR-head CI: [42978310512](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42978310512), PASS (60 product, 40 source-contract, 29 backend, 228 Android; lint/assemble/bundle pass).
- Current PR validation artifact: ZIP SHA-256 `5c601d070f86f01729138eb90d84cf039b64499a73ad90f71541036c226fff5d`; APK SHA-256 `cd665518980fa18d910c7850c4ed602c251d0f0ebff16a399d67551788d65738`; AAB SHA-256 `be085f9f86bb147a88430983944d249254ff9a8cf3e7ad22d03e10e2f1c43239`. AAB is unsigned.
- Current PR compare against canonical app-source head: 15 ahead / 11 behind; merge base `9b5db58e809fa7d5e639bc4ee55df03d100467e8`. Do not merge: `app.js` overlaps #282/#216/exercise handoffs; `MainActivity.kt` is claimed by #93; physical P0 is not run.
- Historical requested run [42694452852](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694452852) was on older head `3fcbe6acbb4dc660284c74c8392818996e1de7ee`; it is not the current exact-head run. Artifact ZIP SHA `ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c`; APK SHA `08a5730096d1cfc97193e47726f90e533f89d9e0cc3c606faae467b46e72e9b5`; unsigned AAB SHA `08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e`; Android tests 223/223.
- Failed run [42694199295](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42694199295) failed the source-contract assertion because the uploaded `MainActivity.kt` ended before `motionSnapshot`. Current PR-head `MainActivity.kt` was read in two chunks: 1,146 lines total, with `motionSnapshot` present.
- Canonical Health dedup source commit `3b65efa94709e3a60cc62113e19c92639e2a76b9` has the same five changed file blobs as tested handoff head `71a2863e51465ad587df8230269c1af4cbdf55d9`. That handoff's exact-head run [43028123167](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/43028123167) passed 60 product / 34 source-contract / 29 backend / 232 Android tests. Artifact ZIP SHA `d39b8dbf445b631d15486c817bbd0a2d67a73c186197eaeb7cb2a350b81204a7`; unsigned AAB SHA `d6e61704062f2dcc50fa8a79e0c407c47b9bef8bde8c099d26e0bf8f381d6d3e`. Canonical run 430293 succeeded at workflow level but skipped Android build due the workflow's canonical-branch exclusion; do not claim exact-commit CI on 3b65.
- Route sync remains design-only in [ROUTE_SYNC_DESIGN_20261110.md](ROUTE_SYNC_DESIGN_20261110.md). `persistFinishedActivity()` stores route points locally in `pulse.v2.activities`; no authenticated route-upload endpoint exists in the current backend contracts.
- Latest successful Play readback: [42405709027, attempt 4](https://github.com/emadabdelzahermohamed-create/THF-Nexus-17.02.2026/actions/runs/42405709027), observed 2026-11-10 18:31:07 UTC. Artifact ZIP SHA `bffbb6484802331c90f7b49ba029ab373f63cc2f13d94d10b980907008e775ee`, embedded JSON SHA `09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63`; both reverified on 2026-11-11.
- Play readback: Internal 51019 completed; Alpha 51007 draft; Production not listed/not verified. No newer successful readback. No upload/commit attempt.
- Existing Internal 51019 release record: source `76053bd9127c38d8065eb7ac250bdeb34ab67854`, signed AAB SHA `5dc7d0077ecfddd3224ca8557a3b4f6d0a5524cf194c0e547fc8b1605c7ba9c5`. Its original build artifact is no longer retrievable for fresh hash recomputation; independent Play readback remains available.
- Next versionCode 51020 is **not allocated**. No new signed AAB exists.

## Device hold

Desktop Commander `localhost` is Offline, last seen about 31 hours before this checkpoint. Last recorded device-wide `location_mode=0` was 2026-11-09; app fine/coarse permissions were historically granted. No setting was changed and no ADB/session action was attempted. Preserve the unknown phone/session state until the device reconnects.

## Current release gates

- GPS and background P0: NOT RUN.
- Shared-file ownership reconciliation: NOT DONE.
- Health physical provenance / Play declaration / Data Safety: NOT DONE.
- Competition admin key, event seed, independent deployment and physical anti-cheat validation: NOT DONE; rewards remain ineligible.
- Route sync implementation and deletion/retention tests: NOT DONE.
- Owner-controlled release API/signing prerequisites: NOT VERIFIED.
- VersionCode 51020 allocation, signing, Internal upload: NOT AUTHORIZED YET.
- Production: NOT VERIFIED.

See [INTEGRATOR_RECHECK_20261111.md](INTEGRATOR_RECHECK_20261111.md) and [GPS_MAP_QUALITY_20261111.md](GPS_MAP_QUALITY_20261111.md) for the full evidence ledger.
