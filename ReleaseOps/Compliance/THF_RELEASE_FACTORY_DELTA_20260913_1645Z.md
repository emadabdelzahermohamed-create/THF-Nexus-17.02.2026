# THF Release Factory Delta — 2026-09-13 16:45Z

Status: NO PUBLIC ROLLOUT / fail-closed.

## Material changes after the 16:41Z checkpoint
- Terra/Rift staging network-authority workflow run 34769077363 completed PASS with WIF/GCP/IAP, exact-source binding, targetSdk 36/mobile contract, fail-closed protected unauthenticated action, and canonical archives unchanged. This resolves the staging network-authority gate only; it does not establish a stable production endpoint or physical-device acceptance.
- Spark/Rush local-practice workflow run 34769249423 completed FAIL. The disposable Spark overlay changed its Gradle file and asserted canonical package `com.topherofit.thf.spark`, but the built APK still resolves to `com.topherofit.thf.spark.debug` / versionName `3.6.2-debug`; build itself was successful, targetSdk 36, and APK v2 signature verification passed. The gate correctly stopped before Rush and final acceptance. Artifact digest: sha256:70e4b1328126df82e0eff904d1e09996f10f31171bf6ae3c8a63e44852c2a272.
- New Terra/Rift staging QA APK workflow run 34769372469 failed at workflow startup with zero jobs, so it is treated as a workflow-definition/startup blocker and no APK evidence is claimed from that run.
- WIF/GCP builder path remains healthy in workflows that actually start.
- WAVE RC14 canonical source access blocker is unchanged: CI OS Login identity cannot read `/root/workspace/wave-mawja`; no broad permission escalation or OS Login weakening was attempted.

## Hard blockers retained
- Exact-candidate physical-device evidence remains PENDING.
- Stable production HTTPS/WSS authority endpoint/cutover remains blocked.
- Production signing, signed AAB, Play Internal upload/approval remain unclaimed.
- WAVE RC14 canonical source permission/workspace binding remains unresolved.
- User-only legal/ownership/2FA/OAuth/billing/signing-key/device actions remain non-delegable.

## Integrity
- THF and WAVE remain isolated.
- No canonical source archive was mutated.
- No GPU/device QA, Play approval, signed production AAB, or production deployment is inferred or fabricated.

body_sha256=73d79aaafb8365e772650fcd0a35e6ed4559f4969945bffb1aa1545dcc8f1d2c
