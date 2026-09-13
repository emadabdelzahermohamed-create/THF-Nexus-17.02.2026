# Unified Android QA Matrix — 2026-09-13

Status: ACTIVE EVIDENCE MATRIX
Scope: THF Core / Terra / Rift plus isolated WAVE_MAWJA lane.

| App | Canonical checkpoint | Package | Version evidence | targetSdk | Runtime/package gate | Candidate APK SHA-256 | Physical device | Play Internal | Primary blocker |
|---|---|---|---|---:|---|---|---|---|---|
| THF Core | RC6 | `com.topherofit.thf.core` | `6.2.2-rc6`, versionCode `62200` from prior package gate | 36 | PASS — HTTPS staging endpoint embedded + service health PASS, run `34743356308` | `262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba` | PENDING | NOT UPLOADED | Real-device acceptance; stable production hostname before final AAB |
| THF Terra | RC34 | `com.topherofit.thf.terra` | RC34 canonical stream; package gate current | 36 | PASS — Godot payload/project.binary, assets=461, signature/alignment/package/API gate PASS, run `34752636192` | `388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7` | PENDING | NOT UPLOADED | Real-device interactive scene/input/GPU acceptance |
| THF Rift | RC37 | `com.topherofit.thf.rift` | `4.7.1-rc37`, versionCode `42071` from package evidence | 36 | PASS — Godot payload/project.binary, assets=450, signature/alignment/package/API gate PASS, run `34752636187` | `fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1` | PENDING | NOT UPLOADED | Real-device interactive scene/input/GPU acceptance |
| WAVE_MAWJA | RC14 live-gate wrapper over RC13 verification contract | UNKNOWN until exact canonical runtime is recovered; do not infer from older RC9 | RC14 state record only | UNKNOWN-current | BLOCKED — full canonical `/root/workspace/wave-mawja` runtime/source not recoverable on WIF builder or current Library search | N/A-current | PENDING | NOT UPLOADED | `WAVE-LIVE-SOURCE-MISSING`; recover exact RC13/RC14 workspace and verify SHA before any build |

## Evidence rules

- SHA-256 is verified before build/export and canonical archives are never overwritten.
- Godot apps require project payload, package identity, API 36, signature, zipalign, and runtime packaging gates before candidate acceptance.
- Service-native apps require a non-placeholder HTTPS runtime endpoint plus health verification; temporary Quick Tunnel values are staging evidence only and are not final production configuration.
- CI PASS is not equivalent to physical-device PASS.
- Production signing, Play upload, Cloudflare production cutover, Solana financial actions, and destructive cloud changes remain outside this matrix unless separately authorized.
- WAVE and THF build paths remain mutually isolated.

## Next safe sequence

1. Physical-device install/cold-launch/runtime acceptance for Core, Terra and Rift.
2. Capture device evidence and update this matrix with PASS/FAIL and exact observed version/package.
3. Continue reversible Play/compliance preparation while production hostname, signing and publication remain blocked by their explicit gates.
4. Resume WAVE immediately if the exact RC13/RC14 canonical workspace/source becomes recoverable; verify identity and SHA before staging.
