# THF Games Factory Large-Batch Checkpoint — Gameplay Semantic Evidence V14

## Authority / deduplication
- Run-start repository head was `c7ce0c9d7fd0f6c759eee70ff69cff0b7e670998`; intervening head changes were Apps/TokenOps work, not game-candidate byte changes.
- Existing game Physical Device Evidence V13 was already proven PASS at run `34833956733`; it was preserved and not reimplemented.
- The authoritative release checkpoint at `945e7b8c251fd6a6348806b55150c78150a73660` records Terra/Rift/Spark/Rush/Learn Games/Fitness Games as unchanged and `NOT_FINAL / PHYSICAL_DEVICE_PENDING`.

## Material gap found
V13 verified semantic offline/local/online raw ADB payloads, but gameplay capability observations could still be SHA-bound files whose bytes did not prove the specific claimed capability. A real file plus SHA is not sufficient evidence that avatar load, locomotion, combat, learning progression or sensor-driven repetitions actually occurred.

## V14 implemented
- `7012945ca2834f70a42ea2d18d0231ee6fcd9f04` — validator: `ReleaseOps/mobile/validate_game_device_evidence_v14.py`.
- `67abc4809a9e1bc0ac20124a962b214e077a5693` — regression suite.
- `9fe62d965f5b21d66a2dacdb51cfd50eb4ac2c23` — permanent GitHub Actions gate.
- `dc7250626774e95909a1643cc00ad10ea8b40669` — corrected V13 test-module loader after the first CI run exposed a harness-only import typo.

V14 layers V13 and requires semantic markers inside the same SHA-bound manual-observation evidence bytes, tied to the same session and exact package. It requires positive touch event counts; safe-area/orientation truth; completed core journey and gameplay interaction; avatar load, movement and camera motion plus world interaction for Terra/Rift; real combat action plus combat state change for Rift; strictly increasing learning progress counters for Spark/Learn Games; positive sensor event counts plus strictly increasing repetition counters for Rush/Fitness Games. Terra/Rift additionally require `THF_SENSOR_LANDSCAPE=TRUE`.

## CI evidence
- Initial V14 run `34836802788` failed in the test harness because `exec_module()` received the ModuleSpec rather than the module. The validator was not weakened.
- The harness was corrected at `dc7250626774e95909a1643cc00ad10ea8b40669`.
- Final V14 run `34836872207`, job `103952572764`: SUCCESS.
- Compile V7-V14: PASS.
- Preserve V13 regression chain: PASS.
- V14 gameplay semantic regressions: PASS for all six products plus negative combat/learning/sensor/orientation cases.
- Non-promotional assertion: PASS; V14 cannot emit `FINAL_OR_PLAY_READY=TRUE`.

## Release truth / blockers
No game candidate is promoted. Physical Android evidence on the exact installed candidate remains non-substitutable: install/cold launch, touch, orientation/safe area, same-process background/resume, raw offline/local/online transitions, crash-free core gameplay, FPS/RAM/thermal, plus product-specific avatar/locomotion/world/combat/learning/sensor/repetition evidence. No physical phone was attached to this execution environment, so no device PASS was fabricated.

No production signing, Play publication, Cloudflare production cutover, Solana/token mutation, canonical archive overwrite, or WAVE mutation was performed.
