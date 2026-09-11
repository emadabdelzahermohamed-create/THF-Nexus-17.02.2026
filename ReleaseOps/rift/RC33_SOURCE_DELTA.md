# THF Rift RC33 source delta

Baseline: RC32 `4.6.6-rc32` artifact SHA `f3d32333034ce15a9473a7e177b09eb7684d25fa374d845b2b01389325714e8d`.

Changed source:
- `app/services/arena.py`: human `revive_teammate` candidate search now uses authoritative players+bots; tactical revive resolution now resolves target IDs across authoritative players+bots. Existing server-owned 110-unit range, LOS validation and 1800ms action window preserved.
- `android-arena/app/build.gradle`: versionCode 42067 / versionName 4.6.7-rc33; compileSdk/targetSdk 36 preserved.
- `config/animations.json`: records RC33 server-owned human↔bot revive parity contract.
- `scripts/rift_rc33_human_bot_revive_parity_gate.py`: RC33-only deterministic behavior/source gate.

Source SHA:
- `app/services/arena.py`: `f41ca92e51f96d5f5016991d680ecf600703b168ae31953c2f9156e05aec5751`
- `native/arena/RiftAudioFeedback.gd`: `a0de254feafce5d7bda6f26321915f30727057e1350ba1bba2356207840eee3a` (byte-identical to RC32)

Artifact SHA: `cd2ae24b9adffe27873acbee42e1380c50665dfbc9d21a6a560fc665ed1b961d`.

Next verified gap: human revive lacks bot-style server threat-aware cancellation during the active revive window.
