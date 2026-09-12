# Core RC6 WIF-safe retry checkpoint — 2026-09-12

Scope: THF Core only. Terra/Rift/WAVE source untouched.

## Prior blocker
- GitHub Actions run `34651159978` failed at WIF authentication before any GCP build step.
- Root cause class matches the previously observed long-ref `google.subject` WIF limit; no source/build failure was established by that run.

## Remediation
- Created short WIF-safe branch `c/r6` from exact Core RC6 gate commit `57843bd7ae36db908532cf9dfc587dbb68b35387`.
- Added isolated workflow `thf-core-rc6-unsigned-build-v2.yml` on commit `4a38c1b6451c523bfc1f29a7607bab752f38d227`.
- Canonical Core RC6 source remains read-only: `THF_Core_RC6_ANDROID_NATIVE_I18N_RELEASE_CUMULATIVE_SOURCE.zip`.
- Expected source SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`.
- Production signing environment variables are explicitly unset by the gate.

## Live result at checkpoint creation
- New run: `34678895451`.
- Checkout: PASS.
- WIF authentication: PASS.
- gcloud setup: PASS.
- Exact-source SHA/API36/Gradle unsigned build and package inspection: IN PROGRESS.

## Safety boundary
- No production signing.
- No Google Play upload/publish.
- No Cloudflare cutover.
- No Solana transaction.
- No canonical archive overwrite/delete.
- WAVE_MAWJA untouched.

## Next
Consume run `34678895451`; if build/package inspection passes, record APK/AAB/evidence SHA-256 and close Core RC6 unsigned/API36 gate. If it fails, fix only the evidence-backed tooling/source issue and rerun on the same isolated lane.
