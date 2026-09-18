# Media 3.0 standalone — release status (2026-09-18)

## Verified now
- Backend tests: 9 passed.
- Android compile/target SDK: 36; min SDK: 26.
- Android package: com.topherofit.media (debug artifact uses .debug suffix).
- Android version: 3.0.0-standalone-rc1 / versionCode 30001.
- Credential Manager integration: code compiles with androidx.credentials 1.6.0 and googleid 1.2.1.
- Google Android server exchange uses a one-time server nonce and server-side ID-token verification.
- Server actions use authenticated Media session identity; caller-supplied user IDs are not trusted.
- THF Pass runtime handoff removed from Media.
- Media backend runs as an isolated systemd service on 127.0.0.1:8102.
- WAVE remains isolated on its existing port/process.

## Staging evidence
- HTTPS staging URL: https://flashers-sentence-cant-alone.trycloudflare.com
- External /health: PASS.
- Current staging debug APK SHA-256:
  de2f5e379b50793a967c7c6c3996e4f05ca401c725ea1f1027f1ae68a78ff11a

## External configuration still required
- Google OAuth client for Media: not present in the build/runtime environment.
- Stable Cloudflare named tunnel/domain or Cloud Run deploy permission: not present.
- Google Play Console/API authorization and upload signing material: not present.
- Physical Android device installation/smoke test: not yet executed.

The trycloudflare URL is staging only and has no production uptime guarantee.
