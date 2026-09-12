# THF Play Data Safety Technical Matrix V1

Date: 2026-09-12
Status: TECHNICAL EVIDENCE MATRIX — NOT A LEGAL/PLAY CONSOLE SUBMISSION
Scope: THF Nexus only. WAVE_MAWJA is explicitly excluded.

Evidence chain:
- Native metadata gate: Run `34697279008`
- Sensitive permission usage gate: Run `34697407569`
- Runtime/backend data-flow gate: Run `34697483514`
- Runtime scanned source-set SHA-256: `19a03999aaa58e469d378f3db24d976e678a002abd3a8ec4888365a12bfc9653`
- Android native source-root SHA-256: `46eca5adaef95d551e90723f87698100dbe242f51cd28186480b3215a2a54942`

Legend:
- `COLLECTED`: source evidence shows data sent to/stored by THF backend when feature is used.
- `LOCAL/SAME-ORIGIN`: observed client destination is the THF same-origin runtime/backend.
- `CAPABILITY-LATENT`: permission/native bridge exists, but current browser runtime blocks it and no active invocation was found.
- `NEEDS_PROVIDER_VERIFY`: current source evidence is insufficient to determine external third-party sharing/provider behavior.
- `USER-PROVIDED`: user explicitly enters/selects/submits the data.
- `DERIVED/INTERACTION`: generated from use of the app/service.

| Play-relevant data class | Current technical status | Evidence / source behavior | Observed purpose | External sharing status |
|---|---|---|---|---|
| Account identifier / username | COLLECTED, USER-PROVIDED | Register/login and `users`/`profiles` persistence | Account management, authentication | NEEDS_PROVIDER_VERIFY; no external destination established in current scan |
| Profile data | COLLECTED, USER-PROVIDED | `/api/profile`; display name, locale, goal, level and preferences stored | Personalization/app functionality | NEEDS_PROVIDER_VERIFY |
| Photos — avatar reference | COLLECTED, USER-PROVIDED | User selects image; `FileReader` -> `photo_base64` -> `/api/avatar/generate`; avatar record stores photo SHA/reference path | Avatar generation / app functionality | NEEDS_PROVIDER_VERIFY; current runtime is same-origin/local-provider path |
| Photos/video — social/media upload | COLLECTED, USER-PROVIDED | File picker -> `/api/media/upload`; runtime stores media bytes + metadata/SHA | User-generated content/social functionality | NEEDS_PROVIDER_VERIFY; production object-storage/provider adapter not yet verified |
| Audio file content | SUPPORTED-BACKEND / UI-NOT-OBSERVED | Media service recognizes `audio/mpeg`, but current media picker scan accepts image/video and no audio picker path was observed | Future/media functionality | NEEDS_PROVIDER_VERIFY; do not declare active audio collection solely from backend support |
| Live camera | CAPABILITY-LATENT | CAMERA permission + native WebView bridge exist; current runtime sends `Permissions-Policy: camera=()` and no `getUserMedia` call was found | Intended media/interactive capability not active in current runtime evidence | Not established |
| Live microphone | CAPABILITY-LATENT | RECORD_AUDIO permission + native bridge exist; current runtime sends `Permissions-Policy: microphone=()` and no `getUserMedia`/MediaRecorder call was found | Intended media/communications capability not active in current runtime evidence | Not established |
| Precise/approximate device location | CAPABILITY-LATENT | Fine/coarse permissions + native geolocation bridge exist; current runtime sends `Permissions-Policy: geolocation=()` and no navigator geolocation call was found | Intended location-aware capability not active in current runtime evidence | Not established |
| In-world/player position | COLLECTED, DERIVED/INTERACTION | `/api/social/position` sends virtual-world x/y/district; chat records position context | Proximity/social/world functionality | LOCAL/SAME-ORIGIN observed; this is not device GPS |
| Fitness/activity | COLLECTED, USER-PROVIDED/DERIVED | Activity submission includes duration, distance, GPS-distance field, steps, cadence, integrity and nonce; workout sessions/sets stored | Fitness tracking, verification, competition | NEEDS_PROVIDER_VERIFY |
| Recovery/health-related inputs | COLLECTED, USER-PROVIDED | Sleep hours, soreness, fatigue, resting-HR delta submitted to readiness endpoint; recovery snapshots exist | Recovery/readiness functionality | NEEDS_PROVIDER_VERIFY; sensitive-data handling/policy must explicitly cover this |
| Chat/messages | COLLECTED, USER-PROVIDED | `/api/social/send`; chat text stored with user/channel/context | Social communication | LOCAL/SAME-ORIGIN observed; provider verify for future voice/video transport |
| Media comments/reactions | COLLECTED, USER-PROVIDED/INTERACTION | Comments/reactions persisted | Social/media functionality | LOCAL/SAME-ORIGIN observed |
| Media viewing activity | COLLECTED, DERIVED/INTERACTION | Media view records include user when available, watch seconds/completion | Product functionality/analytics | LOCAL/SAME-ORIGIN observed |
| Advertising interactions | COLLECTED, DERIVED/INTERACTION | Impression/click events contain campaign, placement, session identifiers | Ad delivery, frequency/yield analytics | NEEDS_PROVIDER_VERIFY; no external ad network destination established by current source scan |
| Sensitive-trait ad targeting | POLICY-PROHIBITED IN SOURCE | Ads service states health, religion and other sensitive traits are not targeting inputs; protected contexts defined | Safety/compliance control | Must be re-verified when external ad provider is configured |
| Device/advertising identifier | NOT OBSERVED | No Android Advertising ID path established in current evidence; activity uses a generated sensor nonce and ads use app session id | N/A | Re-scan dependencies/providers before final submission |
| Authentication/session data | COLLECTED/DERIVED | Login/session mechanisms present | Authentication/security | NEEDS_PROVIDER_VERIFY for any external identity provider added later |

## Release blockers derived from the matrix

1. **Permission minimization decision:** CAMERA, RECORD_AUDIO and location permissions are currently native-capable but browser-blocked/unused by the inspected runtime. Before final AAB, either remove permissions not required for this release or activate only the intended feature with accurate disclosure and tests.
2. **Third-party/provider verification:** object storage, TURN/WebRTC, ads, analytics, identity and AI/provider configurations must be inspected when production providers are selected. Current local/same-origin evidence cannot be generalized to future providers.
3. **Legal-resource gate:** standalone Privacy, Terms, account-deletion and `/.well-known/security.txt` resources are absent from canonical runtime and cannot remain SPA fallbacks.
4. **Account deletion:** public self-service deletion path is not verified and remains a Play release-readiness blocker.
5. **Sensitive-data policy:** recovery/health-related inputs and activity evidence require explicit retention/deletion/security treatment in final policy text.
6. **Final Play Console form:** must be completed only from the final signed-release/provider configuration and requires non-delegable legal/owner acceptance where Google requires it.

## Current safe release posture

No production signing, Play upload, Cloudflare production cutover, Solana/token financial action, canonical archive overwrite/delete, or THF/WAVE file mixing was performed while producing this matrix.