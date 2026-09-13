# THF Release Factory Large-Batch Checkpoint — 2026-09-13 16:41Z

Status: NO PUBLIC ROLLOUT / fail-closed.

## Authoritative candidates retained
- Core RC6 APK SHA-256: 262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba
- Terra RC34 source SHA-256: eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68
- Terra RC34 APK SHA-256: 388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7
- Rift RC37 source SHA-256: 3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914
- Rift RC37 APK SHA-256: fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1
- Spark source SHA-256: 6b74f8d75df8c0b7f74d8c2fee8be7e3517f3803cb42968735bc7a10939bc18c
- Rush source SHA-256: bb6ff035186b13cdde853145f42e66259c205889de2a7b368da34c9cb0582ba7

## Safe reversible repairs in this pass
- aadc26b16781a85cb3cc91e0a63d312f6f75fc96 — retain Spark/Rush remote failure evidence while remaining fail-closed.
- dbcc8cec77a8d78677366e2709a3e1f4a94c702c — scope placeholder endpoint audit to runtime/config files.
- e9d64709fbbcf434953100e57ac92aa2e198de70 — first disposable Spark/Rush package-id preservation repair.
- 23bd00f0694969cb00e54dd2cdd11b96c5d164fc — report exact placeholder endpoint files.
- 035f85f01bcee200a98d850e80cf8f1fef36e6b8 — force canonical Spark/Rush applicationId only in disposable QA candidates.

## Material gate results
- Terra/Rift staging network authority run 34769077363: PASS.
  - WIF/GCP authentication: PASS.
  - exact Terra/Rift source binding: PASS.
  - network/mobile overlays: candidate-only; canonical archives unchanged.
  - protected unauthenticated arena action: fail-closed as required.
  - targetSdk 36/mobile source contract: PASS.
  - artifact id: 10322215266 (`THF-TERRA-RIFT-STAGING-NETWORK-AUTHORITY-V1`).
  - physical-device status remains PENDING; final status remains NOT_FINAL.
- Spark/Rush candidate run 34768745642 proved Spark Gradle build succeeds and targetSdk=36, but correctly failed because APK package was `com.topherofit.thf.spark.debug` rather than canonical `com.topherofit.thf.spark`.
  - server artifact digest: sha256:4d12e9328d1b09066f996bf5eeb7e168777303101223f4e7dc5d84819e8b585d
  - downloaded evidence ZIP SHA-256: c56824d2a14dff59af54bb28437e4dd38c1f2a625985d09ac6142ae29b96db07
- Diagnostic evidence ZIP SHA-256: 1eb24acdb540752843a2e789c51eb6de46c854e58ab40e35f8d0882bd9c14dc7
- Spark/Rush run 34769052978 after first package repair still failed correctly; overlay changed zero package-suffix files and package remained `.debug`.
  - uploaded artifact digest: sha256:3e978234342a846b7b13fa8cbeed307907a7dfd9a47ef95dde5b52452722d61f
- Spark/Rush run 34769249423 for commit 035f85f... is currently executing the disposable build/inspection step. No PASS is claimed until its truth gate completes.

## Unresolved hard blockers
- Exact-candidate physical-device evidence is absent for Core/Terra/Rift and remains mandatory for final release.
- Stable production HTTPS/WSS authority endpoint/cutover remains separate from quick/staging tunnel validation.
- Production signing, signed AAB, Play Internal upload/approval are not claimed.
- WAVE RC14 remains blocked at canonical source access: OS Login maps CI to the service-account OS user which cannot read `/root/workspace/wave-mawja`. Safe resolution is narrowly scoped OS Admin Login or, preferably, a service-account-owned release workspace cryptographically bound to the root canonical checkout. No OS Login weakening or broad Owner grant was performed.
- Legal acceptance/ownership, production signing keys, 2FA/OAuth/billing, Play declarations requiring owner/legal input, and physical-device actions remain non-delegable.

## Isolation and truth constraints
- THF and WAVE remain isolated.
- No canonical source archive was mutated by the disposable candidate overlays.
- No GPU/device QA, signed AAB, Play approval, or production deployment is fabricated or inferred.

checkpoint_body_sha256=3a1edb6d0fa4aa9417080d6435fbad9b49ebd7d1c1979fc410268a33543cbd48
