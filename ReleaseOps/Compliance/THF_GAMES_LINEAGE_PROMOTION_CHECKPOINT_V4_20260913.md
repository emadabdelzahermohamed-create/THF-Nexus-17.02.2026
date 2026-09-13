# THF Games — Lineage Promotion Checkpoint V4 — 2026-09-13

## Purpose
This checkpoint supersedes only the `PROVENANCE_PENDING` status for the recovered Learn Games / Fitness Games outer archives recorded in the immediately preceding V3 checkpoint. It does not change any real-function or physical-device failure status.

## Evidence workflow
Workflow: `THF Learn Fitness Lineage Proof V1`
Run: `34768383614` — SUCCESS
Artifact: `THF-LEARN-FITNESS-LINEAGE-PROOF-V1`
Artifact ID: `10321475139`
Artifact ZIP digest: `5254834095893bdfb89f53ce21364f74e434f95d77a9658c126c4f882bd16469`

The workflow re-hashed the recovered outer archives and the prior P49 RC2 inner source archives, then inspected the existing builder evidence/result JSON in read-only mode. It emitted only SHA-like values and safe status fields; URLs, credentials and arbitrary payload values were suppressed. WAVE files were not read or changed.

## Learn Games lineage — PASS
The existing evidence file SHA-256 is `5140229e8147428e1b7a62fbb8390501f31702c3c4877bdd6fb70ecc9980477e`.

It explicitly records:
- `canonical_outer_sha256 = ce8547851c9573db02603ea6f11e020a1b7d346af0cac51e07947304f1a7c1f9`
- `canonical_inner_source_sha256 = dbd259b224924e60902fb0e1b2ebca77bc243e5f29a64d04fd3114438fd41484`
- debug APK SHA-256 `43d741bdd7c6dd558836ed5220a5b0a64fb41c2b2270931b34f37ed1a90772ae`
- test unsigned AAB SHA-256 `6ec569cd2a80f68b6c8c446344d0281428b56b5df68f7f02bcdfb8e0d1668bd5`
- application ID `com.thf.topherofit.learngames`

Therefore the recovered `source.zip` SHA `ce854785...a7c1f9` is proven to be the canonical outer candidate package whose recorded inner source is the P49 RC2 SHA `dbd259...d41484`.

Real-function status remains FAIL. Its current required failures are still:
`no_ui_only_shell`, `real_input_wiring`, `player_or_avatar_load`, `locomotion_or_gameplay_action`, `learning_loop`.

## Fitness Games lineage — PASS
The existing evidence file SHA-256 is `c57104c07ce501a458edc4705e8117b9cc138e6271040fbac9f3a10148759379`.

It explicitly records:
- `canonical_outer_sha256 = cf5d73c3a03ab503dbd7c36a2d4db3ec1449ec8281304627b9463e2cb8732a25`
- `canonical_inner_source_sha256 = da3c865a76848c170d679547e05d6edbc0b5ffd6a48002b12ad0d26415fd0273`
- debug APK SHA-256 `049a52833c40fdd2c2a0538e5b4416bb6e8fb1f71ddf15d4b7277b249a6719da`
- test unsigned AAB SHA-256 `a4455d93b5c8536695145fbb75d0054daf76bd44231de9991171af3529fbe7bd`
- application ID `com.thf.topherofit.fitnessgames`

Therefore the recovered `source.zip` SHA `cf5d73c3...32a25` is proven to be the canonical outer candidate package whose recorded inner source is the P49 RC2 SHA `da3c865...fd0273`.

Real-function status remains FAIL. Its current required failures are still:
`no_ui_only_shell`, `real_input_wiring`, `player_or_avatar_load`, `locomotion_or_gameplay_action`, `fitness_loop`.

## Authority interpretation
For subsequent engineering, use the proven outer source packages as the latest authoritative candidate containers, while retaining the recorded P49 RC2 inner-source SHA as provenance. This promotion is lineage-only. It does **not** allow reuse of any device, gameplay, package or release PASS from a different byte sequence.

## Release truth
- Learn Games: lineage PASS; API 36 marker PASS; real-function FAIL; device PENDING; NOT_FINAL.
- Fitness Games: lineage PASS; API 36 marker PASS; real-function FAIL; device PENDING; NOT_FINAL.
- Canonical archives remained unchanged.
- WAVE isolation preserved.
- No production signing, Play publishing, Cloudflare production cutover, token transaction or destructive cloud action occurred.

## Next
Engineer genuine local learning/fitness game loops on new reversible candidate bytes: real touch/input handling, player/avatar state, gameplay action, learning/mastery or exercise/rep loop as applicable, explicit offline truth, and backend-authoritative online/ranked/economy state. Re-run build/package/API36/security gates for every changed SHA, followed by exact-SHA physical-phone acceptance before any FINAL/PLAY_READY label.
