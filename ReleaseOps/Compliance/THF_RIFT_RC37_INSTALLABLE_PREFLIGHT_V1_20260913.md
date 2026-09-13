# THF Rift RC37 Installable QA Preflight V1 — 2026-09-13

Status: PASS-PREFLIGHT
Scope: THF Rift only. WAVE_MAWJA isolated and untouched.

## Evidence

- GitHub Actions run: `34736170994`
- Job: `inspect` (`103667891583`)
- Result: SUCCESS
- Access path: GitHub OIDC/WIF -> GCP -> IAP -> `thf-wave-builder`
- Persistent cloud keys: NOT USED
- Evidence artifact: `THF-Rift-RC37-INSTALLABLE-PREFLIGHT`
- Artifact ID: `10310788361`
- Artifact ZIP SHA-256: `885513d9d71d0c87cb2f067bc3201e9c3d5bbe7d313ca6417c28c34f87450dc9`

## Canonical source verification

- Archive: `THF_Rift_v4.7.1_RC37_HUMAN_RELOAD_TIMING_PARITY_CUMULATIVE_SOURCE.zip`
- Expected SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- SHA before inspection: MATCH
- SHA after inspection: MATCH
- ZIP integrity: PASS
- Source size: `108758664` bytes
- Canonical source mutation: FALSE

## Build identity discovered

Project root inside archive: `THF_Nexus_Arena_Core`

Android project:
`THF_Nexus_Arena_Core/android-arena`

Godot metadata:
- `project.godot` present
- `export_presets.cfg` present
- preset: `Android AAB Candidate`
- package/name: `THF Rift`
- package/unique_name: `com.topherofit.thf.rift`
- package/signed: `false`

Android metadata:
- namespace/package: `com.topherofit.thf.rift`
- versionCode: `42071`
- versionName: `4.7.1-rc37`
- launcher activity exported: true

Declared permissions observed in canonical manifest:
- `android.permission.INTERNET`
- `android.permission.VIBRATE`
- `android.permission.ACCESS_WIFI_STATE`
- `android.permission.CHANGE_WIFI_MULTICAST_STATE`

The preflight does not by itself assert that every declared permission is required at runtime; permission minimization remains a separate compliance concern.

## Isolation and safety

- Rift/WAVE isolation: PASS
- WAVE files touched: FALSE
- Production signing performed: FALSE
- Google Play upload performed: FALSE
- Cloudflare production cutover performed: FALSE
- Solana/token financial action performed: FALSE
- Destructive cloud mutation performed: FALSE

## Next step

Build an installable Rift RC37 QA APK from a fresh disposable extraction of the pinned canonical source. Verify package/version, APK signature, zip alignment, SHA-256, and canonical source SHA before/after. QA/debug signing only; no production signing or Play upload.
