# Terra RC34 WIF retry

Purpose: retrigger the Terra RC34 Godot/Android gate from a short WIF-safe branch without modifying Terra product source.

Source commit: 412ff973188a9078cb3481991c2c54c99f355e45
Source checkpoint: TERRA-RC34
Canonical SHA-256: eaa2ae79b4f85781903e7c7909910758344422209baa650cf7cf9fd397bdbd68
Drive staging: exact split parts uploaded and read-only access granted to thf-release-builder service account after first 404 evidence.
Isolation: THF Terra only; WAVE_MAWJA untouched.
Safety: unsigned/test gate only; no production signing, store publish, Cloudflare production cutover, Solana action, secret material, or destructive cloud mutation.
