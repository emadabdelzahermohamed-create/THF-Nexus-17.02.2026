# THF Apps APPS-RC3 exact-candidate attempt — truthful checkpoint

Date: 2026-09-13
Scope: Pulse, Forge, Echo, Codex, Spark, Rush, Vault, Signal, Command. Core RC6 was intentionally not rebuilt because its current exact-candidate gate is already proven and there is no regression evidence. THF Pass remains backend/SDK/federation-only.

## Execution

A new QA-only, reversible GitHub Actions lane was added at `.github/workflows/thf-apps-rc3-exact-candidate-large-batch-v1.yml` and executed as workflow run `34767185096` from commit `0618ba774bc51d1d68c87d4fee3e3fe5629502e7`.

The lane authenticated through existing WIF, connected to the existing isolated GCP builder, searched builder-accessible ZIPs by **content SHA-256 rather than filename**, and required the exact APPS-RC3 source hashes recorded in the prior authoritative RC3 checkpoint. It was prepared to clean-extract, `assembleRelease`, QA-sign, zipalign, inspect package identity, verify targetSdk 36, verify signature/non-debuggable state, and bind each result to an APK SHA.

The workflow completed successfully as a diagnostic/truth gate. Artifact `THF-APPS-RC3-EXACT-QA-CANDIDATES-V1` (artifact id `10320602343`) has archive digest `sha256:c4ade3ef9ad03c236366811b6db4a9c7cad771228ca1380eef3c0882e5a72fae`.

## Result

No exact RC3 source archive was present in the GCP builder-visible filesystem for any of the nine required SHA-256 values. Therefore **zero APK candidates were built**, and no package/runtime/device PASS is inferred.

| App | Required APPS-RC3 source SHA-256 | Result |
|---|---|---|
| Pulse | `71a16804e7c138535bb373263ae4374d8a5eef410ffe83b165472c684b6c8b10` | SOURCE_MISSING |
| Forge | `0f7a416a9e14af9dbb3cdcb26bfb891e0c680d4a33a73d60601eda215e697e51` | SOURCE_MISSING |
| Echo | `40a197b60563e560cab93ba0a64c859d9b650da222fdaec933993977d63902ab` | SOURCE_MISSING |
| Codex | `3d60cc550732468c89fe120f552def53ac798646d065e94efa153f8979e15b1e` | SOURCE_MISSING |
| Spark | `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0` | SOURCE_MISSING |
| Rush | `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b` | SOURCE_MISSING |
| Vault | `7a2ba4236a0c42d2521fa2eb2c2d7108ceba0d2929ebdf68959a6eacbce4a793` | SOURCE_MISSING |
| Signal | `51d7ce44fed24f7490973bcc7e019a8430157c4d5bfa1541e7cb590b0b7957c0` | SOURCE_MISSING |
| Command | `f7da9039041b8142d795e96934b95f00b83ac8fb5e3d6f5d9bfbff0aeb2eb408` | SOURCE_MISSING |

The prior RC3 checkpoint says these cumulative archives were stored in the THF Nexus Overnight persistent workspace. The connected Drive metadata search did not resolve those archives by RC3/Pulse terms, and the builder did not contain them by exact hash. The autonomous build lane will not substitute APPS-RC2 or any similarly named archive.

## Exact unblock action

Stage the nine **exact hash-matching APPS-RC3 source archives** into a location readable by the existing isolated builder, or expose their exact private Drive file IDs to the existing WIF service account. No production signing, paid spend, owner identity verification, or public rollout is required for this unblock.

## Additional hardening completed while the candidate lane ran

- `portfolio_readiness_v1.json` was advanced from APPS-RC2 to the authoritative APPS-RC3 source SHAs and truthful source-level readiness.
- Portfolio Readiness Gate validated the updated matrix successfully in workflow run `34767216170`.
- Added `validate_mobile_candidate_acceptance.py`, a fail-closed exact-candidate/physical-device acceptance validator.
- Added a non-passing evidence template and regression tests covering SHA binding, HTTPS/WSS non-loopback requirements, real offline semantics, device touch/layout/background/offline/core-journey/crash-free evidence, accessibility/Data Saver/RTL/localization/rollback, and game performance evidence when applicable.
- Updated `.github/workflows/thf-portfolio-readiness-gate.yml` to compile/test both readiness and device-acceptance validators and prove that the blank template cannot accidentally PASS.

## Truth boundary

No ordinary app in this RC3 batch is FINAL/PLAY_READY. A source-level hardening PASS is not a compiled candidate PASS. Physical-device acceptance remains mandatory and must be bound to the exact eventual APK SHA. Signal/Command remain private/internal. THF Pass remains backend/SDK-only. Production signing and public Play rollout remain outside autonomous execution.
