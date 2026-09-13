# THF Core / Terra / Rift — Play Store Asset Inventory V1

Date: 2026-09-13
Status: PASS-INVENTORY / REMEDIATION-REQUIRED
Workflow run: 34731264723
Workflow commit: d297917c229f413d1c9cd6d492706a7fbcf55e4c
Execution path: GitHub OIDC/WIF -> GCP -> IAP -> thf-wave-builder

## Safety / isolation
- Read-only inspection only.
- Canonical archives were not extracted persistently, overwritten, deleted, signed, uploaded to Play, or modified.
- WAVE_MAWJA isolation: PASS for all three THF archives.
- Production signing: NOT PERFORMED.
- Google Play upload/publish: NOT PERFORMED.
- Cloudflare production cutover: NOT PERFORMED.
- Solana financial action: NOT PERFORMED.

## Pinned source verification

| App | Pinned source SHA-256 | ZIP integrity | SHA unchanged after |
|---|---|---|---|
| Core RC6 | `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a` | PASS | PASS |
| Terra RC34 | `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` | PASS | PASS |
| Rift RC37 | `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` | PASS | PASS |

## Inventory result

| App | Launcher icon candidates | Feature graphic candidates | Screenshot candidates | Store/marketing image candidates | strings.xml | AndroidManifest.xml |
|---|---:|---:|---:|---:|---:|---:|
| Core | 0 | 0 | 0 | 0 | 20 | 1 |
| Terra | 1 | 0 | 0 | 0 | 0 | 1 |
| Rift | 1 | 0 | 0 | 0 | 0 | 1 |

Detected launcher icon paths:
- Terra: `android/app/src/main/res/mipmap-mdpi/ic_launcher.png`
- Rift: `THF_Nexus_Arena_Core/android-arena/app/src/main/res/mipmap-mdpi/ic_launcher.png`

## Release interpretation

The inventory workflow itself is PASS. Store-asset readiness is NOT PASS.

Current blockers:
1. Core canonical RC6 has no detected launcher/app-icon image candidate.
2. Core, Terra and Rift have no detected Play feature graphic candidate.
3. Core, Terra and Rift have no detected Play screenshot candidate.
4. Terra and Rift have one launcher icon candidate each, but this inventory did not claim that those files satisfy Play Store listing icon dimensions/format; that requires a dedicated image-dimension/format gate.
5. Store listing graphics must accurately represent current app behavior and must not be fabricated from unrelated UI.

Current Google Play Help requirements checked on 2026-09-13:
- Feature graphic: JPEG or 24-bit PNG without alpha, 1024 x 500 px.
- Store listing screenshots: minimum two across device types; JPEG or 24-bit PNG without alpha; minimum dimension 320 px and maximum dimension 3840 px, with the maximum dimension no more than 2x the minimum dimension.
- Google recommends screenshots between 1080 and 7680 px for promotional eligibility, subject to the detailed current Play guidance.

Official reference: Play Console Help — Add preview assets to showcase your app (`support.google.com/googleplay/android-developer/answer/9866151`).

## Highest-priority next reversible gate

Run a read-only brand/store-asset source discovery across the THF release workspace and repository, preserving strict WAVE isolation, to determine whether compliant THF-owned logo/icon masters and genuine current-version screenshots already exist outside the three canonical archives. Verify SHA-256 for every selected source before any derivative asset work. Do not synthesize or publish store graphics until the source provenance and current-version UI match are established.
