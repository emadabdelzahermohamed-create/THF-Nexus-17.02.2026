# THF Data Safety Runtime Flow V1 — PASS

Date: 2026-09-12
Scope: THF Nexus runtime only. WAVE_MAWJA excluded and untouched.
Execution: GitHub Actions -> GCP WIF -> IAP -> thf-wave-builder.
Run: 34697483514
Job: 103563351758
Workflow commit: 9100c37aea5e5b22ac8b286d200a82be1816c1b1
Scanned source-set SHA-256: `19a03999aaa58e469d378f3db24d976e678a002abd3a8ec4888365a12bfc9653`

## Result

- Gate: PASS
- THF/WAVE isolation: PASS
- Mutation performed: FALSE
- Production signing performed: FALSE
- Play upload performed: FALSE
- Cloudflare production cutover performed: FALSE
- Solana financial action performed: FALSE

## Data-flow facts

### User photos and media
- The user-facing web UI allows explicit image/video file selection for media publishing.
- Selected media is POSTed to same-origin `/api/media/upload`; the backend streams the bytes into bounded local runtime media storage, computes SHA-256 and stores media metadata in the database.
- Avatar Studio allows explicit image selection. The browser uses `FileReader`, converts the selected image to a data URL, and sends `photo_base64` to same-origin `/api/avatar/generate`.
- Avatar records include a photo SHA-256/reference path plus generated avatar metadata.

Technical classification: user-selected photos/media are collected by the THF backend when these features are used. This is not a statement about external third-party sharing.

### Fitness/activity/recovery
- `/api/activity/submit` transmits activity inputs including duration, distance, GPS-distance field, steps, cadence, device-integrity value and a client-generated sensor nonce.
- Workout sessions and sets are submitted and stored.
- `/api/recovery/readiness` submits sleep hours, soreness, fatigue and resting-heart-rate delta.

Technical classification: fitness/activity and recovery/health-related inputs are collected by the THF backend when the user uses these features.

### Social and user-generated content
- Proximity chat text is submitted to `/api/social/send` and stored with user/channel and in-world x/y/district context.
- `/api/social/position` submits the avatar/player position in the virtual world. This is in-game spatial state and must not be represented as device GPS merely because it uses x/y fields.
- Media comments, reactions and view events are persisted.

### Ads/app interactions
- The client records same-origin ad impression/click events including campaign, placement and session identifiers.
- Current source states that ad targeting must not use health data, religion or other sensitive traits, and defines protected contexts.
- This scan did not establish an external advertising-network destination. Provider/configuration verification remains required before any final “shared with third parties” disclosure.

## Camera / microphone / device-location capability status

Native Android code contains OS permission bridges for CAMERA, RECORD_AUDIO and coarse/fine location. However, the current THF HTTP runtime emits:

`Permissions-Policy: camera=(), microphone=(), geolocation=()`

The current web-source scan also found no direct `getUserMedia`, `MediaRecorder`, `navigator.geolocation`, `watchPosition` or `getCurrentPosition` invocation. Therefore the present runtime evidence is:

- Camera live capture: capability present natively, but browser runtime access currently blocked / no direct live capture invocation observed.
- Microphone live capture: capability present natively, but browser runtime access currently blocked / no direct live capture invocation observed.
- Device geolocation: capability present natively, but browser runtime access currently blocked / no direct browser geolocation invocation observed.
- File/photo/video picker: active and used for explicit user-selected media/avatar files; this is distinct from live camera/microphone capture.

Release decision needed before final Play declaration: either remove permissions that are not intended for this release, or activate the corresponding feature deliberately and disclose it accurately. Do not infer current GPS collection solely from the manifest permission or the in-world x/y position data.

## Network/security facts

- Web/API traffic shown by the current client is same-origin.
- Current CSP has `connect-src 'self'`.
- Production Android release URL is separately enforced as HTTPS by the native wrapper/build gate.
- TLS failures are fail-closed in the native WebView wrapper.

## Remaining compliance blockers

1. Build a technical Play Data Safety matrix from these verified facts; keep unknown third-party/provider sharing explicitly unresolved until provider configuration is inspected.
2. Resolve latent CAMERA/RECORD_AUDIO/LOCATION permissions: remove unused release permissions or implement/enable the intended capability and disclose it.
3. Standalone Privacy, Terms, account-deletion and `/.well-known/security.txt` resources remain missing from the canonical runtime.
4. A public account-deletion workflow still requires implementation and verification.
5. Final legal/Play Console representations remain user/legal-acceptance gates and must not be auto-submitted.

No canonical source archive was overwritten or deleted.