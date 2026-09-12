# THF Versioned Permission-Min Source V1 — 2026-09-12

Status: PASS
Scope: THF Android release-source preparation only. WAVE_MAWJA excluded.

## Evidence

- GitHub Actions run: `34708908483`
- Workflow commit: `59842ab7fc2230ae75960dd67e8921efe5fd9ce7`
- Authentication path: GitHub OIDC/WIF -> GCP -> IAP/OS Login
- Persistent cloud keys: not used
- Canonical Android source path: `$HOME/thf-runtime-s1/outer/01_THF_NEXUS_SUITE/ANDROID_PLAY_SOURCE`
- Canonical source SHA-256 before: `46eca5adaef95d551e90723f87698100dbe242f51cd28186480b3215a2a54942`
- Canonical source SHA-256 after: `46eca5adaef95d551e90723f87698100dbe242f51cd28186480b3215a2a54942`
- Canonical unchanged: PASS
- Versioned candidate path: `$HOME/thf-release-candidates/permission-min-v1-34708908483`
- Versioned candidate source SHA-256: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7`
- AndroidManifest XML parse: PASS
- THF/WAVE isolation: PASS

## Candidate change

The versioned candidate removes only the currently latent Android permissions already proven removable by the prior API-36 build gate:

- `android.permission.CAMERA`
- `android.permission.RECORD_AUDIO`
- `android.permission.ACCESS_FINE_LOCATION`
- `android.permission.ACCESS_COARSE_LOCATION`

The canonical source archive/tree was not modified, overwritten or deleted.

## Deliberately not performed

- No production API hostname was embedded.
- No production signing was performed.
- No Google Play upload or publishing action was performed.
- No Cloudflare production cutover was performed.
- No Solana/token action was performed.
- No WAVE source or runtime was copied into the THF candidate.

## Next release dependency

This candidate is now ready to become the source for final Core/Terra/Rift production-configured builds after an explicitly authorized stable production API hostname is frozen. Until that happens, final production AAB rebuild/signing remains blocked by policy rather than tooling.
