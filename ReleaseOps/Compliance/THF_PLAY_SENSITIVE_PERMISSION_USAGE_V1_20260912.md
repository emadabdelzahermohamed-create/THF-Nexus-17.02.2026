# THF Play Sensitive Permission Usage V1 — PASS

Date: 2026-09-12
Scope: THF Nexus Suite Android native wrapper only. WAVE_MAWJA excluded and untouched.
Execution: GitHub Actions -> GCP WIF -> IAP -> thf-wave-builder.
Run: 34697407569
Job: 103563152350
Workflow fix commit: 23e2f14261ae24290025a5330361ad56e389fe9b

## Result

- Gate: PASS
- Source tree deterministic SHA-256: `46eca5adaef95d551e90723f87698100dbe242f51cd28186480b3215a2a54942`
- THF/WAVE source isolation: PASS
- Mutation: FALSE
- Production signing: FALSE
- Play upload: FALSE
- Cloudflare production cutover: FALSE
- Solana financial action: FALSE

## Sensitive permission usage evidence

The Android wrapper does not merely declare the sensitive permissions; the native WebView bridge contains explicit runtime handling for them in `app/src/main/java/com/thf/topherofit/MainActivity.java`:

- Camera: `PermissionRequest.RESOURCE_VIDEO_CAPTURE` is mapped to `Manifest.permission.CAMERA` and requested through Android runtime permissions when absent.
- Microphone: `PermissionRequest.RESOURCE_AUDIO_CAPTURE` is mapped to `Manifest.permission.RECORD_AUDIO` and requested through Android runtime permissions when absent.
- Location: `onGeolocationPermissionsShowPrompt` checks `ACCESS_FINE_LOCATION` and requests both fine and coarse location when missing.
- The first web permission request is denied while Android permission is being requested, preventing implicit grant before OS authorization.

These are technical use paths. They prove that camera, microphone and location capabilities can be requested by the trusted web content; they do not by themselves prove server-side collection, sharing, retention or purpose.

## WebView security evidence

Observed controls:

- JavaScript enabled for the app WebView.
- File access disabled.
- Web contents debugging enabled only under `BuildConfig.DEBUG`.
- A custom `WebViewClient` controls URL navigation.
- TLS certificate errors call `handler.cancel()`; no SSL bypass was observed.
- Release builds require `APP_BASE_URL` to begin with HTTPS.
- Release fallback value is `https://invalid.example`, so a missing production URL cannot silently become cleartext production traffic.

## Native endpoint evidence

- Debug default: `http://10.0.2.2:8000`.
- Release endpoint is injected using `APP_BASE_URL`.
- `BUILD_RELEASE.sh` also enforces an HTTPS production URL.

## Compliance consequence / next gate

Google Play Data Safety mapping must now reconcile these native capability paths with actual web/runtime code paths and backend endpoints before any disclosure is finalized. Next reversible gate: inspect `clients/web` and backend runtime for camera/microphone/location invocation, upload/transmission endpoints and purpose signals, without changing production state.

Policy blockers remain independent: standalone Privacy/Terms/account-deletion/security.txt resources and a public account-deletion workflow still require implementation/verification before release readiness.
