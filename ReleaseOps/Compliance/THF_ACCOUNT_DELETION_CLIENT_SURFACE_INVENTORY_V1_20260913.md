# THF Account Deletion Client Surface Inventory V1

Status: **PASS-WITH-FINDING**

## Evidence
- GitHub Actions run: `34721700255`
- Workflow commit: `37a5830b89b3ceac6ba37f6e296a508fc75f03d3`
- Canonical source archive: `THF_NEXUS_6_FINAL_SOURCE_20260829.zip`
- Canonical archive SHA-256 verified: `8c060bdb7776ccf485b6294cda513a75b0fd3be28d43a416431d1368260a4884`
- GitHub OIDC/WIF -> GCP -> IAP: PASS
- THF/WAVE source isolation: PASS

## Finding
A source search across `clients` and `src` for account-deletion, account removal, `/api/account`, privacy/settings/logout surfaces found no user-facing account-deletion control in the canonical THF client source. The only matching line was an unrelated AI privacy note.

The canonical web client contains the main shell and service pages, but no independent deletion/settings page. The Android source scan in this canonical source archive returned no native Kotlin/Java/XML/Gradle client files in the inspected `clients` tree.

## Release interpretation
- Backend account deletion candidate: already proven by disposable HTTP E2E (`34721620117`).
- User-facing deletion control: **MISSING / BLOCKER**.
- Public `/account-deletion` instructions resource: **MISSING / BLOCKER**.
- Privacy/Terms/security.txt independent resources remain separate compliance blockers.

## Safety
- Canonical source mutation: FALSE
- Production runtime mutation: FALSE
- Production DB mutation: FALSE
- Production signing: FALSE
- Google Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana/token financial action: FALSE
- WAVE_MAWJA mutation: FALSE

## Next step
Inspect the exact web client structure from the verified account-deletion endpoint candidate, then create a reversible versioned client-surface candidate that exposes a deletion control and independent `/account-deletion` instructions without touching production or the canonical source archive.
