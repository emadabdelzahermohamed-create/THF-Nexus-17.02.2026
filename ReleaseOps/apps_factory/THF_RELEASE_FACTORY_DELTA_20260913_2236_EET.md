# THF Release Factory Delta — 2026-09-13 22:36 EET

Body SHA-256 (content below this line before insertion): `ef5926429adadbae2ddde9d30bc461a0c11feb1e61d88c443396fe1c200357ce`

## Truth boundary
`FINAL_OR_PLAY_READY=FALSE`

No production signing, Play publication, Cloudflare production cutover, destructive cloud mutation, WAVE source mutation, real credential use, or physical-device claim was performed.

## New safe autonomous work
Added read-only workflow `THF Pass Runtime Source Inventory V1` at commit `f6313740929121a4cb273afe8cae58a300fb46a8`.

Workflow run `34778114163` completed SUCCESS through GitHub OIDC/WIF, GCP/IAP and the existing builder. It inspected only the deployed THF staging runtime under the release-builder service-account workspace and explicitly recorded `MUTATION_PERFORMED=FALSE` and `WAVE_UNTOUCHED=TRUE`.

Artifact:
- name: `THF-PASS-RUNTIME-SOURCE-INVENTORY-V1`
- id: `10324033686`
- digest: `sha256:6d568236f09527a77151677790f7b1ce3c06173fb161f3d96293060a0ed1259a`

## Material finding
The deployed runtime source confirms the THF Pass lifecycle gap is implementation-level, not merely an OpenAPI/probe ambiguity.

Observed route/service evidence:
- `/api/auth/login` POST is implemented and calls `rt.identity.login(...)`.
- `identity.service` implements `login`, `_new_session`, TTL-backed session insertion and `user_from_token`.
- No deployed HTTP route evidence was found for refresh.
- No deployed HTTP route evidence was found for logout.
- No deployed HTTP route/service evidence was found for server-side revoke/revocation.
- No deployed HTTP route evidence was found for federation/handoff/OAuth/OpenID.
- A generic `refresh` keyword exists elsewhere in the deployed tree, but it is not evidence of an auth refresh route and must not be promoted as such.

This is consistent with live safe-negative run `34777926029`: health/login-like surface exists, while refresh/logout/revoke/federation are not reachable.

## Release consequence
The currently runtime-bound Android candidates remain valid as QA staging candidates for package/API36/non-empty HTTPS binding evidence, but shared-auth readiness remains blocked. No app may be promoted to FINAL/PLAY_READY based on the login surface alone.

Required engineering before auth promotion:
1. add a reversible candidate implementation for refresh/expiry, logout and server-side revocation;
2. add federation/handoff only against an explicit non-production contract;
3. add integration tests proving expiry -> refresh, logout invalidation and revoked-token rejection;
4. only then use a non-production test identity/service credential for positive-flow semantics.

## Other authoritative blockers unchanged
- Exact-SHA physical-phone acceptance remains mandatory for all Android candidates.
- Production signing / Play Internal / owner/legal gates remain unproven.
- Stable production HTTPS/WSS cutover remains unproven.
- WAVE RC14 remains isolated and blocked on authoritative canonical RC13/RC14 source accessibility; no older source was substituted.
