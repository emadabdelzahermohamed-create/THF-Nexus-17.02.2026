# THF Games Large-Batch Checkpoint — 2026-09-14 03:40 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING
Scope: Terra/Nexus World, Rift/Nexus Arena, Spark, Rush, Learn Games, Fitness Games and shared authenticated backend authority.

## Starting authoritative state

The preceding game checkpoint is `ReleaseOps/games_factory/THF_GAMES_LARGE_BATCH_CHECKPOINT_20260914_0320_EET.md`.

Exact physical-device APK candidates remain byte-for-byte unchanged:
- Terra `8539af9a7d531f80b14c1b2e4366ac2dda666d042ae8520b4fa1ea299d2d2165`
- Rift `3577175821a91d4d76da77d9fc982575704a85e20162e4b66afe37565f63b5fb`
- Spark `9fffc4d97e64faf1d92ec6900968902570e2739d6751d752377ebde2589165ea`
- Rush `3e9aabaebdf1b321430abb3286156aeeaf8cf0174f2abff593a3ee3dc50d0e3a`
- Learn Games `e0667eef4c03aaf78ff8f14c74873fae5ad5c5a3a6f4a28f7c36a73505eb4727`
- Fitness Games `7404d3ff644253109e36d4fad25edb6cb3313ad8676e3aa7e87c42ab7088832a`

Physical-device evidence tooling V3 remains the governing hardware gate. No device evidence was fabricated or promoted in this batch.

## Auth contract inventory

Added `.github/workflows/thf-game-backend-auth-contract-inventory-v1.yml`.

Commit: `dba90e8ab4046d06e0d822b0e36256951e690d1b`
Run: `34793087533`
Result: SUCCESS
Artifact: `THF-GAME-BACKEND-AUTH-CONTRACT-INVENTORY-V1`
Artifact ZIP SHA-256: `3747c4c319f97953fd87aa54f41267d71ee6878c6efd31900a63d58549018ecd`

The read-only isolated inventory proved:
- WIF/OIDC -> GCP -> IAP builder path remains operational.
- Canonical THF runtime Python source SHA-256 is `6abec6481f40272f6a847e8da4ef6890243d55243e6d88d806cde6bfa97ac046` before and after the inspection.
- 35 relevant API paths were discovered, including register/login, economy, world, social, avatar and arena routes.
- Auth helpers include bearer-token extraction and user resolution.
- No external network, production credential, WAVE read/write, or canonical-source mutation occurred.

## First authenticated authority probe and diagnostic correction

Added `.github/workflows/thf-game-backend-authenticated-authority-v1.yml`.

Commit: `8bc6e2004caae974f9812cbfecc1d0c10ab170dd`
Run: `34793192214`
Result: FAIL-CLOSED
Artifact ZIP SHA-256: `28b9a4e8ccd485fee36c93bfd02aadbfd390d90427b05758905f0b2ee92961b1`

The run passed 11 of 12 checks. The sole failure was `avatar/generate` returning HTTP 400 for an intentionally minimal payload with a valid identity. The same authority surface rejects invalid identity at the auth layer. Therefore treating HTTP 400 as an authentication failure conflated payload validation with authority and was a harness defect.

The run also showed a second evidence-quality problem: a non-2xx Arena action by user B cannot prove cross-user ownership rejection unless the identical action is first demonstrated valid for owner A. The evidence was not promoted to ownership PASS.

## Corrected authenticated role-authority gate

Added `.github/workflows/thf-game-backend-authenticated-role-authority-v2.yml`.

Commit: `a6c0dc94106a556813fa3832d724cd8f4e4f2e75`
Run: `34793302980`
Result: SUCCESS
Artifact: `THF-GAME-BACKEND-AUTHENTICATED-ROLE-AUTHORITY-V2`
Artifact ZIP SHA-256: `b488a5d821fff4b2003ba989505122a864b4771672f250c16e33acb3640ecceb`

All 11 role/authentication checks passed in an isolated temporary runtime/database with external networking disabled:
- two ephemeral users register and login;
- authenticated economy balance succeeds;
- invalid bearer token is rejected with 403;
- ordinary authenticated user is rejected from world-environment admin mutation with 403;
- ordinary authenticated user is rejected from internal economy award with 403;
- avatar route distinguishes valid identity from invalid identity and reaches payload validation; this is explicitly NOT an avatar functional PASS;
- social-position actor identity remains bearer-bound despite another user's `user_id` being injected in the body;
- authenticated arena start succeeds.

Truth boundary:
- `AUTHENTICATED_ROLE_AUTHORITY=PASS`
- `ARENA_OWNERSHIP_PROOF=PENDING_STRONG_SAME_ACTION_CONTROL`
- `FINAL_OR_PLAY_READY=FALSE`

## Program-wide preserved blockers

- Exact-candidate physical-device acceptance remains PENDING for every app/game.
- Production signing, signed AAB and Play Internal approval remain NOT PROVEN.
- Stable production HTTPS/WSS cutover remains NOT PROVEN; Quick Tunnel evidence is staging only.
- WAVE RC14 remains isolated and blocked by CI OS Login access to canonical `/root/workspace/wave-mawja`; WIF/GCP/IAP are operational. Do not weaken OS Login/SSH and do not substitute older WAVE sources.
- THF Pass stable externally reachable trusted-TLS staging remains unproven.
- Notification provider delivery and physical notification receive/tap/background-resume evidence remain unproven.
- User-only signing keys, legal acceptance, ownership/console actions, 2FA/OAuth/billing and real physical-device actions remain non-delegable.

## Next safe autonomous block

Derive a valid deterministic Arena action contract in an isolated temporary runtime, prove the identical owner action succeeds, then prove a second authenticated user cannot mutate that exact owner session. Keep ownership PENDING until that same-action control exists. Continue Play/compliance and exact-hash evidence work without changing candidate bytes.
