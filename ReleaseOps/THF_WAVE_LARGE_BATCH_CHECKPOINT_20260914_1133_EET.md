# THF + WAVE Large-Batch Release Checkpoint — 2026-09-14 11:33 EET

## Scope inspected
- Latest ReleaseOps checkpoints, current `main`, recent GitHub Actions runs, exact app/game candidate SHAs, runtime truth and WAVE RC14 blocker were reviewed before mutation.
- THF and WAVE were kept isolated.
- No production signing, Play publication, Cloudflare production cutover, Solana/token mutation or physical-device/GPU evidence was fabricated.

## Material repair: THF App Physical Device Evidence V6
Apps V5 required per-check raw probes but did not require touch/orientation/background-resume claims to be proven by one immutable lifecycle transcript. Games V10 already had that stronger continuity property.

V6 now requires one non-empty SHA-256-bound ADB lifecycle transcript from the same declared physical-device session and binds it to:
- exact session ID;
- exact package ID;
- exact candidate APK SHA-256;
- authoritative source SHA-256;
- approved method `adb-shell-lifecycle-transcript-v1`;
- observed touch;
- portrait and landscape;
- responsive-layout and safe-area observations;
- background/resume with the same numeric PID before and after;
- strict observation interval contained inside the declared phone session;
- continued V5 semantic/raw-probe chain and V4 crash-free logcat chain;
- explicit `final_or_play_ready=false`.

Files:
- `ReleaseOps/mobile/validate_app_device_evidence_v6.py`
- `ReleaseOps/mobile/test_validate_app_device_evidence_v6.py`
- `.github/workflows/thf-app-physical-device-evidence-tooling-v6.yml`

Commits:
- `48f01ba934d7400cbe5428fe49ae34e843f42b14` — validator V6
- `112d09fe5100de9e784cef03e420413b987ff5d2` — V6 regressions
- `5573fadb859d49f3cbed9ef518a72d264cf6359b` — permanent CI gate

## CI evidence
Workflow run `34823252920` — SUCCESS.
- V2–V6 Python compilation: PASS
- V2–V6 regression suites: PASS
- authoritative pending-truth gate: PASS
- `LIFECYCLE_TOUCH_ORIENTATION_SINGLE_TRANSCRIPT_REQUIRED=TRUE`
- `BACKGROUND_RESUME_SAME_PID_REQUIRED=TRUE`
- `EXACT_CANDIDATE_AND_SOURCE_LINEAGE_REQUIRED=TRUE`
- `PHYSICAL_DEVICE_STATUS=PENDING`
- `FINAL_OR_PLAY_READY=FALSE`

## Exact candidates
No app/game APK bytes or source candidates were rebuilt or changed in this batch. Existing exact candidate authority therefore remains unchanged.

## Runtime / endpoint truth
Apps Factory remains fail-closed:
- configuration URL bindings are not THF backend proof;
- `BACKEND_HEALTH_AUTH_PROOF=FALSE`;
- `NETWORK_RELEASE_READY=FALSE`;
- a stable externally reachable trusted-TLS THF backend/Pass endpoint with real health/auth/session/federation evidence is still required.

## WAVE RC14
WAVE remains isolated and unchanged. Existing evidence still shows:
- WIF authentication works;
- gcloud/IAP/SSH reachability works;
- OS Login maps CI to service-account user `sa_115575029018678177962`;
- canonical `/root/workspace/wave-mawja` cannot be safely read by unattended CI;
- blocker remains `CANONICAL_ROOT_OS_LOGIN_REQUIRED`.

Safe remaining owner/admin options are still:
1. narrowly-scoped `roles/compute.osAdminLogin`; or
2. preferably a service-account-owned release workspace cryptographically bound to canonical `/root/workspace/wave-mawja`.

Do not disable OS Login, weaken SSH or grant broad project Owner merely to bypass this gate.

## Release truth
Overall status remains `NOT_FINAL / NO_GO`.
Still required before final promotion:
- exact-candidate physical-phone evidence for every THF app/game;
- install/launch/touch/layout/orientation/background-resume/offline-network/core journey/crash-free acceptance;
- games additionally: avatar/player load, movement/camera/gameplay plus FPS/RAM/thermal;
- stable trusted production/staging HTTPS/WSS backend evidence;
- production signing and signed AAB;
- Play Internal acceptance;
- FCM/APNs real-device receive/tap/background-resume evidence where applicable;
- WAVE canonical-source access and its own real candidate/runtime/device evidence.

Rollback is limited to the three V6 commits above; no product APK/source bytes were changed.

Body SHA-256: `5e4cb483ad9530a52f7428ebfce8fab3f976801a53fb006b5dd66a12543d4143`
