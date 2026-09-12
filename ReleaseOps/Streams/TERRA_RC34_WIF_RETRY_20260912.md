# Terra RC34 WIF retry

Purpose: retrigger the existing Terra RC34 Godot/Android gate from a short WIF-safe branch without modifying Terra product source.

Source commit: 412ff973188a9078cb3481991c2c54c99f355e45
Source checkpoint: TERRA-RC34
Isolation: THF Terra only; WAVE_MAWJA untouched.
Safety: unsigned/test gate only; no production signing, store publish, Cloudflare production cutover, Solana action, secret material, or destructive cloud mutation.
