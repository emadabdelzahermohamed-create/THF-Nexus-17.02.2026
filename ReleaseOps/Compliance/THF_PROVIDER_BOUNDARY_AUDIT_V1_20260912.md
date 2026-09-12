# THF Provider Boundary Audit V1

Date: 2026-09-12
Status: PASS — provider configuration remains release-gated
Scope: THF Nexus only. WAVE_MAWJA explicitly excluded and untouched.

## Evidence

- GitHub Actions run: `34700038234`
- Job: `103570055932` (`provider_boundary`)
- WIF authentication: PASS
- Google Cloud CLI setup: PASS
- GCP IAP SSH to `thf-wave-builder`: PASS
- Read-only provider-boundary audit: PASS
- Audited source-set SHA-256: `f3c084f35c0453938e77368ccac4110915af9dd6b01a3eac55ba56e5c09d6cea`
- Follow-up deterministic workflow run `34700055669`: PASS

## Findings

### AI

The scanned runtime contains provider hooks identified by environment-variable names for OpenAI, Gemini and Groq. The active source path has a deterministic `local-policy` fallback. This audit did not read secret values and does not establish that any external AI provider is configured or receiving production user data.

### Media / object storage / live transport

The current media implementation provides local upload/storage behavior for the inspected runtime. Source evidence explicitly keeps large-media object storage behind a production adapter boundary and keeps public cross-network live audio/video behind a TURN/WebRTC provider gate. No active production object-storage or TURN/WebRTC destination was established by this audit.

### Avatar

The current runtime provides a local animated GLB fallback. High-fidelity photoreal reconstruction remains a pluggable external/GPU-provider gate controlled by configuration; the scan does not establish an active external high-fidelity provider.

### Advertising / analytics

The inspected runtime implements a first-party ad/yield control plane with local impression/event persistence, frequency caps, protected contexts and sensitive targeting disabled in source. Provider-reported revenue has an administrative boundary, but this scan did not establish an active third-party ad network or external analytics destination.

### Identity

The inspected runtime contains the local THF identity/session service. No active external OAuth/OIDC/Firebase identity provider destination was established by the scanned source evidence.

### Network/security boundary

- Runtime CSP observed in source: `connect-src 'self'`.
- Runtime Permissions-Policy observed in source: `camera=(), microphone=(), geolocation=()`.
- Hard-coded external-host classification did not identify a specific active OpenAI/Google/Groq/Cloudflare/AWS/Azure provider endpoint in the inspected source. Generic external literals must not be interpreted as configured production destinations.

## Play/Data Safety implication

Current same-origin/local evidence must remain the release declaration baseline until final production providers are selected and re-audited. Provider hooks or environment-variable names alone are not proof of external collection/sharing. Any future activation of external AI, object storage, TURN/WebRTC, ad/analytics or identity providers requires a fresh final-build Data Safety/network audit before Play Console submission.

## Safety / isolation evidence

- `THF_RUNTIME_WAVE_ISOLATION=PASS`
- `SECRET_VALUES_READ=FALSE`
- `MUTATION_PERFORMED=FALSE`
- `PRODUCTION_SIGNING_PERFORMED=FALSE`
- `PLAY_UPLOAD_PERFORMED=FALSE`
- `CLOUDFLARE_PRODUCTION_CUTOVER_PERFORMED=FALSE`
- `SOLANA_FINANCIAL_ACTION_PERFORMED=FALSE`
- `WAVE_UNTOUCHED=TRUE`

## Next highest-priority safe gates

1. Android sensitive-permission minimization candidate: prove whether CAMERA, RECORD_AUDIO and precise/approximate location can be removed from the release candidate without breaking intended current functionality; candidate-only, reversible, no production signing/upload.
2. Legal/static-resource readiness: restore standalone Privacy, Terms, account-deletion and `/.well-known/security.txt` routing/resources from the latest canonical lineage where available, while leaving operator/legal-entity placeholders unresolved rather than inventing legal identity data.
3. Re-run runtime compliance and Play Data Safety against the eventual final provider configuration and final AAB.

No canonical archive was overwritten or deleted.