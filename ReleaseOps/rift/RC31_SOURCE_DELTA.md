# Rift RC31 source delta

Authoritative baseline: RC30 artifact SHA `1651ff94d42e63c2c1daa1e6d08820d706460bacba7f09c8e77f84a62b11bd41`.

Changed Rift files only:
- `app/services/arena.py`: adds server-owned immediate hostile detection for bot revive, down-state tactical cleanup for bots, pre-start revive defer and in-flight revive cancellation. Player/bot authoritative downing paths call the bot cleanup helper only when the downed actor is a bot.
- `android-arena/app/build.gradle`: versionCode 42065, versionName 4.6.5-rc31, API 36 preserved.
- `config/animations.json`: records RC31 server-owned tactical interruption policy.
- `scripts/rift_rc31_bot_tactical_interruption_gate.py`: new RC31-only 69-check deterministic gate.

Native/Godot source is unchanged from RC30: 34/34 native files byte-identical. This is not a substitute for Godot parser/import/headless evidence; Godot 4.7.2 executable was unavailable in the current runtime.

Cumulative artifact SHA: `0c87563b469d61f63330504f231b99c90db7f4832c2b08f12bd801440bb21253`.
Local source patch SHA: `ff8a7d37268cc598aeaea5f66515c8f1ed70c441ff2a02b50124a95ecd6fdce0`.

Next verified source gap: human/player actors can still be downed while an authoritative cover/vault/revive action is active without explicit down-state tactical-action cleanup. Keep hit/damage/ranked ownership server-side when closing it.
