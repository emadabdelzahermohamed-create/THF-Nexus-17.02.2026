# THF Google Play Data Safety Prefill — V3 — 2026-09-13

Status: TECHNICAL PREFILL ONLY — NOT A LEGAL DECLARATION OR PLAY CONSOLE SUBMISSION
Scope: current THF Android release-candidate behavior. WAVE_MAWJA is excluded and remains technically isolated.

This file converts the verified technical evidence into a conservative Play Console preparation worksheet. Final answers must be rechecked against the production-configured, production-signed binaries and final provider contracts before submission.

## Candidate evidence incorporated

- API-36 Android candidate path is active.
- Permission-minimized candidate removes CAMERA, RECORD_AUDIO, ACCESS_FINE_LOCATION and ACCESS_COARSE_LOCATION.
- Core RC6 runtime-configured staging candidate: package `com.topherofit.thf.core`, APK SHA-256 `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`.
- Terra RC34 runtime candidate: package `com.topherofit.thf.terra`, APK SHA-256 `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7`.
- Rift RC37 runtime candidate: package `com.topherofit.thf.rift`, APK SHA-256 `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1`.
- Account deletion technical implementation is PASS-CANDIDATE.
- Independent `/privacy`, `/terms`, `/account-deletion` and `/.well-known/security.txt` technical resources are PASS-CANDIDATE; policy wording/production values still require owner/legal approval.

## Conservative data-type prefill

| Play-relevant data family | Technical answer for current candidate | Collection source | Sharing status from inspected configuration | Final-release action |
|---|---|---|---|---|
| Account identifiers / username | COLLECTED | User-provided + account/session processing | No external destination established in inspected candidate | Recheck final identity/provider configuration |
| Profile / preferences / locale / goals | COLLECTED | User-provided | No external destination established in inspected candidate | Confirm purposes and retention language |
| Photos | COLLECTED where user selects avatar/social media | User-provided | Same-origin/local path observed | Recheck final AI/object-storage/CDN providers |
| Videos | COLLECTED where user uploads social/media content | User-provided | Same-origin/local path observed | Recheck final object-storage/CDN/transcoding providers |
| Audio files | BACKEND CAPABILITY EXISTS; active Android UI collection not proven | Unknown/currently unproven | Not established | Do not declare active audio collection unless final UI/build exposes it |
| Health / fitness / activity | COLLECTED | User-provided and derived from sessions/evidence | No external destination established in inspected candidate | Legal/privacy wording must cover purpose, retention, deletion and security |
| Recovery/readiness inputs | COLLECTED | User-provided | No external destination established in inspected candidate | Treat as sensitive health-related data in policy review |
| Messages / chat | COLLECTED | User-provided | Same-origin observed | Recheck if external realtime/voice/video provider becomes active |
| App interactions / media viewing | COLLECTED | Derived from use | Same-origin observed | Confirm analytics purpose and provider destination |
| Advertising interactions | COLLECTED where ads/campaign features are active | Derived from use | No external ad-network destination established in inspected configuration | Recheck final ads/analytics SDK/provider configuration |
| Precise/approximate device location | NOT REQUESTED by versioned permission-minimized Android candidate | N/A | N/A | Fresh audit required if location is re-enabled |
| Live camera | NOT REQUESTED by versioned permission-minimized Android candidate | N/A | N/A | Fresh audit required if camera is re-enabled |
| Live microphone | NOT REQUESTED by versioned permission-minimized Android candidate | N/A | N/A | Fresh audit required if microphone is re-enabled |
| Advertising ID / device ad identifier | NOT OBSERVED in current evidence | N/A | N/A | Re-scan final dependencies and merged manifest |
| Authentication/session/security data | COLLECTED / DERIVED | Account security | No external IdP established in current inspected configuration | Recheck final identity provider and retention |
| Virtual-world/player coordinates | COLLECTED as in-app interaction data, not GPS | Derived from gameplay | Same-origin observed | Keep distinct from device location declaration |

## Play Console decision guardrails

- Do not answer `Not collected` for a data family merely because a specific screen was not exercised if source/runtime evidence proves collection elsewhere.
- Do not answer `Shared` solely because data is sent to THF's own backend. Sharing classification must be revisited if a third-party processor/provider receives the data in the final production configuration.
- Do not rely on the absence of Android permissions to conclude there is no file/media collection; user-selected files can still be collected through picker flows.
- Do not classify in-world/player x/y/district as device location/GPS.
- Sensitive-trait advertising remains prohibited by current source policy; any future ad provider must be audited before release.

## Resolved since Data Safety Matrix V2

1. Independent privacy/terms/account-deletion/security resource routing is technically implemented as a candidate rather than SPA fallback.
2. Authenticated self-service account deletion is technically PASS-CANDIDATE, including old-session rejection in the disposable E2E verification path.
3. Current Core/Terra/Rift runtime candidate APK identities and SHA-256 values are now locked in ReleaseOps evidence.

## Remaining blockers before final Play declaration

1. Owner/legal approval of Privacy Policy, Terms, deletion-retention wording and production security contact values.
2. Freeze the final production provider set: identity, object storage/CDN, AI, ads/analytics, TURN/WebRTC and any health/fitness processor.
3. Freeze the stable production API hostname after separately authorized Cloudflare production cutover.
4. Rebuild final production-configured AABs and repeat merged-manifest/dependency/data-flow inspection.
5. Recheck final production-signed binaries before Play submission.
6. Complete any non-delegable Play Console ownership/legal declarations by the account owner where required.

## Safety

No production signing, Play upload/publishing, Cloudflare production cutover, Solana/token financial action, destructive cloud change, canonical archive overwrite/delete, or THF/WAVE mixing is authorized or performed by this prefill.
