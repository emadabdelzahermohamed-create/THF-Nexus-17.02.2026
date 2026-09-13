# THF Core / Terra / Rift Play SDK Matrix V1 — PASS

Date: 2026-09-13

## Scope
Read-only inspection of the pinned canonical/versioned Android release sources for THF Fit Core, Terra and Rift. The scan verifies archive SHA-256, ZIP integrity, THF/WAVE isolation, source-level references to common Play/ads/analytics SDKs, sensitive Android permissions, and source immutability. It is a technical source inventory only; it does not submit or change any Play Console declaration.

## Execution
- GitHub Actions run: `34728725525`
- Workflow head: `23ecaea2c775a0de1a45832c75fadae5d6b9f614`
- GitHub OIDC/WIF: PASS
- GCP IAP builder execution: PASS
- Canonical source mutation: FALSE
- Production signing: FALSE
- Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana financial action: FALSE

## Source integrity
| App | Pinned source SHA-256 | ZIP integrity | SHA after scan | WAVE isolation |
|---|---|---|---|---|
| Core | `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a` | PASS | unchanged | PASS |
| Terra | `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` | PASS | unchanged | PASS |
| Rift | `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` | PASS | unchanged | PASS |

## SDK / source-reference matrix
All three inspected sources returned `0` references for:
- Google Mobile Ads / AdMob
- Firebase Analytics
- Facebook Audience Network
- AppLovin
- Unity Ads
- Play Integrity client SDK
- Google Play Billing client
- Install Referrer
- Advertising ID (`AD_ID`)
- Google UMP consent SDK

## Permission facts
For Core, Terra and Rift, the scan found:
- Camera permission references: `0`
- Record-audio permission references: `0`
- Fine-location permission references: `0`
- Coarse-location permission references: `0`
- Internet permission references: `1`
- Source AndroidManifest.xml count: `1`

## Interpretation
For these exact pinned sources, no inspected ads/analytics/billing/install-referrer/Advertising-ID/UMP/Play-Integrity client integration is present in source. The current technical evidence therefore supports an ads declaration of "no ads SDK detected in the inspected release sources" and no Advertising-ID permission requirement, subject to final Play Console declaration review and any later provider/configuration changes.

Play Integrity remains a product/configuration decision rather than an already-integrated client dependency in these sources. Do not mark production Play Integrity linkage PASS unless it is intentionally enabled and then verified end-to-end.

## Next safe step
Use this matrix to update the Play release roadmap and prepare the remaining reversible Play Console preflight evidence (store metadata/app-content/content-rating inputs and final Data Safety declaration mapping). Re-run this inventory if any source, dependency, provider, manifest, or production configuration changes.
