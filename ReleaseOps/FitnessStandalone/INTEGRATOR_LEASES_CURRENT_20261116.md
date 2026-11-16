# TopHeroFit Integrator file ownership / lease registry — 2026-11-16

Scope: TopHeroFit only. Repository: `emadabdelzahermohamed-create/THF-Nexus-17.02.2026`.
Canonical branch: `agent/codex/fitness-recovery/20261023`.
Canonical base at registry creation: `fbb63025ef0d6dbfe22c7661b049a4b72da2b5a0`.

## Authority
- The canonical integrator is the sole writer for release/version allocation, canonical workflows, signing configuration, Google Play edits/uploads/track commits and Production promotion.
- All release changes must preserve source SHA -> exact-head tests -> signed AAB -> independent Play Internal readback.
- No versionCode is allocated until owner API/key prerequisites, exact-head Android CI and physical P0 pass. Next code must be greater than 51019; 51020 is not allocated.
- No merge of an untested handoff. No rebuild/reupload of unchanged bytes. No phone/Play/Production PASS without exact artifact SHA and independent readback.

## Active file-level holds
| Surface | Current owner / PR | Hold and integration rule |
|---|---|---|
| `ActivityTrackingService.kt`, `ActivityLocationFallbackPolicy.kt`, `GpsFixGate.kt`, `GpsFixPresentationPolicy.kt` and GPS tests | PR #297, head `1c099845979a998dc0d374322f471c39400e566e` | Sole active native GPS handoff. Exact-head CI 43923207674 PASS. Keep Draft until physical P0. #284 overlaps and must not be merged wholesale. |
| `app.js` and active-workout/session UI | PR #282, #216, #224; #284 also touches map UI | Shared ownership hold. No whole-file overwrite. Reconcile minimal hunks and run combined-head product/source/Android tests. |
| `MainActivity.kt`, `AndroidManifest.xml`, Health rationale strings and Health Services bridge | PR #93 | Health Services owner. Canonical Health Connect allowlist is exactly five scopes; #93 currently requests 19 and is blocked. #284 also touches MainActivity/source-contract. |
| Exercise catalog JSON/JS, catalog builder/manifest/tests | PR #160 | Catalog ownership. 53 ahead / 210 behind; Draft; no native test runner/CI evidence. Coordinate with #213/#224 before any transplant. |
| Program JSON/JS, program builder/manifest and prescription UI | PR #213 | Program/RIR ownership. 190 ahead / 210 behind; Draft; no native Python/CI evidence. Coordinate with #160/#224 and app.js owner. |
| Offline demo runtime and active-workout demo UI | PR #224 | Demo ownership. 153 ahead / 210 behind; Draft; overlaps app.js and catalog/program assets. Compatibility harness is not native Node/Android CI. |
| `ActivityGpsRouteSmoother.kt` and test | PR #248 | Helper/test only, 4 ahead / 189 behind; Draft; not service-integrated and no Android Gradle/JUnit exact-head CI. |
| ReleaseOps, release workflows, signing, versionCode, Play | Canonical integrator only | No parallel PR/agent may allocate a version, change signing/workflow or write Play. Owner API/key prerequisites remain unverified. |

## Current PR register (compare against canonical base at registry creation)
| PR | State | Ahead / behind | Current head | Decision |
|---|---|---:|---|---|
| #297 GPS | Draft | 8 / 0 | `1c099845979a998dc0d374322f471c39400e566e` | Exact-head CI PASS; physical P0 required. |
| #284 Maps/GPS | Draft | 19 / 52 | `274155eafdfff381009ef5814a621f32b225f1a8` | No current-head CI; overlaps #297/#93/#282/#216. |
| #282 Metrics | Draft | 2 / 94 | `3291e076510b5626dd8ee931dad84728ba01605d` | Stale app.js branch; rebase and combined CI after #216 ownership resolution. |
| #93 Health Services | Draft | 2 / 355 | `1cc08cef7dae7f432275fd23960f4390a49db14c` | 19 scopes vs five-scope allowlist; blocked. |
| #216 Workout resume | Draft | 201 / 210 | `1ef915886fdac62c8fe1d5e50505fd354d989ee3` | Stacked/divergent; no exact-head workflow. |
| #160 Arabic catalog | Draft | 53 / 210 | `82e5ca5c2fe796b82cb8d02dbeece3f4b5df125c` | Source assertions only; no native test runner. |
| #213 Timed RIR | Draft | 190 / 210 | `f719214d813f367350d8a10591903d16b68f8da1` | No native Python/CI run; overlaps #160/#224. |
| #224 Offline demos | Draft | 153 / 210 | `cc703baa3cc0e1866e50aafb9a8caad26583fc0a` | Compatibility harness only; no native Node/Android CI. |
| #248 Route smoother | Draft | 4 / 189 | `67d3b438815fe83ced301551aee43f5a6548c91d` | Helper/test only; no Android Gradle/JUnit CI. |
| #294 GPS predecessor | Closed unmerged | — | `71364e31f4f631dc2593f38b15a8b92626aacdfe` | Superseded by #297; do not reopen/merge. |
| #299 Health sport mapping | Merged | — | `ed46cd03e0f71788ded660bd288852a9dca5a63c` | Merged at `16fd1b16ef9d3592ef031298e059ed730ff92f92` after exact-head CI 43881473640. |
| #295 Health provenance | Merged | — | `06ce46526bd01b7a887b736add55451421ce9536` | Merged after exact-head CI 43602214529. |

## Release / device blockers
- SM-A217F / Android 12 last known; Desktop Commander localhost OFFLINE, last seen about 151 hours; current session state unknown. No ADB/session action until reconnect and inspect.
- Physical GPS/session P0 is not run. Source-level CI is not physical acceptance.
- Play latest read-only readback (2026-11-16 17:56:42Z): Internal 51019 Completed, Alpha 51007 Draft, Production not listed/not verified. Upload/commit attempts false.
- Route sync is design-only; no authenticated route endpoint or precise-location upload.
- No paid infrastructure, Maps billing/key or unrelated project.