# THF + WAVE Large-Batch Release Checkpoint — 2026-09-14 18:45 EET

## Material repairs
- Repaired invalid YAML in `.github/workflows/thf-vault-signal-api36-candidates.yml`; Python heredoc is again inside the shell block.
- Hardened the same gate against `set -o pipefail` SIGPIPE false negatives by replacing `find | head` with `find -print -quit` and materializing `strings` output before grep.
- No release criterion was weakened.

## Validation
- Vault/Signal exact-source workflow run `34862678706` passed WIF auth, gcloud setup, IAP staging, exact-source build, provenance retrieval and the Mobile Real-Function Release Policy step.
- The policy correctly keeps both generated wrapper-shell APKs rejected as release authority.
- Follow-up workflow run `34862996122` was triggered from the pipefail-hardening commit and is serialized behind the previous run.

## Authority truth
- Latest authoritative lineage reconciliation remains fail-closed: Spark/Rush source authority unresolved there; Vault/Signal APK authority unresolved there.
- The older physical-device registry contains candidate mappings that conflict with the later lineage reconciliation and must not override the later fail-closed lineage authority.
- Vault/Signal exact-source build audit classifies their ~37 KB / seven-entry WebView APKs as `REJECT_WRAPPER_SHELL_ONLY`, with no APK promotion, no physical-device eligibility, no production signing and no FINAL/PLAY_READY.
- Terra V4 remains QA-only package `com.topherofit.thf.terra.phoneqa`, targetSdk 36, Godot 4.7.2, with genuine offline local exploration wiring but no physical-device/FPS/RAM/thermal evidence and no production promotion.

## WAVE isolation
- WAVE was not modified in this batch.
- No SSH/OS Login weakening, older-source substitution, Cloudflare cutover, production deployment, signing, Play submission or token-finance mutation was performed.

## Remaining non-delegable / external blockers
- Exact-candidate physical Android device sessions and evidence.
- Production signing key / Play App Signing / Internal Track actions.
- Stable trusted production HTTPS/WSS and real health/auth/session/federation proof.
- Owner/admin/legal acceptances where required.
- Authorized canonical WAVE workspace access or cryptographically bound service-account-owned release workspace.

## Release truth
`NOT_FINAL / NO_GO`

## Evidence body SHA-256
`30688fcaee8fe9807e11ac280dd90ec2e2c6963f78e38ea2e7760bb5a81c867a`
