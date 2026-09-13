# THF Android Runtime Triad PASS + Physical Device Gate — 2026-09-13

Status: PACKAGING/RUNTIME-CONFIG PASS; PHYSICAL-DEVICE ACCEPTANCE PENDING
Scope: THF Core + Terra + Rift only. WAVE_MAWJA remains isolated.

## Verified latest runs

### THF Core RC6
- Workflow run: `34743356308` — PASS
- Artifact: `THF-Core-RC6-RUNTIME-CONFIGURED-STAGING`
- Canonical source SHA-256: `6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a`
- APK SHA-256: `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba`
- Package: `com.topherofit.thf.core`
- targetSdk: 36
- HTTPS service URL embedded: PASS
- Service health at build gate: PASS
- Endpoint class: Cloudflare Quick Tunnel staging
- Production signing: FALSE
- Production cutover: FALSE

### THF Terra RC34
- Workflow run: `34752636192` — PASS
- Artifact: `THF-Terra-RC34-RUNTIME-FIXED-APK`
- Artifact archive digest: `sha256:5b8d923366fd2ab4028f4acc1e42af4ab6a17a992183df898e026959eea43bda`
- Canonical source SHA-256: `eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68`
- APK SHA-256: `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7`
- Package: `com.topherofit.thf.terra`
- targetSdk: 36
- asset_count: 461
- project_binary_count: 1
- Godot project payload: PASS
- QA signing recovery: TRUE
- Production signing: FALSE
- Canonical archive mutated: FALSE

### THF Rift RC37
- Workflow run: `34752636187` — PASS
- Artifact: `THF-Rift-RC37-RUNTIME-FIXED-APK`
- Artifact archive digest: `sha256:0de948ba21fe96e275c2ec459d95820202e4ba11c5fcdf54c49a03214323f0dd`
- Canonical source SHA-256: `3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914`
- APK SHA-256: `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1`
- Package: `com.topherofit.thf.rift`
- targetSdk: 36
- asset_count: 450
- project_binary_count: 1
- Godot project payload: PASS
- QA signing recovery: TRUE
- Production signing: FALSE
- Canonical archive mutated: FALSE

## Regression closure

The two user-observed Android runtime failures are now blocked by CI gates:

1. Godot APKs cannot pass when project payload is absent. Terra and Rift both contain packaged Godot project data (`project.binary`) and passed the shared runtime packaging guard.
2. Service-native Android builds cannot pass the runtime-configured lane with an empty/insecure service URL. Core contains a verified HTTPS staging endpoint and passed service health verification.

Build success alone is not considered final acceptance.

## Next release gate

The highest-priority remaining gate for these three Android candidates is physical-device acceptance:

- install APK on a real Android device;
- launch from a cold start;
- verify no Godot `missing .pck/project data` engine failure;
- verify Terra and Rift reach their actual first interactive scene;
- verify touch/input rendering and first-frame stability;
- verify Core reaches the service-backed application flow without `service not configured`;
- capture package/version/runtime evidence and any crash/logcat evidence;
- only after device PASS may these candidates advance toward final release signing/AAB release gates.

This gate is intentionally not faked by desktop/headless CI.

## WAVE isolation/recovery recheck

A fresh Library search for the RC13/RC14 canonical WAVE workspace/source still did not locate the full source archive. `WAVE_CURRENT_STATE_RC14.json` remains the newest state record and identifies the real `/root/workspace/wave-mawja` runtime plus RC13 bundle as required for the RC14 live gate. Therefore `WAVE-LIVE-SOURCE-MISSING` remains an independent blocker; RC9 is not substituted.

No WAVE bytes were copied into THF build paths and no THF bytes were copied into WAVE paths.

## Open PR / financial safety

PR #2 remains open and draft for isolated TokenOps read-only work. No Solana transaction, signing, burn, transfer, authority mutation, treasury migration, or other financial action was performed.

## Safety boundary

No persistent cloud key used; WIF/IAP remains the cloud access path. No production signing, Google Play publication, Cloudflare production cutover, destructive cloud action, canonical source overwrite/delete, or cross-project mutation was performed.
