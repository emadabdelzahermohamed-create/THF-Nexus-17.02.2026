# THF Apps Factory final checkpoint — 2026-09-14 02:09 EET

`FINAL_OR_PLAY_READY=FALSE`

This checkpoint supersedes the 02:07 EET Apps Factory note for this engineering block. Scope remains Core, Pulse, Forge, Echo, Codex, Spark, Rush, Vault UX, Signal, Command and THF Pass/shared federation/handoffs. Native game streams, token finance and WAVE were not mutated.

## Completed blocks

### 1. Same-SHA preservation
No proven Core or nine-app exact-candidate package gate was redundantly rebuilt. API 36/package identities and previously bound APK SHAs remain unchanged; physical-device acceptance remains PENDING.

### 2. THF Pass exact candidate over isolated HTTPS
Workflow `THF Pass Private HTTPS Staging V1`, run `34788521954`: SUCCESS.

Artifact ID `10327258382`, ZIP SHA-256 `01ab9c42a70b0a3975369b5debe7d628a3ade2cc6ff73863b978310256719a0b`.

Baseline hashes before/after remained identical:
- app.py `471a8e0c6b67320386db6efcd32a3718265a645a30af3d7a9ea95060258058be`
- identity/service.py `8421a63db2e05bbd3b10b60da3edb0a3190ad7c2ea0498f4a1a704c3f7827b9f`

Exact disposable candidate:
- app.py `7f839cdba4307c5cd9a9aa258c4a3cdbf8bb55308f84ddda2b0217582ecc1ab2`
- identity/service.py `36c9a173d394a9c2d19c931dbf8e89ab5478c27b197b278ce76b9b9b8286443c`

HTTPS loopback proof: health, register/login, refresh rotation, expired-refresh rejection, logout revocation, revoke-all, audience-bound one-time handoff, wrong-audience rejection, replay rejection and existing security regressions all PASS. Temporary DB and ephemeral test certificate only. `PUBLIC_ENDPOINT_CHANGED=FALSE`, `DEPLOYMENT_PERFORMED=FALSE`, rollback PASS.

### 3. Spark/Rush exact-source test debt materially reduced
Exact source inventory run `34788546294`: SUCCESS; authoritative archives themselves contain no embedded source tests.

External exact-source real regressions run `34788612192`: SUCCESS for both apps.
- Spark RC3 source SHA `dc312dc65e681e914c3421a20362cd0fba0c1e692a7becdb66d7d17a0b6299a0`: 6 tests PASS. Artifact `10326439802`, digest `8fef5838d9bc2335153a6c6de752597e2def3570e59d486b2322d978b4a12796`.
- Rush RC3 source SHA `bd7e365ded07fd569020fff1c699d74322fd5c767b16ac6336f2bc99f8b5958b`: 6 tests PASS. Artifact `10326564676`, digest `078a786ac677b5d11415e549a1a8e1f49e0e5beb9abd4200e7f896a78edc4ce7`.

The tests execute against clean exact-SHA archive extraction and explicitly reject `NO-SOURCE` as a false PASS. They cover health/catalog behavior, deterministic Spark level generation, fail-closed unauthenticated mutations, Rush anti-cheat policy/truthfulness, no-pay-to-win policy and leaderboard read behavior.

### 4. Regression evidence is now fail-closed and persistent
Registry: `ReleaseOps/apps_factory/THF_EXTERNAL_EXACT_SOURCE_TESTS_20260914.json`.
Validator and negative regression tests enforce exact source SHA/package binding, immutable source-archive truth, minimum real executed-test count, artifact digest integrity and prohibition of FINAL/device claims.

Gate `THF External Exact Source Tests Gate V1`, run `34788748525`: SUCCESS, including validator and five fail-closed regression tests.

## Checkpoint commits
- `a4f717258aa596cf09ce3fbf7694f6ffe67f8d3e` — isolated HTTPS Pass rehearsal.
- `150fff5e6c7e5c01210366935d008b1b5b64122d` — Spark/Rush exact-source test-surface inventory.
- `3c18f9e628429c58a79d9e1f66df3f459fc850f8` — Spark real regression pack.
- `8d7fc3f8b6d291a7d0ea54537e2a140199edf886` — Rush real regression pack.
- `c39137ad3c1a74b15e687617e3d1eaed780c8093` — real exact-source execution workflow.
- `c04bfaec21a16c69032cecf6a948ea7dd8cea79b` — evidence registry.
- `cccfc6b16dd782d81bf5b550a40d0d1facfd6530` — registry validator.
- `0da054e8dd2cbcd376ca11b55f1c5f3aa1dcbfc9` — validator regression tests.
- `01d733f1556c06eb670fcfb5ba37086b7cf4dbfa` — registry CI gate.

## Remaining truthful blockers
- Stable externally reachable non-public HTTPS THF Pass staging with trusted TLS is not yet proven; loopback HTTPS proof must not be represented as externally reachable service evidence.
- App-specific push/provider implementation remains absent from the nine authoritative source archives; `PUSH_READY=FALSE`.
- Physical-phone exact-APK acceptance remains required for install/launch/touch/layout/orientation/background-resume/offline-network/Data Saver/accessibility/RTL/core journey/crash-free evidence.
- Production signing, signed AAB, Play Internal acceptance and owner/legal/OAuth/2FA actions remain unperformed.

## Next executable block
Preserve all exact candidate identities; advance provider-neutral notification registration/token lifecycle implementation and tests without claiming provider delivery, prepare a stable isolated HTTPS Pass staging target with rollback and trusted endpoint evidence without touching the public endpoint, and continue device-evidence preparation while keeping all release promotion fail-closed.
