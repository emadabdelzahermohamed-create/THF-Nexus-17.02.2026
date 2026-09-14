# THF + WAVE Large-Batch Checkpoint — 2026-09-14 06:32 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING

## Material repair completed
Spark and Rush release authority is now reconciled to one exact APK candidate per Android package across the apps and games registries.

Active exact candidates:
- Spark / `com.topherofit.thf.spark`
  - source: `APPS_RC4+REAL_GAME_OVERLAY_V1`
  - source SHA-256: `58a32690ea69b6fd62a977145079e0ad6e75061724a786d5db9276b95ec48d43`
  - APK SHA-256: `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush / `com.topherofit.thf.rush`
  - source: `APPS_RC4+REAL_GAME_OVERLAY_V1`
  - source SHA-256: `766936c25700643bcf813d4e754b287f79810eebe859bd45388391bf57bf771c`
  - APK SHA-256: `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`

The prior apps-stream APKs were retained as `superseded_candidates` for audit and are not valid physical-device authority:
- Spark old APK: `92bc7f913d560a185044af2df7b1955d3a0b29eca920034edf3cd9741bce0c23`
- Rush old APK: `304164035cc4b82d23e2b2e6bf48abca3c466c46f5668a203cf0b4cfca223e99`

Registry reconciliation commit:
- `f045dfe01f0094732994771b00b5601b5de2213e`

## Gate repair and rerun
The first post-reconciliation Cross-Stream Candidate Consistency run correctly exposed a stale regression test that still asserted the former Spark/Rush conflict must exist. The test was updated only after the registries contained one identical exact APK SHA per overlapping package; the validator itself was not weakened.

Test repair commit:
- `88943103b3f0fdf3eec313a47910eab3bf03c9fa`

Final run:
- workflow: `THF Cross-Stream Candidate Consistency V1`
- run: `34802926550`
- result: `SUCCESS`
- regression tests: PASS
- authoritative registry evaluation: PASS
- artifact upload: PASS
- artifact: `THF-CROSS-STREAM-CANDIDATE-CONSISTENCY-V1`
- artifact ID: `10332380459`
- artifact digest: `sha256:42e897f4d4b261fd3419ac789eb421a83e6b39c346ade9c2dc84443b725ad28f`
- artifact expires: `2026-12-13T03:32:02Z`

## Preserved release truth
This reconciliation does not promote either app to FINAL or PLAY_READY. Exact-candidate physical-device evidence remains mandatory, including install, launch, touch, responsive layout/orientation, background/resume, offline/network transitions, core journey and crash-free smoke. Game candidates additionally require real gameplay/device observations including FPS/RAM/thermal, and Rush requires real sensor-motion/repetition evidence.

The current six-game authoritative-source lock remains PASS and their exact APK bytes remain unchanged. Production signing/signed AAB, Play Internal acceptance, stable trusted production HTTPS/WSS, Cloudflare production cutover, and physical-device acceptance are still unproven.

WAVE remains isolated. RC14 remains blocked on CI OS Login access to canonical `/root/workspace/wave-mawja`; no older WAVE source was substituted and SSH/OS Login was not weakened.

Evidence body SHA-256: `627d78b9313aecdfcbaf74f316aa94d21557ea6683d8b7d0f73e0f2b1c4776b2`
