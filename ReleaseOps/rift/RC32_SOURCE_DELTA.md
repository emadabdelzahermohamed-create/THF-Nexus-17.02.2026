# Rift RC32 source delta

- `app/services/arena.py`: generalized authoritative actor down cleanup; player cover/vault/revive `action_state`, cover metadata, aiming and lean are cleared when server damage downs the actor; RC31 bot semantics are preserved.
- `android-arena/app/build.gradle`: `versionCode 42066`, `versionName 4.6.6-rc32`, compile/target SDK 36 preserved.
- `config/animations.json`: RC32 human-down cleanup contract metadata.
- `native/arena/RiftAudioFeedback.gd`: gameplay-neutral Godot 4.7.2 type fix only. SHA `40804b4461820e78b63ca606dfc8cce1ad799f27eba61c94c3ed37f60de9f23d` -> `a0de254feafce5d7bda6f26321915f30727057e1350ba1bba2356207840eee3a`.
- `scripts/rift_rc32_human_down_tactical_cleanup_gate.py`: RC32-only targeted validation.

Godot 4.7.2 parser/import/headless: PASS in isolated ReleaseOps/GCP run `34651723807`. Initial workflow YAML failure was corrected before this successful run.

Artifact SHA-256: `f3d32333034ce15a9473a7e177b09eb7684d25fa374d845b2b01389325714e8d`.

Next verified source gap: human `revive_teammate` currently enumerates only `s['players'].values()`, so human-to-downed-bot revive parity is absent even though bot revive considers players+bots.
