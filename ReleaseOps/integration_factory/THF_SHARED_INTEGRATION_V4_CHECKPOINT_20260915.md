# THF Shared Integration V4 Checkpoint — 2026-09-15

## Scope
Shared THF integration only. WAVE_MAWJA was not touched. No production signing, store publication, financial mutation, deployment, token action, or other irreversible operation was performed.

## Authoritative baseline
- Previous shared contract baseline: V3 (`thf.shared.integration.v3`).
- V3 schema validator repair head before this batch: `961962e1eb35f85f400c5b5eec73baf6feefa29b`.
- Package identities remain unchanged.

## V4 commits
- `da553bcc921841f1d8ac1bef36231d5bb42ccf64` — runtime binding contracts.
- `9ed164b6dffed1657d51689e4ef5cf80ce75b34a` — V4 regression coverage.
- `cad0e6f626ff4c91890abbe46e00fa9c4256e2bc` — Android V4 machine-readable manifest.
- `e3c898b0e794a9c068b77c277a4665f62829774c` — V4 CI gate.

## CI evidence
GitHub Actions run `34904946338` — **THF Shared Integration V4** — completed **SUCCESS** on commit `e3c898b0e794a9c068b77c277a4665f62829774c`.

The gate compiles the V3/V4 Python contracts, executes the existing V3 regression suite plus the new V4 runtime suite, and validates the V4 Android manifest/package compatibility/release-truth invariants.

## V4 additions
### Credential Manager / Google
- Android Credential Manager + Sign in with Google request is package-bound to known THF package identities.
- Mobile client secrets are explicitly forbidden.
- A minimum 32-character per-request nonce is required and represented only by a SHA-256 audit value in the returned request contract.
- Server cryptographic signature verification remains mandatory.
- Server nonce verification is now mandatory in the V4 identity validator in addition to V3 issuer/audience/expiry/email checks.

### Session lifecycle
- Authenticated session subject is mandatory.
- Access-token lifetime is bounded to at most 30 minutes by the shared runtime contract.
- Refresh-token rotation and reuse detection are mandatory.
- Refresh material is secure-storage-only and server revocation is required.
- Returned contract stores hashes for refresh-token ID/device ID and never returns/logs raw refresh material.

### Admin / Publisher authorization
- Existing V3 authenticated-session and role checks remain in force.
- V4 additionally requires fresh server-issued operator roles with a maximum age of 300 seconds for Admin/Publisher entry.
- Client-side role override is explicitly forbidden.

### Cross-app handoff
- Existing 300-second, single-use, server-signed/no-role/no-secret semantics are preserved.
- V4 binds the handoff audience to the exact target THF package ID.
- The eventual production server signature must cover the target package, preventing target-confusion/replay into a sibling application.

### Health consent and synchronization
- Explicit consent receipts now carry subject/provider/metric scope, grant time and revocation state.
- Audit representation hashes subject/consent identifiers and contains no raw health payload.
- Revoked consent fails closed.
- Health sync is restricted to consented metrics and bounded to a maximum 31-day window per request.
- Opaque cursor syntax is validated.
- Provenance and deduplication remain mandatory; client health data still has zero reward authority.
- Health Connect remains primary; Samsung Health Data SDK remains optional/nonfatal pending approved partner/runtime binding.

### Motion verification
- V4 submission envelope binds motion evidence to a user/workout and optional deduplicated supporting health-record references.
- Health records remain supporting evidence only.
- Manual client reward override is forbidden and the final verdict remains server-authoritative.

### Naming/icons/package compatibility
- V4 machine-readable branding covers the twelve THF Android identities with the approved Arabic/English names.
- Package IDs remain unchanged.
- Adaptive icon, monochrome icon and store-icon source are mandatory metadata requirements.
- Admin/Publisher public listing remains forbidden.

## Remaining external/runtime bindings — explicitly not complete
- Google Auth Platform production OAuth client/brand/consent configuration.
- Real backend Google signature/JWK verifier binding.
- Durable server refresh-token/session reuse-detection store.
- Production server role issuer/claim freshness binding.
- Durable Health consent store and real provider permission/runtime adapters.
- Cross-app production signer.
- Samsung Health production partner registration/AAR approval.
- Exact-candidate physical-phone Health Connect/Samsung Health/Credential Manager validation.
- Production signing/Play acceptance.

## Release truth
`PHYSICAL_DEVICE_PASS = FALSE`

`FINAL_OR_PLAY_READY = FALSE`
