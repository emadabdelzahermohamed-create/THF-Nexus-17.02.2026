# THF Google Play Release Roadmap — 2026-09-12

Status: ACTIVE
Scope: THF Fit Core · THF Fit Terra · THF Fit Rift
Policy: No public Play release until every P0 gate below is PASS. WAVE remains isolated unless an app explicitly depends on it.

## Gate 1 — Production Runtime / VPS

| Task | State | Acceptance |
|---|---|---|
| Recover existing `thf-runtime-s1` | PASS | Existing runtime located on GCP VM |
| Start THF Nexus runtime | PASS | Local `/health` returns `ok:true`, release `6.0.0` |
| Temporary Cloudflare HTTPS smoke | PASS | External `/health` passes through Quick Tunnel |
| Create Named Cloudflare Tunnel | TODO | Stable named tunnel, not `trycloudflare.com` |
| Bind fixed production hostname | TODO | Stable HTTPS API hostname with TLS |
| Set production API base URL in Core/Terra/Rift | TODO | No temporary Quick Tunnel URL embedded |
| External end-to-end API smoke from installed apps | TODO | Auth/session/core API paths work from real Android devices |

## Gate 2 — Android Production Binaries

| Task | State | Acceptance |
|---|---|---|
| Android SDK / build tools 36 | READY | Builder workflow validates API 36 metadata |
| Core package identity | READY | `com.topherofit.thf.core`, versionCode 62200 |
| Terra package identity | READY | `com.topherofit.thf.terra`, versionCode 42060 |
| Rift package identity | READY | `com.topherofit.thf.rift`, versionCode 42064 |
| Core/Terra/Rift release AAB build gate | TODO-VERIFY | Run latest RC17 build and retain AAB + SHA-256 evidence |
| Production upload-key signing | TODO | Release AABs signed for Play upload; debug keys forbidden |
| Play App Signing enrollment | TODO | Each Play app enrolled and upload certificate recorded |
| Real-device install/smoke | TODO | Launch, login, API, lifecycle, permissions, network PASS |
| Crash/ANR regression gate | TODO | No release-blocking crash/ANR in final candidate |

## Gate 3 — Google Play Console Compliance

| Task | State | Acceptance |
|---|---|---|
| Create/verify Play Console entries for all 3 apps | TODO-VERIFY | Correct package IDs; ownership confirmed |
| Store listing assets | TODO | Name, short/full description, icon, feature graphic, screenshots |
| Privacy Policy | TODO-VERIFY | Public HTTPS policy URL + in-app access |
| Data Safety | TODO | Accurate declarations for collected/shared data |
| App content / content rating | TODO | Required questionnaires complete |
| Ads declaration / consent flow | TODO-VERIFY | Correct declaration and consent where applicable |
| Permissions review | TODO | Only required permissions; sensitive permissions justified |
| Play Integrity production configuration | TODO-VERIFY | Production project/app linkage and verification path PASS where enabled |
| Countries / pricing / distribution | TODO | Launch countries and free/paid configuration set |

## Gate 4 — Play Track Validation

| Task | State | Acceptance |
|---|---|---|
| Internal testing upload | TODO | Final signed AAB uploaded and installable from Play |
| Closed testing, if account policy requires it | CONDITIONAL | Required tester count/duration completed |
| Play pre-launch report | TODO | No blocking compatibility/security/accessibility findings |
| Production access | CONDITIONAL | Granted for account if Google requires an access application |

## Gate 5 — Public Production

| Task | State | Acceptance |
|---|---|---|
| Final release manifest | TODO | AAB hashes, package IDs, versions, runtime hostname, rollback reference |
| Staged rollout | TODO | Start controlled rollout; monitor crashes/ANRs/backend health |
| Public availability | TODO | Core/Terra/Rift visible and installable from Google Play |

## Release order

1. Freeze stable production API hostname.
2. Rebuild and inspect Core/Terra/Rift release AABs against that hostname.
3. Sign with upload key and enroll/verify Play App Signing.
4. Complete Play Console store/compliance forms.
5. Upload to Internal testing and install from Play on real devices.
6. Complete Closed testing / production-access gate only if the developer account is subject to it.
7. Submit staged Production rollout.

## Hard blockers before first Play upload

- Stable production API endpoint instead of Quick Tunnel URL.
- Final release AAB artifacts for Core/Terra/Rift with SHA-256 evidence.
- Upload-key / Play App Signing path.
- Play Console app records and mandatory policy/store metadata.

## Non-blocking post-launch integrations unless explicitly required by a selected app build

- High-fidelity GPU avatar provider.
- Large-media object storage/transcoding expansion.
- Public TURN/WebRTC expansion.
- Solana production signer/economy cutover.
- WAVE media integration beyond fail-closed/disabled behavior.
