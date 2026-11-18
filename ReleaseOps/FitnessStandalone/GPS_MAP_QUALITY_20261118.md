# TopHeroFit GPS / Maps quality checkpoint — 2026-11-18

## Current canonical status

Canonical application HEAD after #302 merge: \`d2e4c6887fc3b94565536e5d985c193ab8ac1990\`.

### Merged UI correction #302

- Merge commit: \`d2e4c6887fc3b94565536e5d985c193ab8ac1990\`.
- Tested source: \`45b57ceaf218e15e04d8c818a40caa4e1b6376f7\`.
- Exact-head CI run 44361213445: Product 73, source-contract 34, backend 29, Android 275/275, zero failures/ignored; API 36, Kotlin, lint, assembleDebug and bundleRelease validation passed.
- ZIP SHA-256 \`381473a829fc64ead55b27f1264a570ffd1ba7dab1c59b61cc6ac232f7e68095\`; QA APK \`d4a896e436ef185142721ba88ed6c56bd2df4e556f5fe22dd640cf6385af3667\`; unsigned validation AAB \`0f968afa00f68c787bb0751caffbd8857ab56a92451f5fca1ed2d30fac216dfa\`.
- UI behavior: ready Fused/NETWORK fixes are labeled Location rather than GPS; paused is distinct; accepted accuracy is displayed only when finite and positive; Arabic/English copy is explicit. No native service or Play changes.

### Native GPS/session candidate #297 — still Draft

Exact source HEAD \`f741af0dccd48dbcf258f5ae5b1d23e0db58f3af\`; exact-head run 44358671462 SUCCESS:
- Product 69/69; source-contract 34/34; backend 29/29; Android 304/304; zero failures/ignored.
- API 36, Kotlin, lint, assembleDebug and bundleRelease validation PASS.
- Artifact 14452564181 ZIP SHA-256 \`1fe20c29953a629f35d93413473345ae67ddc3414f8b071d335e25701d309609\`.
- QA APK SHA-256 \`d471438d8ce89454a24ab6cd8d8f802ae58c2e270c1ca93f3a01e7478d8cf77f\`.
- Validation AAB SHA-256 \`670d09313a87daf64ffa6dfe2dcd825fc6a7f8e9a7232c6eaf7f73eb93316082\`; unsigned.
- Candidate source is 11 ahead / 2 behind current canonical because it predates the docs checkpoint and #302 UI merge. Its native diff is disjoint from #302, but eventual physical QA must use a fresh branch based on current canonical and exact-head CI so the installed QA APK includes the merged UI fix.
- Keep Draft until physical P0.

### Native source safeguards

- Fused primary; permission-aware fallback to exactly one framework provider.
- GPS provider only when fine permission is granted; coarse-only uses NETWORK_PROVIDER.
- Provider change resets location/accuracy/speed and distance anchor; no cross-provider segment credit.
- Stale, mock, invalid, future, out-of-order, poor-accuracy and implausible fixes are filtered.
- GpsDistanceAccumulator uses an uncertainty deadband, multi-fix confirmation, long-gap re-anchoring and bounded path/net ratio.
- V3 checkpoint retains phase, wall/monotonic clocks, boot identity and bounded route; process downtime is not credited.
- Foreground service, START_STICKY, ongoing notification, Pause/Resume/Finish actions and periodic checkpointing are present in source, not yet physically proven.

## Map architecture

- Leaflet WebView map.
- Attributed OpenStreetMap street tiles.
- OpenTopoMap terrain tiles.
- EOX Sentinel-2 cloudless satellite/hybrid layers.
- OSM tile caching may improve repeat loads but does not provide a complete offline map download.
- No Google Maps SDK, archived Google Maps Rx, billing account, API key or paid infrastructure is required for the selected map stack.

## Historical #284

- Current PR head \`274155eafdfff381009ef5814a621f32b225f1a8\`; 19 ahead / 65 behind canonical; diverged; no exact-head CI.
- Run 42694452852 is historical only and validates SHA \`3fcbe6acbb4dc660284c74c8392818996e1de7ee\`.
- Its ActivityTrackingService/fallback-policy changes overlap #297. Its renderActivity status/pause hunk is superseded by merged #302. MainActivity/Manifest overlap #93.
- Keep Draft. Any remaining map-only work must be isolated after rebase; do not merge the current branch wholesale.

## Remaining GPS P0

Physical device is offline. Last known Samsung SM-A217F / Android 12; last recorded \`location_mode=0\` from 2026-11-09. Current session unknown; preserve. No ADB or device action was attempted.

Required physical tests:
1. 60-second stationary walk/run/cycle: no step/distance drift beyond sensor baseline.
2. Measured outdoor route for walk/run/cycle: compare phone fixes and route to reference distance.
3. Fine-to-coarse permission downgrade and denied permission.
4. First-fix latency, multipath/jump rejection and accuracy-circle honesty.
5. Screen-off/background, app navigation and task removal.
6. Notification Pause/Resume/Finish.
7. Process-death restore without crediting downtime or bridging a route gap.
8. Inspect logs/crash/ANR and ensure no session deletion.

## Anti-cheat / route sync boundaries

- \`ActivityEvidenceAnomalyPolicy.assessSegment()\` is tested but not called by \`ActivityTrackingService\`. Current filters are not full anti-cheat or cryptographic location attestation.
- Completed routes remain local in WebView localStorage. Authenticated workout sync currently carries workout/set metadata only. No route endpoint, cloud backup or restore exists.
- Route sync remains a separate opt-in design requiring precise-location consent, finished-session-only upload, retention, revocation and deletion semantics. It is not the 1-second local map refresh.

No signed AAB, Play upload or physical GPS PASS is claimed.