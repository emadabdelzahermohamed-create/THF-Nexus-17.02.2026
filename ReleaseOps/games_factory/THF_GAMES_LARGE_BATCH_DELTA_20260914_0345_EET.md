# THF Games Large-Batch Delta — 2026-09-14 03:45 EET

Status: ACTIVE / NOT_FINAL / PHYSICAL_DEVICE_PENDING

This delta follows `THF_GAMES_LARGE_BATCH_CHECKPOINT_20260914_0340_EET.md` and closes the Arena ownership proof that was deliberately left pending there.

## Canonical Arena contract inventory

Workflow: `THF Arena Action Contract Inventory V1`
Commit: `dcbe1904d6c977f2b87da2ac22ccda5c3027577e`
Run: `34793402611`
Result: SUCCESS
Artifact ZIP SHA-256: `37257926088953b0b0e8381604dd4de9d833be3c6446ee040dab7c37a6a70def`

Read-only source inspection on canonical runtime SHA-256 `6abec6481f40272f6a847e8da4ef6890243d55243e6d88d806cde6bfa97ac046` established:
- `/api/arena/start` is bearer-bound and passes the authenticated user id into `ArenaService.start`.
- `/api/arena/action` is bearer-bound and passes authenticated user id, `match_id`, and action into `ArenaService.action`.
- valid actions are `fire`, `reload`, `cover`, and `advance`.
- client-supplied damage/score is not accepted; outcomes are server-generated.
- no canonical source, WAVE file, external network, or production credential was modified/used.

## Exact same-action cross-user ownership proof

Workflow: `THF Arena Cross-User Ownership V1`
Commit: `2df24b870314b66a2d30b7fc9aa7b4c31b53171d`
Run: `34793464863`
Result: SUCCESS
Artifact: `THF-ARENA-CROSS-USER-OWNERSHIP-V1`
Artifact ZIP SHA-256: `f9a5ce76b9a3b1e0a0a093468d5f8030150f1ac03039fd71ccc8e59656505c81`

Eight of eight checks passed in a temporary isolated runtime/database:
- user A and user B independently registered and authenticated;
- A created an Arena match;
- the canonical `advance` action succeeded for owner A with HTTP 200;
- the identical `advance` action against the same `match_id` was rejected for authenticated user B with HTTP 400;
- after B's rejected attempt, A executed the same action again and the owner action counter increased by exactly one, proving B's rejected request did not mutate A's match state.

Truth boundary:
- `ARENA_CROSS_USER_OWNERSHIP=PASS`
- this is isolated backend authority evidence, not physical-device gameplay evidence;
- no production signing, Play approval, GPU/device QA, or production deployment is claimed;
- all registered APK candidates remain `PHYSICAL_DEVICE_PENDING`;
- `FINAL_OR_PLAY_READY=FALSE`.

WAVE remains isolated and unchanged; RC14 canonical-source OS Login access remains a separate blocker.
