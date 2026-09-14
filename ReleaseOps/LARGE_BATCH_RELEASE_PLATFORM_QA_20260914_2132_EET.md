# THF + WAVE Large-Batch Release / Platform / QA Checkpoint — 2026-09-14 21:32 EET

## Scope
Hourly large-batch release/platform/QA pass across THF + WAVE, preserving project isolation and Mobile Real-Function Release Policy fail-closed semantics.

## Starting authority
- Prior main checkpoint: `99a4fc78138f9b2c8bcab3e3ff85e8889c87aa69`.
- Prior checkpoint recorded global artifact-size policy PASS and retained the exact Rift RC41 staging blocker.
- No older Rift source was promoted.

## Repaired release/tooling defect
Latest failed Pulse run `34880421527` had a successful Android build but failed the retrieval gate because the workflow still required the retired evidence field:
`under_100MiB=PASS`.

The build script had already migrated to:
- `artifact_size_policy=TELEMETRY_ONLY_NO_ARBITRARY_CAP`
- `validated_content_pruned_for_size=FALSE`

The retrieval workflow was therefore stale and produced a false-negative after a valid QA build.

Repair commit:
`ef8af2f4ce2b87d65483b872b6389830746285cb`
`fix(pulse): align retrieval gate with telemetry-only size policy`

The repaired retrieval gate now:
- requires `artifact_size_policy=TELEMETRY_ONLY_NO_ARBITRARY_CAP`;
- requires `validated_content_pruned_for_size=FALSE`;
- explicitly rejects reappearance of `under_100MiB=`;
- retains targetSdk 36, SHA-256, physical-device pending, and NOT_FINAL checks.

## Verification
### Global size-policy gate
- Run: `34881132833`
- Result: SUCCESS
- Head: `ef8af2f4ce2b87d65483b872b6389830746285cb`

### Pulse MPFB Motion Phone QA
- Run: `34881132830`
- Result: SUCCESS
- WIF authentication: PASS
- GCP setup: PASS
- IAP builder staging: PASS
- Android build: PASS
- Candidate retrieval/integrity: PASS
- Artifact upload: PASS
- targetSdk: `36`
- package: `com.topherofit.thf.pulse.debug`
- version: `4.1.3-motionqa1-debug`
- versionCode: `41301`
- APK size bytes: `20468010`
- APK SHA-256: `93e5dbf46215e01670aa1eedc51b06ba3e880f2d86950847a7a4f96d908aba47`
- Avatar SHA-256: `4f556086e1b7149f6c958f1f399f4368f6ad9b76afd3503d6f848eeeb7bea24f`
- Artifact ID: `10362882533`
- Artifact ZIP SHA-256: `1494fa15714eba3cafaaba82db0c2ff389426030111f4cbb4ceb5d84eba013ce`

## Mobile Real-Function truth boundary
This remains QA-only and is not a production release candidate:
- `backend_features=NOT_ACCEPTED_IN_THIS_VISUAL_QA`
- `physical_device_status=PENDING`
- `final_or_play_ready=FALSE`
- no physical install/launch/touch/orientation/background-resume/offline-network/core-journey/crash-free evidence was fabricated;
- no production signing, signed AAB, Play approval, or production deployment is claimed.

## Outstanding release blockers
### Rift / games
Exact Rift RC41 source bytes remain unavailable to the automated builder/materializable source path according to the immediately preceding authoritative checkpoint. No RC37/older artifact is promoted as RC41. Physical-device game evidence remains mandatory.

### GitHub governance
`main` is currently unprotected and required status-check enforcement is off. Repository rulesets list is empty. A repository owner/admin governance action is still required to enforce protected `main` and required release gates. No unsupported administration mutation was attempted.

### WAVE
WAVE remained isolated and unmodified in this pass. No THF repair was applied to WAVE and no WAVE source/runtime authority was substituted.

## Overall release decision
`NOT_FINAL / NO_GO`

The successful CI/build evidence does not supersede physical-device evidence, stable production HTTPS/WSS authority, production signing/Play Internal acceptance, legal/ownership actions, or exact authoritative source requirements.

Checkpoint body SHA-256 (content above this line): `96d28a911621bc29a57ab111ce18a2a1b2f7b91cd770d2a2c793205c8c1c98ed`
