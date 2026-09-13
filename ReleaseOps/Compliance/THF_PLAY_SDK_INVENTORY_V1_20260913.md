# THF Play SDK Inventory V1 — PASS

Date: 2026-09-13

## Scope
Read-only inspection of the versioned permission-minimized Android release-source candidate. This is a technical source inventory, not a Play Console declaration and not a claim about uninspected app variants.

## Candidate integrity
- Path class: versioned THF release candidate, isolated from WAVE.
- Expected SHA-256: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7`
- SHA-256 before: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7`
- SHA-256 after: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7`
- Source mutation: FALSE

## Execution
- GitHub Actions run: `34728616630`
- Workflow head: `94a947a1bf87677944e6cd9316c956b8bb837962`
- GitHub OIDC/WIF: PASS
- GCP IAP builder execution: PASS
- Manifest XML parse: PASS
- THF/WAVE isolation: PASS

## Manifest fact
Declared permissions count: `1`

- `android.permission.INTERNET`

No Camera, Microphone, Fine Location, Coarse Location or AD_ID permission was declared in this inspected candidate.

## Source-reference inventory
The read-only source scan returned zero references for each of the following categories:

- Google Mobile Ads / AdMob: `0`
- Firebase Analytics: `0`
- Facebook Audience Network: `0`
- AppLovin: `0`
- Unity Ads: `0`
- Play Integrity client SDK: `0`
- Google Play Billing client: `0`
- Install Referrer: `0`
- Advertising ID (`AD_ID`): `0`
- Google UMP consent SDK: `0`

## Interpretation
For this exact versioned candidate, no inspected advertising, analytics, Play Integrity, billing, install-referrer, Advertising ID, or UMP client SDK integration is present in source. Do not extrapolate this result to Core/Terra/Rift variants until each canonical/versioned source is inspected independently.

## Safety evidence
- Production signing performed: FALSE
- Play upload performed: FALSE
- Cloudflare production cutover performed: FALSE
- Solana financial action performed: FALSE
- Canonical source overwrite: FALSE
- WAVE touched: FALSE

## Next safe step
Run the same read-only SDK/manifest inventory independently against the pinned Core, Terra and Rift release sources, verifying each declared SHA-256 first. Then use the per-app matrix to narrow Ads declaration, Data Safety and Play Integrity blockers without changing production configuration.
