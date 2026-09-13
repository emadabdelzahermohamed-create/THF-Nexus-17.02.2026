# THF Policy Resources Candidate V1 — PASS-CANDIDATE

Date: 2026-09-13

## Scope
Reversible technical routing candidate only. No legal approval is asserted.

## Input
- Basename: `THF_NEXUS_6_ACCOUNT_CLIENT_CANDIDATE_V1_34723424879.zip`
- SHA-256 before build: `8b0b892d1f32bdc7d5daa9867a442a349f6306969f29e9771dab2af3a9178784`
- SHA-256 after build: `8b0b892d1f32bdc7d5daa9867a442a349f6306969f29e9771dab2af3a9178784`

## Output
- Basename: `THF_NEXUS_6_POLICY_RESOURCES_CANDIDATE_V1_34726147267.zip`
- SHA-256: `a2989295b495a717eb8890537f1a348b6cabe78f261fa13ae763f76e1b835310`

## Execution evidence
- GitHub Actions run: `34726147267`
- Workflow head: `4f9b49f1a0a02248796371296906e5eab3a58ff1`
- GitHub OIDC/WIF authentication: PASS
- GCP IAP builder execution: PASS
- `/privacy` distinct from SPA root: PASS
- `/terms` distinct from SPA root: PASS
- `/.well-known/security.txt` distinct from SPA root: PASS
- `security.txt` content type `text/plain`: PASS
- Draft markers present: PASS
- THF/WAVE isolation: PASS

## Safety / mutation evidence
- Legal content approved: FALSE
- Production runtime mutation: FALSE
- Production DB mutation: FALSE
- Canonical archive overwrite: FALSE
- Production signing performed: FALSE
- Google Play upload performed: FALSE
- Cloudflare production cutover performed: FALSE
- Solana financial action performed: FALSE
- WAVE touched: FALSE

## Status
`PASS-CANDIDATE` for technical routing/resource behavior only.

## Remaining blockers
1. Privacy Policy legal/content review and approval.
2. Terms legal/content review and approval.
3. `security.txt` production contact/canonical values review and approval.
4. Stable production hostname/canonical URLs remain gated behind the separately authorized Cloudflare production cutover.
5. Production signing and Google Play upload remain explicitly gated.

## Next safe step
Continue with reversible release-readiness verification that does not require legal approval, production signing, Play publishing, Cloudflare production cutover, Solana financial actions, or destructive cloud changes.
