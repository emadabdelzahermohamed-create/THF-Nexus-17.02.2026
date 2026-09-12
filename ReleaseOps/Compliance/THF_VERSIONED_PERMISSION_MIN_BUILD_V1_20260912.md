# THF Versioned Permission-Min Build V1 — 2026-09-12

Status: PASS
Scope: THF Android release-source candidate only. WAVE_MAWJA untouched.

## Provenance

- GitHub Actions workflow: `THF Versioned Permission-Min Build V1`
- Run: `34709148029`
- Workflow commit: `32436f38014db9e4820bdf460f026099c39fda23`
- Access path: GitHub OIDC/WIF -> GCP -> IAP -> `thf-wave-builder`
- Persistent cloud key: NOT USED
- Candidate path: `/home/sa_115575029018678177962/thf-release-candidates/permission-min-v1-34708908483`
- Expected candidate source SHA-256: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7`

## Verification

- Candidate SHA-256 before build: `36b049848fb2002bc11358290fb6d95451d9c407055bb140cba2eb595888f3b7` — PASS
- AndroidManifest XML parse — PASS
- Sensitive latent permissions absent from versioned candidate source — PASS:
  - `android.permission.CAMERA`
  - `android.permission.RECORD_AUDIO`
  - `android.permission.ACCESS_FINE_LOCATION`
  - `android.permission.ACCESS_COARSE_LOCATION`
- Gradle distribution SHA-256 verification — PASS
- Android API 36 platform presence — PASS
- Debug build — PASS
- Merged debug manifest permission minimization — PASS
- Release test AAB build — PASS
- lintVital release tasks — PASS
- Candidate SHA-256 after build unchanged — PASS
- THF/WAVE isolation — PASS

## Build outputs

- Debug APK SHA-256: `44b5c2f2d3b398768bf937487ae86d87d06702d715b94e900dea27ea82cc1484`
- Test unsigned AAB SHA-256: `429b6e982c6c1290033b0b69a2f7433d69eee208b03d6a20c59c376a2a818e30`
- AAB signing state: `UNSIGNED-AS-EXPECTED`

The test AAB intentionally used the reversible test-only `THF_TEST_UNSIGNED=1` build path. No production signing credentials were loaded.

## Safety / actions deliberately not performed

- Production signing: NOT PERFORMED
- Google Play upload/publishing: NOT PERFORMED
- Cloudflare production cutover: NOT PERFORMED
- Solana/token financial action: NOT PERFORMED
- Canonical source archive overwrite/delete: NOT PERFORMED
- WAVE source/runtime mutation: NOT PERFORMED

## Findings

The versioned permission-minimized source is buildable against API 36 and produces the same deterministic QA APK/AAB hashes as the earlier isolated permission-minimization candidate. The source checksum is unchanged by the build.

The build logs also report Gradle/deprecation warnings (Gradle 9 compatibility warning and deprecated Java API use in `MainActivity.java`). These are technical-debt findings, not current build blockers; they should be addressed before a future Gradle 9/toolchain migration.

## Next highest-priority unblocked work

1. Continue Google Play compliance/readiness work that does not require production credentials or public cutover: independent Privacy/Terms/account-deletion/security.txt resources and final Data Safety facts.
2. Preserve this versioned candidate until a stable production API hostname is authorized/frozen.
3. Rebuild final Core/Terra/Rift production-configured AABs only after that hostname is frozen.
4. Production signing and any Play upload remain blocked pending exact authorization.
5. WAVE remains independently blocked on recovery of the latest full canonical WAVE runtime/source; do not substitute older RC material.
