# THF Play Data Safety Technical Matrix V2

Date: 2026-09-12
Status: TECHNICAL RELEASE-CANDIDATE EVIDENCE — NOT A LEGAL/PLAY CONSOLE SUBMISSION
Scope: THF Nexus Android release candidate only. WAVE_MAWJA excluded and untouched.

## Evidence chain

- Native metadata gate: Run `34697279008`
- Sensitive permission usage gate: Run `34697407569`
- Runtime/backend data-flow gate: Run `34697483514`
- Provider-boundary audit: PASS, documented in `THF_PROVIDER_BOUNDARY_AUDIT_V1_20260912.md`
- Permission-minimized isolated candidate: Run `34700180841`
- Versioned permission-min source: Run `34708908483`
- Versioned API-36 permission-min build: Run `34709148029`
- Versioned candidate source SHA-256: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7`
- Debug APK SHA-256: `44b5c2f2d3b398768bf937487ae86d87d06702d715b94e900dea27ea82cc1484`
- Test unsigned AAB SHA-256: `429b6e982c6c1290033b0b69a2f7433d69eee208b03d6a20c59c376a2a818e30`

## Change from V1

The previous matrix classified live camera, live microphone and device geolocation as `CAPABILITY-LATENT` because their Android permissions/native bridges existed while the inspected browser runtime blocked them and no active invocation was found.

For the versioned release candidate, the following Android manifest permissions have now been removed and the candidate still builds successfully against API 36:

- `android.permission.CAMERA`
- `android.permission.RECORD_AUDIO`
- `android.permission.ACCESS_FINE_LOCATION`
- `android.permission.ACCESS_COARSE_LOCATION`

The merged debug manifest was verified free of these permissions, and the candidate source hash was unchanged by the build. This resolves the permission-minimization blocker for the current candidate. It does not assert that future releases may never add these capabilities; any later activation requires a fresh permission/data-safety audit.

## Current Play-relevant technical matrix

| Data class | Release-candidate technical status | Evidence / behavior | Current external-sharing evidence |
|---|---|---|---|
| Account identifier / username | COLLECTED, USER-PROVIDED | Register/login and user/profile persistence | No external destination established in inspected configuration; re-verify final providers |
| Profile data | COLLECTED, USER-PROVIDED | Profile/locale/goal/level/preferences persistence | Re-verify final provider configuration |
| Avatar photo | COLLECTED, USER-PROVIDED | User-selected image -> avatar generation endpoint; photo/reference metadata retained | Current inspected path is same-origin/local; re-verify final AI/storage providers |
| Social/media photos and video | COLLECTED, USER-PROVIDED | File picker -> media upload; media bytes/metadata/SHA persisted | Current inspected path is same-origin/local; re-verify object storage/CDN before submission |
| Audio file content | BACKEND-SUPPORTED / UI-NOT-OBSERVED | Backend recognizes audio type; no active audio picker path established | Do not declare active collection solely from backend support |
| Live camera | NOT REQUESTED BY VERSIONED ANDROID CANDIDATE | CAMERA permission removed; current runtime also blocks camera via Permissions-Policy and no active invocation was found | Not established |
| Live microphone | NOT REQUESTED BY VERSIONED ANDROID CANDIDATE | RECORD_AUDIO removed; current runtime blocks microphone and no active invocation was found | Not established |
| Device precise/approximate location | NOT REQUESTED BY VERSIONED ANDROID CANDIDATE | Fine/coarse location permissions removed; current runtime blocks geolocation and no active invocation was found | Not established |
| In-world/player position | COLLECTED, DERIVED/INTERACTION | Virtual-world x/y/district sent to same-origin social/runtime APIs | Same-origin observed; not device GPS |
| Fitness/activity | COLLECTED, USER-PROVIDED/DERIVED | Duration, distance, steps, cadence, integrity/evidence fields, session/set records | Re-verify final provider configuration |
| Recovery/health-related inputs | COLLECTED, USER-PROVIDED | Sleep, soreness, fatigue, resting-HR delta/readiness data | Sensitive-data policy/retention/deletion language required |
| Chat/messages | COLLECTED, USER-PROVIDED | Chat text/user/channel/context persisted | Same-origin observed; re-verify if external voice/video transport is enabled later |
| Media comments/reactions | COLLECTED, USER-PROVIDED/INTERACTION | Comments/reactions persisted | Same-origin observed |
| Media viewing activity | COLLECTED, DERIVED/INTERACTION | Watch seconds/completion/view records | Same-origin observed |
| Advertising interactions | COLLECTED, DERIVED/INTERACTION | Impression/click/campaign/placement/session events | No external ad-network destination established in inspected configuration |
| Sensitive-trait ad targeting | POLICY-PROHIBITED IN SOURCE | Protected/sensitive traits are not targeting inputs in inspected source | Re-verify if external ad provider is later enabled |
| Device/advertising identifier | NOT OBSERVED | No Android Advertising ID path established in current evidence | Re-scan final dependencies/providers |
| Authentication/session data | COLLECTED/DERIVED | Login/session/security mechanisms | Re-verify if external identity provider is enabled |

## Resolved blocker

`PERMISSION-MINIMIZATION` is now `PASS-CANDIDATE` for the versioned release source. The four previously latent sensitive Android permissions are absent and API-36 debug/test-AAB builds pass.

## Remaining P0/P1 compliance blockers

1. **Independent legal/static resources:** Privacy, Terms, account-deletion and `/.well-known/security.txt` must resolve to real independent resources rather than SPA fallback.
2. **Account deletion:** public/self-service account-deletion route and end-to-end behavior still require verification.
3. **Sensitive-data policy:** fitness/recovery/health-related retention, deletion, security and purpose language must match the final implementation.
4. **Final provider verification:** object storage/CDN, AI, ads/analytics, identity and TURN/WebRTC must be re-audited after production provider configuration is frozen.
5. **Stable production API hostname:** remains blocked pending exact Cloudflare production-cutover authorization; do not embed the temporary Quick Tunnel URL.
6. **Final signed-release verification:** Data Safety must be checked again from final production-configured binaries before Play submission.
7. **Non-delegable Play/legal acceptance:** owner/legal declarations remain user/Play-Console actions where required.

## Safety posture

No production signing, Play upload/publishing, Cloudflare production cutover, Solana/token financial action, canonical source overwrite/delete, destructive GCP change, or THF/WAVE mixing was performed while producing this matrix.
