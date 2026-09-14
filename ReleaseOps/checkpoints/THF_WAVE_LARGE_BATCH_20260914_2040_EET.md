# THF + WAVE LARGE-BATCH Release/Platform/QA Checkpoint — 2026-09-14 20:40 EET

Overall status: NOT_FINAL / NO_GO.

## THF Rift authority and AAB tooling
- Latest authoritative Rift source is RC41 / 4.7.5-rc41 / versionCode 42075 / targetSdk 36.
- Canonical RC41 source SHA-256: 29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d.
- Production package identity: com.topherofit.thf.rift.
- Existing RC37 AAB tooling was repaired: the import-sidecar validator now fails only for actual Android base/res leakage and requires Android API 36 and expected package metadata.
- RC37 QA AAB run 34875721129 completed SUCCESS and produced AAB SHA-256 a9ddd489d49b45c78f48d71836b0b3ac072cfd16fb99518af98e41ca018e9522, raw size 144523066 bytes.
- That RC37 AAB is historical QA evidence only: package com.topherofit.thf.rift.phoneqa, production signing false, physical-device evidence pending, final/play-ready false, and it is superseded by RC41 authority.
- Play size evidence was corrected: raw AAB file size is advisory only; Play-size acceptance remains UNVERIFIED_REQUIRES_PLAY_OR_BUNDLETOOL.
- Exact RC41 builder discovery run 34876093324 completed SUCCESS. Exact RC41 bytes are MISSING on the private GCP builder. Next executable release gate is STAGE_EXACT_RC41_BYTES, then fresh Godot 4.7.2 parser/import/headless plus Android API36 AAB export.

## THF platform/toolchain
- GitHub WIF -> GCP -> IAP -> private builder path is operational.
- Android API 36 is hard-required in the Rift AAB helper.
- Godot 4.7.2 export path is operational for the staged historical RC37 source.
- Terra RC34 V4 has an independent fail-closed installability gate for exact QA APK identity; physical-device install remains required and final/play-ready remains false.
- GitHub main branch is currently unprotected and required status-check enforcement is off. Repository owner/admin action is required to enable protection/rulesets; no administrative bypass was attempted.

## Mobile Real-Function Release Policy
- No app/game is promoted to FINAL from build/static/source evidence alone.
- Exact-candidate physical-device evidence remains mandatory for install, launch, touch, layout/orientation, background/resume, offline/network transitions, core journey, and crash-free smoke.
- Games additionally require player/avatar load, movement/camera/gameplay interaction, FPS/RAM/thermal observation.
- No GPU/device QA, production-signed AAB, Play approval, production deployment, or Cloudflare production cutover is claimed.

## WAVE isolation
- WAVE source/runtime was not modified.
- WAVE RC14 remains guarded to canonical /root/workspace/wave-mawja.
- Outstanding WAVE external/non-delegable gates remain canonical runtime access, MEDIA_API_URL/MEDIA_API_TOKEN + VPS/FFmpeg, Cloudflare authorization, production signing/Play Console, and physical Android smoke.
- No older WAVE source was substituted and no SSH/OS Login protections were weakened.

## Next safe release work
1. Stage exact Rift RC41 source bytes matching SHA-256 29edaa0eb594a25d0960cb176765663f9bab3d91a60fd98016474ff5695cb95d to the private builder.
2. Run fresh Godot 4.7.2 parser/import/headless and API36 AAB export against RC41 with production package identity preserved and signing disabled until owner-controlled signing is available.
3. Measure Play delivery size with bundletool/Play rather than raw AAB bytes.
4. Continue fail-closed exact-candidate device-evidence collection; do not promote any QA package or historical source.
5. Preserve THF/WAVE isolation and require owner/admin actions only for branch protection, signing, legal/Play acceptance, OAuth/2FA/billing, and physical-device operations.

Checkpoint body SHA-256: 731fcb65b887f6c3f77af600966f37a5b2d149a3d72e90cfcaba248e9cefbf4b
