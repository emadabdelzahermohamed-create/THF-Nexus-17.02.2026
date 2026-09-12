# THF Google Play Release Roadmap — 2026-09-12

Status: ACTIVE
Scope: THF Fit Core · THF Fit Terra · THF Fit Rift
Policy: No public Play release until every P0 gate below is PASS. WAVE remains isolated unless an app explicitly depends on it.

## Gate 1 — Production Runtime / VPS

| Task | State | Acceptance |
|---|---|---|
| Recover existing `thf-runtime-s1` | PASS | Existing runtime located on GCP VM |
| Start THF Nexus runtime | PASS | Local `/health` returns `ok:true`, release `6.0.0` |
| Temporary Cloudflare HTTPS smoke | PASS | External `/health` passes through Quick Tunnel; run `34687446254` |
| GCP production inventory | PASS-WITH-FINDING | Run `34702891468`; runtime root FOUND, local health PASS release `6.0.0`; evidence `ReleaseOps/GCP_PRODUCTION_INVENTORY_20260912.md` |
| Firewall hardening | BLOCKED-AUTHORIZATION | Public `default-allow-ssh` TCP/22 and `default-allow-rdp` TCP/3389 from `0.0.0.0/0` are broader than required; do not mutate without explicit authorization; IAP SSH rule already exists |
| Cloud Run inventory | LIMITED-PERMISSION | `run.services.list` denied to least-privilege WIF service account; no privilege escalation attempted |
| Create Named Cloudflare Tunnel | BLOCKED-AUTHORIZATION | Stable named tunnel requires explicit Cloudflare production-cutover authorization before execution |
| Bind fixed production hostname | BLOCKED-AUTHORIZATION | Stable HTTPS API hostname with TLS; no production DNS/cutover performed without exact authorization |
| Set production API base URL in Core/Terra/Rift | WAITING-RUNTIME-HOSTNAME | No temporary Quick Tunnel URL embedded |
| External end-to-end API smoke from installed apps | WAITING-FINAL-BINARIES | Auth/session/core API paths work from real Android devices |

## Gate 2 — Android Production Binaries

| Task | State | Acceptance |
|---|---|---|
| Android SDK / build tools 36 | PASS | Builder validates API 36 metadata through WIF/IAP |
| Core package identity | PASS | `com.topherofit.thf.core`, versionCode 62200 |
| Terra package identity | PASS | `com.topherofit.thf.terra`, versionCode 42060 |
| Rift package identity | PASS | `com.topherofit.thf.rift`, versionCode 42064 |
| Core unsigned release AAB candidate | PASS | Run `34678895451`; AAB SHA-256 `e71625911d2c06eb0d084f6ed094fcd142f093fcfbb2bf2b13b59a4221760e6e`; source SHA-256 `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a` |
| Terra unsigned/test AAB candidate | PASS | Run `34676649980`; AAB SHA-256 `3af39232213171de0a5069dea2dfe3dab585d75f7246bf0bd75d61bb8a7dbee3`; source SHA-256 `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68` |
| Terra QA binary retrieval | PASS | Run `34701965401`; artifact `THF-Terra-RC34-QA-binaries`, artifact ID `10300501979`, artifact digest SHA-256 `a7c332b5cd48fcf556929ccf8e38e20560985b807367b51656ec4c178d9a6b1b`; no signing/publishing performed |
| Rift unsigned/test AAB candidate | PASS | Run `34676685100`; AAB SHA-256 `1eb449b061135984bbdef5cecf012496b8d667963f37d813518f4fcd389652c7`; source SHA-256 `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914` |
| Permission-minimized Android candidate | PASS-CANDIDATE | Run `34700180841`; isolated copy removed CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION and ACCESS_COARSE_LOCATION; debug APK SHA-256 `44b5c2f2d3b398768bf937487ae86d87d06702d715b94e900dea27ea82cc1484`; test unsigned AAB SHA-256 `429b6e982c6c1290033b0b69a2f7433d69eee208b03d6a20c59c376a2a818e30`; canonical source SHA-256 remained `46eca5adaef95d551e90723f87698100dbe242f51cd28186480b3215a2a54942` before/after |
| Final production-configured AAB rebuild | WAITING-RUNTIME-HOSTNAME | Rebuild only after stable production API base URL is frozen; retain SHA-256 evidence |
| Production upload-key signing | BLOCKED-AUTHORIZATION | Release AABs signed for Play upload; debug keys forbidden; no production signing performed |
| Play App Signing enrollment | USER/PLAY-CONSOLE | Each Play app enrolled and upload certificate recorded |
| Real-device install/smoke | WAITING-FINAL-BINARIES | Launch, login, API, lifecycle, permissions, network PASS |
| Crash/ANR regression gate | WAITING-FINAL-BINARIES | No release-blocking crash/ANR in final candidate |

## Gate 3 — Google Play Console Compliance

| Task | State | Acceptance |
|---|---|---|
| Create/verify Play Console entries for all 3 apps | TODO-VERIFY | Correct package IDs; ownership confirmed |
| Store listing assets | TODO | Name, short/full description, icon, feature graphic, screenshots |
| Privacy Policy | BLOCKED-CONTENT | Run `34715148011`: `/privacy` is SPA fallback identical to `/`; requires reviewed distinct public HTTPS policy + in-app access. Evidence `ReleaseOps/Compliance/THF_POLICY_ACCOUNT_DELETION_AUDIT_V2_20260912.md` |
| Account deletion | BLOCKED-IMPLEMENTATION | Run `34715148011`: `/account-deletion` is SPA fallback and no self-service account-delete route was identified; requires authenticated in-app deletion flow plus public deletion information URL and reviewed retention semantics |
| Terms | BLOCKED-CONTENT | Run `34715148011`: `/terms` is SPA fallback identical to `/`; reviewed distinct terms resource required where product/legal policy requires it |
| Security contact resource | BLOCKED-CONTENT | Run `34715148011`: `/.well-known/security.txt` returns the SPA root as `text/html`; provide a real approved resource if retained as a release requirement |
| Data Safety | IN-PROGRESS | Runtime/native/provider facts audited; final declaration waits on final permission/provider configuration and approved retention/deletion semantics |
| App content / content rating | TODO | Required questionnaires complete |
| Ads declaration / consent flow | TODO-VERIFY | Correct declaration and consent where applicable |
| Permissions review | PASS-CANDIDATE | Four latent sensitive permissions can be removed without breaking API-36 debug/test-AAB builds; candidate run `34700180841`; apply only to a versioned release source, never overwrite canonical archive |
| Play Integrity production configuration | TODO-VERIFY | Production project/app linkage and verification path PASS where enabled |
| Countries / pricing / distribution | TODO | Launch countries and free/paid configuration set |

## Gate 4 — Play Track Validation

| Task | State | Acceptance |
|---|---|---|
| Internal testing upload | BLOCKED-AUTHORIZATION | Final signed AAB uploaded and installable from Play; irreversible/publishing action not performed |
| Closed testing, if account policy requires it | CONDITIONAL | Required tester count/duration completed |
| Play pre-launch report | WAITING-INTERNAL-TRACK | No blocking compatibility/security/accessibility findings |
| Production access | CONDITIONAL | Granted for account if Google requires an access application |

## Gate 5 — Public Production

| Task | State | Acceptance |
|---|---|---|
| Final release manifest | IN-PROGRESS | Current unsigned/test AAB hashes captured; stable runtime hostname, signed AAB hashes and rollback reference still required |
| Staged rollout | BLOCKED-AUTHORIZATION | Start controlled rollout only after exact authorization; monitor crashes/ANRs/backend health |
| Public availability | BLOCKED-AUTHORIZATION | Core/Terra/Rift visible and installable from Google Play only after explicit release authorization |

## Verified runtime checkpoint

- GCP access uses GitHub OIDC/WIF + IAP/OS Login; no persistent cloud key is required.
- Runtime process: RUNNING on localhost port `18080` at the latest compliance audit.
- Cloudflare Quick Tunnel process: RUNNING.
- Local `/health`: PASS; audit run `34715148011` returned HTTP 200 with a distinct JSON response.
- External HTTPS `/health`: PASS in run `34687446254`.
- GCP inventory run `34702891468` verified the builder/runtime read-only and performed no mutation.
- Policy/deletion audit run `34715148011` verified that `/privacy`, `/terms`, `/account-deletion` and `/.well-known/security.txt` currently resolve to the same SPA root and therefore are not compliance resources.
- The Quick Tunnel hostname is temporary evidence only and MUST NOT be embedded as a production API URL.
- Public SSH/RDP firewall rules are recorded for later hardening but remain unchanged pending exact authorization.

## Release order

1. Obtain exact authorization for Cloudflare production cutover, then freeze a stable production API hostname.
2. Maintain the versioned permission-minimized release-source candidate while preserving the canonical archive unchanged.
3. Complete distinct Privacy/Terms/account-deletion/security resources and an authenticated self-service deletion path; obtain required legal/owner approval for wording and retention semantics.
4. Rebuild and inspect Core/Terra/Rift final AABs against the frozen hostname.
5. Perform production upload-key signing only after exact signing authorization and verify Play App Signing.
6. Complete Play Console store/compliance forms.
7. Upload to Internal testing only after exact Play publishing authorization and install from Play on real devices.
8. Complete Closed testing / production-access gate only if the developer account is subject to it.
9. Submit staged Production rollout only after explicit final release authorization.

## Hard blockers before first Play upload

- Explicit authorization for Cloudflare production cutover and a stable production API endpoint instead of Quick Tunnel URL.
- Distinct approved Privacy Policy and account-deletion information resource; authenticated self-service deletion implementation and reviewed retention semantics.
- Final production-configured AAB rebuild for Core/Terra/Rift after the API hostname is frozen.
- Explicit production-signing authorization plus upload-key / Play App Signing path.
- Play Console app records and remaining mandatory store/app-content metadata.
- Explicit authorization before any Play upload/publishing action.

## WAVE_MAWJA isolation status

WAVE remains technically isolated from these THF runtime and Android gates. No WAVE source, runtime, build artifact or production configuration is used by Core/Terra/Rift. The previously identified WAVE live-gate blocker remains the absence of the full canonical `/root/workspace/wave-mawja` runtime/source on the GCP builder; WIF/IAP itself is not the blocker.

## Non-blocking post-launch integrations unless explicitly required by a selected app build

- High-fidelity GPU avatar provider.
- Large-media object storage/transcoding expansion.
- Public TURN/WebRTC expansion.
- Solana production signer/economy cutover.
- WAVE media integration beyond fail-closed/disabled behavior.
