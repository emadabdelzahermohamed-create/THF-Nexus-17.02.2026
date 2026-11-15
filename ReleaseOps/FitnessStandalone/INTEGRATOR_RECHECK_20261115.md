# TopHeroFit integrator recheck — 2026-11-15

## Canonical source and writes

- Repository: emadabdelzahermohamed-create/THF-Nexus-17.02.2026.
- Canonical branch: agent/codex/fitness-recovery/20261023.
- Canonical head before this evidence checkpoint: a8692a06ff93a7bb1b293f9eac986402f3f020c6.
- Canonical application merge PR #296: 1e38da33ba16e9fa6a3276606a1130ff8f95a454.
- This run's only application-branch integration was a force-with-lease rebase of PR #294 onto canonical. No PR was merged.
- A comment-only read-only Play probe trigger was committed; workflow logic was unchanged.
- Evidence docs and release ledger are updated in this checkpoint commit only. No app code, release version, signing config or Play track was changed.

## GPS PR #294

- New head 71364e31f4f631dc2593f38b15a8b92626aacdfe, parent canonical a8692a06ff93a7bb1b293f9eac986402f3f020c6.
- 1 ahead / 0 behind; eight GPS source/test files only; GitHub mergeable=true; Draft.
- Exact-head run 43739798192 SUCCESS: Product 67, source-contract 34, backend 29, Android 270; zero failures/ignored; API 36, lint, assemble and bundle validation PASS.
- Artifact ZIP 2c240ae85e192cea642b85979573e2f1936b9c88a4abb986ac55921d389bff53; QA APK cc1a54f8cfea54fe7651ce70c33e7d92028f9f4bc514c4d55c807b36b2257bce; unsigned AAB f082889f60b80d3103fe1d3d8a419f4d8c7d8711b803b11a05b44b4f9a033f99.
- PR body updated; no merge because physical P0 is not run.

## Historical PR #284

- Current head 274155eafdfff381009ef5814a621f32b225f1a8; 19 ahead / 49 behind; 13-file diff; no current-head CI; mergeable=false.
- Historical run 42694452852 is valid only for 3fcbe6acbb4dc660284c74c8392818996e1de7ee. ZIP ee28619b54c910d640928d9a560e980b00f522782603f4ead109686f25379a1c; APK 08a5730096d1cfc97193e47726f90e533f89d9e0cc3c606faae467b46e72e9b5; unsigned AAB 08d2c80b5da604f6b50a95a7944b6576da87933ee5eec94c2a3944b5274b780e.
- MainActivity.kt on #284 branch is 1,146 lines; motionSnapshot present. The 42694199295 failure was a truncated 1,000-line API read, not proof that the method was absent in the restored current file.

## Health and metrics

- PR #296 merged after exact-head run 43721667918: Product 67, source 34, backend 29, Android 254; ZIP 762540d8b291c1e7b7419130b2decd8c8c6b7c3b3a41183bbeb37f66c09c7659; QA APK e20af5bdcfe34c088bcb5ddba8ba1852b26d36b6281c3614654cd1b2a9b7456a; unsigned AAB 34998ff0a56b601aca328392e31d697d79ca02f7be3922e2ba00d27d6efe89ec.
- Canonical Health Connect allowlist remains five scopes: READ_STEPS, READ_EXERCISE, WRITE_EXERCISE, READ_DISTANCE, READ_ACTIVE_CALORIES_BURNED.
- Swimming presentation now fails closed for phone/ring/chest strap metadata and requires reviewed provider + compatible watch/band + active/automatic recording + stable ID + valid exercise type/time. Not hardware attestation; physical wearable check remains open.
- PR #282 exact head 3291e076510b5626dd8ee931dad84728ba01605d passed 42506335882, but is 2 ahead / 91 behind and shares app.js with #216. The null-vs-zero fix is not merged; canonical app.js still maps missing Health summary metrics to zero.
- PR #93 is 2 ahead / 352 behind, has no exact-head run, and adds 14 extra Health scopes (19 total) beyond canonical five.
- PR #216 is 201 ahead / 207 behind with no exact-head run; stacked exercise/workout UI.
- PR #248 is 4 ahead / 186 behind with no exact-head run; route smoother helper/test only.

## Leases and shared-file holds

No formal lease registry file was found in canonical ReleaseOps/FitnessStandalone or Swarm paths. Shared files are not assumed free:
- ActivityTrackingService/GPS native files: #294; #284 overlaps.
- app.js: #282 and #216; #284 also touches map UI.
- MainActivity/source-contract/manifest: #93; #284 also touches MainActivity.

Comments were added to #284, #93 and #282; #294 body was updated with the exact tested head and release blockers.

## Live Google Play readback

- Read-only probe 43739661313 SUCCESS, observed 2026-11-15 17:11:22 UTC.
- Artifact 14171926791 ZIP SHA-256 81a58281458d9b4137a0a4da0a155a203ae6466f960f112199016286a72b8e38.
- Embedded JSON SHA-256 09e7a346e5e1c893d4328a0894d03c0071e7319bf33516f0423d20105d8f4d63 (full 64-character digest).
- Internal 51019 completed; Alpha 51007 draft; Production not listed/not verified.
- uploadAttempted=false; commitAttempted=false. No Play upload or track mutation occurred.

## Physical P0 and route sync

- Desktop Commander localhost OFFLINE, last seen about 126 hours before the 2026-11-15 19:12 Cairo check; SM-A217F current state unknown. No ADB or session action.
- Physical GPS, screen-off/background, notification controls, process-death, Health grants/revokes, real wearable and swimming checks remain BLOCKED_NOT_RUN.
- ActivityEvidenceAnomalyPolicy.assessSegment remains unwired in ActivityTrackingService; active GPS gates are mock/coordinate/accuracy/freshness/sport-speed plus source-aware distance re-anchoring. No cryptographic location attestation.
- Finished GPS routes remain in WebView localStorage. No authenticated route endpoint or cloud upload. ROUTE_SYNC_DESIGN_20261110.md is design-only.

## Release decision

- Internal 51019 remains the latest independent Play readback.
- Next versionCode 51020 is unallocated.
- Existing signing workflow is pinned to old source 76053bd and versionCode 51019; signing contract requires four upload-key secrets and a Play-bound upload certificate.
- The fresh read-only Play probe proves read access only, not secret availability or upload/write permission.
- No new signed AAB, no signing, no upload, no track commit and no Production promotion.
- Production remains blocked by physical P0 and policy/privacy gates.
- No paid infrastructure, Maps billing/key or unrelated project was used.
