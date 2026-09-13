# THF Android Artifact Integrity Checkpoint — 2026-09-13

Status: VERIFIED ARTIFACT SNAPSHOT
Scope: THF Core RC6, Terra RC34, Rift RC37 only. WAVE_MAWJA remains isolated and is not represented by these artifacts.

## Verified GitHub Actions artifacts

| App | Workflow run | Artifact ID | Artifact name | Artifact ZIP SHA-256 | Candidate APK SHA-256 | Canonical source SHA-256 | targetSdk | Runtime gate |
|---|---:|---:|---|---|---|---|---:|---|
| Core RC6 | 34743356308 | 10312629324 | THF-Core-RC6-RUNTIME-CONFIGURED-STAGING | ecb52d75fbc99960937f4e00ad2019ba3dbdc723296a76278ff0a7ebdcb916d9 | 262e1ee0dc4436f60de1f871c1a9a8fb633058ef87d8d4ab46d282a6fb3236ba | 6dab85e19f17e9d9c712cc1e588759bf826aa2ddd291fa361bbadaee014a045a | 36 | PASS — HTTPS staging endpoint embedded + health PASS |
| Terra RC34 | 34752636192 | 10315967515 | THF-Terra-RC34-RUNTIME-FIXED-APK | 5b8d923366fd2ab4028f4acc1e42af4ab6a17a992183df898e026959eea43bda | 388f3c09bd8e0d64ebb5ad5e9c10b92d3b17f05851949936a07fb5b3db5b18c7 | eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68 | 36 | PASS — Godot project.binary present, assets=461 |
| Rift RC37 | 34752636187 | 10315992361 | THF-Rift-RC37-RUNTIME-FIXED-APK | 0de948ba21fe96e275c2ec459d95820202e4ba11c5fcdf54c49a03214323f0dd | fe35328b6ec4ed98a4c26cd5067e8056310fd773d9a3e7c3212943249eb024b1 | 3e2407d4aa76d4d23f4f0a0c3ccb02f02f1a9522b42518a38c03e0f01775e914 | 36 | PASS — Godot project.binary present, assets=450 |

## Direct artifact verification performed

The current GitHub Actions ZIP artifacts were downloaded without modifying the canonical source archives. Their ZIP SHA-256 values match GitHub's artifact digests. Each ZIP was unpacked into a disposable local directory and the candidate APK SHA-256 was recalculated.

Core `TRUTH.txt` confirms `service_url_embedded=true`, `service_url_scheme=https`, `service_health=PASS`, `production_signing=false`, `production_cutover=false`, `canonical_archive_mutated=false`, and `wave_untouched=true`.

Terra and Rift `TRUTH.txt` confirm `godot_payload=PASS`, `project_binary_count=1`, expected package names, target SDK 36, QA-only signing recovery, `production_signing=false`, `canonical_archive_mutated=false`, and `wave_untouched=true`.

## Artifact retention

At verification time all three GitHub artifacts were unexpired. GitHub reports current expiry dates of 2026-09-27 for these QA artifacts. They are evidence/candidates only, not production releases.

## Release truth

- CI/package/runtime-payload gates: PASS for Core, Terra and Rift.
- Physical-device install/cold-launch/interactive acceptance: PENDING.
- Production signing: NOT PERFORMED.
- Google Play irreversible publication: NOT PERFORMED.
- Cloudflare production cutover: NOT PERFORMED.
- Solana/token financial action: NOT PERFORMED.
- Canonical source overwrite/delete: NOT PERFORMED.
- WAVE/THF mixing: NOT PERFORMED.

## Next safe step

Use the exact APK SHA-256 values above for physical-device acceptance. Do not accept screenshots from a differently hashed APK as evidence for this checkpoint. If a device test fails, capture package/version, cold-launch behavior, Android version/device model, and relevant runtime error before rebuilding. In parallel, continue reversible Play/compliance preparation and WAVE source recovery, while keeping production-only gates closed.
